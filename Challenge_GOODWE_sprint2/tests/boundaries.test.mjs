import test from 'node:test';
import assert from 'node:assert/strict';
import { setImmediate } from 'node:timers/promises';
import { openDatabase } from '../server/infrastructure/database/index.mjs';
import { IntelligenceClient } from '../server/infrastructure/intelligence/client.mjs';
import { createDemoDataset } from '../server/infrastructure/demo/dataset.mjs';
import { createApplication } from '../server/bootstrap.mjs';
import { analyzeSessions } from '../server/application/analyze-sessions.mjs';
import { normalizeBatch } from '../server/domain/session.mjs';
import { sessionInput } from '../web/features/sessions/session-input.mjs';

const responseClient = (payload) =>
  new IntelligenceClient({
    url: 'http://intelligence.test',
    fetcher: async () => ({ ok: true, json: async () => payload }),
  });
const analysis = (candidates) => ({
  model: 'IsolationForest',
  version: 'test-model',
  training_samples: 30,
  results: candidates.map(({ id }) => ({ id, score: 0.2, reasons: [], review_status: 'clear' })),
});
const unavailable = (error) => error.code === 'service_unavailable';

test('regras físicas permanecem pendentes mesmo quando a IA retorna clear', async () => {
  const candidates = [{ id: 'PHYSICAL', reasons: ['Potência acima do limite nominal.'] }];
  const result = await analyzeSessions(
    responseClient(analysis(candidates)),
    [],
    candidates,
    '2026-10-01',
  );
  assert.equal(result.sessions[0].review_status, 'pending');
  assert.deepEqual(result.sessions[0].reasons, candidates[0].reasons);
});

test('resposta de IA incompleta ou com IDs duplicados nunca libera um lote', async () => {
  const candidates = [{ id: 'A' }, { id: 'B' }];
  for (const payload of [
    {},
    { ...analysis(candidates), results: analysis(candidates).results.slice(0, 1) },
    {
      ...analysis(candidates),
      results: [analysis(candidates).results[0], analysis(candidates).results[0]],
    },
    { ...analysis(candidates), results: analysis([{ id: 'A' }, { id: 'UNKNOWN' }]).results },
  ]) {
    await assert.rejects(() => responseClient(payload).analyze([], candidates), unavailable);
  }
});

test('resposta não JSON da IA é tratada como indisponibilidade', async () => {
  const client = new IntelligenceClient({
    url: 'http://intelligence.test',
    fetcher: async () => ({
      ok: true,
      json: async () => {
        throw new SyntaxError('Invalid JSON');
      },
    }),
  });
  await assert.rejects(() => client.analyze([], [{ id: 'A' }]), unavailable);
});

test('previsão com horas duplicadas não é entregue à interface', async () => {
  const client = responseClient({
    date: '2026-10-01',
    model: 'RandomForestRegressor',
    version: 'test-model',
    recommendation: 'Capacidade disponível.',
    peak_hour: 0,
    peak_kw: 1,
    hours: Array.from({ length: 24 }, () => ({ hour: 0, expected_kw: 1 })),
  });
  await assert.rejects(() => client.forecast([], '2026-10-01', 14.4), unavailable);
});

test('lote verifica sobreposições independentemente da ordem recebida', () => {
  const { catalog, examples } = createDemoDataset();
  const first = examples[0];
  const later = {
    ...first,
    id: 'LATER',
    start_at: '2026-09-29T06:00:00-03:00',
    end_at: '2026-09-29T08:00:00-03:00',
  };
  assert.throws(
    () => normalizeBatch([later, first], catalog),
    (error) => error.code === 'conflict',
  );
  const next = { ...later, start_at: first.end_at };
  assert.deepEqual(
    normalizeBatch([next, first], catalog).map(({ id }) => id),
    ['LATER', first.id],
  );
});

test('leituras SQLite aguardam a transação e não expõem dados revertidos', async () => {
  const database = await openDatabase({ path: ':memory:' });
  let begin, release;
  const started = new Promise((resolve) => {
    begin = resolve;
  });
  const held = new Promise((resolve) => {
    release = resolve;
  });
  const transaction = database.transaction(async (connection) => {
    await connection.query("INSERT INTO units (id, label) VALUES ('TEST', 'Teste')");
    begin();
    await held;
    throw new Error('Rollback esperado');
  });
  const rejected = assert.rejects(transaction, /Rollback esperado/);
  try {
    await started;
    let settled = false;
    const read = database.query('SELECT * FROM units').then((rows) => {
      settled = true;
      return rows;
    });
    await setImmediate();
    assert.equal(settled, false);
    release();
    await rejected;
    assert.deepEqual(await read, []);
  } finally {
    release();
    await rejected;
    await database.close();
  }
});

test('inicializações concorrentes criam o catálogo e as sessões uma única vez', async () => {
  const database = await openDatabase({ path: ':memory:' });
  const app = createApplication(database, {
    intelligence: { analyze: async (_, candidates) => analysis(candidates) },
  });
  try {
    await Promise.all([app.initializeDemo(), app.initializeDemo()]);
    assert.equal((await database.query('SELECT * FROM units')).length, 6);
    assert.equal((await database.query('SELECT * FROM sessions')).length, 370);
  } finally {
    await database.close();
  }
});

test('formulário preserva segundos e mapeia última leitura da sessão interrompida', () => {
  const fields = {
    id: 'FORM',
    start_at: '2026-09-28T05:00:30',
    end_at: '2026-09-28T06:00',
    end_meter_kwh: '105.2',
  };
  const input = sessionInput(fields, { unitId: '302', userId: 'U302', status: 'interrupted' });
  assert.equal(input.start_at, '2026-09-28T05:00:30-03:00');
  assert.equal(input.end_at, '2026-09-28T06:00:00-03:00');
  assert.equal(input.last_valid_meter_kwh, '105.2');
  assert.equal(input.end_meter_kwh, undefined);
  assert.equal(fields.end_meter_kwh, '105.2');
});

test('leitura vazia do formulário permanece ausente, sem virar consumo zero', () => {
  const input = sessionInput(
    { start_at: '2026-09-28T05:00', end_at: '2026-09-28T06:00', end_meter_kwh: '' },
    { unitId: '302', userId: 'U302', status: 'completed' },
  );
  assert.equal(input.end_meter_kwh, undefined);
});
