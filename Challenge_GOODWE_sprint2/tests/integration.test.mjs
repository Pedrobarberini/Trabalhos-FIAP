import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { openDatabase } from '../server/database.mjs';
import { ChargeOps } from '../server/service.mjs';
import { createHttpServer } from '../server/http.mjs';
import { seed } from '../server/seed.mjs';

let db, service, server, base;
const sample = {
  id: 'TEST-VALID',
  user_id: 'U501',
  unit_id: '501',
  vehicle_id: 'V501',
  charger_id: 'HCA01',
  start_at: '2026-09-28T05:00:00-03:00',
  end_at: '2026-09-28T06:00:00-03:00',
  status: 'completed',
  start_meter_kwh: 100,
  end_meter_kwh: 105.2,
};
async function request(path, body) {
  const response = await fetch(
    base + path,
    body === undefined
      ? {}
      : {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        },
  );
  return { status: response.status, data: await response.json() };
}
before(async () => {
  db = await openDatabase({ path: ':memory:', url: '' });
  service = new ChargeOps(db);
  await seed(service);
  server = createHttpServer(service);
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  base = `http://127.0.0.1:${server.address().port}`;
});
after(async () => {
  if (server) await new Promise((r) => server.close(r));
  if (db) await db.close();
});

test('seed contém histórico e duas anomalias demonstráveis analisadas pela IA real', async () => {
  const { data, status } = await request('/api/dashboard?month=2026-09');
  assert.equal(status, 200);
  assert.equal(data.pending, 2);
  assert.equal(data.sessions, 184);
  assert(
    data.alerts
      .find((s) => s.id === 'DEMO-ANOMALIA')
      .reasons.some((r) => r.includes('Isolation Forest')),
  );
});
test('previsão usa o serviço Python e expõe avaliação temporal e baseline', async () => {
  const { data, status } = await request('/api/forecast?date=2026-10-01');
  assert.equal(status, 200);
  assert.equal(data.model, 'RandomForestRegressor');
  assert.equal(data.hours.length, 24);
  assert.equal(data.training_days, 61);
  assert(Number.isFinite(data.validation_mae_kw));
  assert(Number.isFinite(data.baseline_mae_kw));
});
test('registra uma sessão pela API, calcula o consumo e mantém a versão do modelo', async () => {
  const result = await request('/api/sessions', sample);
  assert.equal(result.status, 201);
  assert.equal(result.data.sessions[0].energy_wh, 5200);
  assert.match(result.data.sessions[0].model_version, /chargeops/);
});
test('duplicatas e intervalos simultâneos são recusados sem duplicar consumo', async () => {
  assert.equal((await request('/api/sessions', sample)).status, 409);
  assert.equal((await request('/api/sessions', { ...sample, id: 'OVERLAP' })).status, 409);
  assert.equal((await db.query("SELECT id FROM sessions WHERE id = 'TEST-VALID'")).length, 1);
});
test('lote inválido é atômico e não deixa registros parciais', async () => {
  const result = await request('/api/import', {
    sessions: [
      {
        ...sample,
        id: 'ATOMIC',
        start_at: '2026-09-27T05:00:00-03:00',
        end_at: '2026-09-27T06:00:00-03:00',
      },
      { ...sample, id: 'BAD-USER', user_id: 'U999' },
    ],
  });
  assert.equal(result.status, 422);
  assert.equal((await db.query("SELECT id FROM sessions WHERE id = 'ATOMIC'")).length, 0);
});
test('indisponibilidade da IA bloqueia ingestão, sem liberação silenciosa', async () => {
  const offline = new ChargeOps(db, 'http://127.0.0.1:1');
  await assert.rejects(
    () =>
      offline.ingest([
        {
          ...sample,
          id: 'OFFLINE',
          start_at: '2026-09-26T05:00:00-03:00',
          end_at: '2026-09-26T06:00:00-03:00',
        },
      ]),
    (error) => error.status === 503,
  );
  assert.equal((await db.query("SELECT id FROM sessions WHERE id = 'OFFLINE'")).length, 0);
  const startup = await openDatabase({ path: ':memory:', url: '' });
  try {
    await assert.rejects(
      () => seed(new ChargeOps(startup, 'http://127.0.0.1:1')),
      (error) => error.status === 503,
    );
    assert.equal((await startup.query('SELECT id FROM units')).length, 0);
    assert.equal((await startup.query('SELECT id FROM sessions')).length, 0);
  } finally {
    await startup.close();
  }
});
test('ingestões concorrentes com o mesmo ID resultam em uma única sessão', async () => {
  const input = {
    ...sample,
    id: 'RACE',
    start_at: '2026-09-25T05:00:00-03:00',
    end_at: '2026-09-25T06:00:00-03:00',
  };
  const results = await Promise.all([
    request('/api/sessions', input),
    request('/api/sessions', input),
  ]);
  assert.deepEqual(results.map((r) => r.status).sort(), [201, 409]);
});
test('sem histórico suficiente a IA exige revisão, em vez de marcar como normal', async () => {
  const empty = await openDatabase({ path: ':memory:', url: '' });
  try {
    const result = await service.ai('/analyze', {
      history: [],
      candidates: [{ id: 'COLD', energy_wh: 5200, duration_minutes: 60, reasons: [] }],
    });
    assert.equal(result.results[0].review_status, 'pending');
    assert.equal(result.results[0].score, null);
  } finally {
    await empty.close();
  }
});
test('sessões pendentes impedem faturamento', async () =>
  assert.equal((await request('/api/invoices', { month: '2026-09' })).status, 409));
test('não aprova registro sem leitura e exige justificativa na revisão', async () => {
  assert.equal(
    (
      await request('/api/sessions/DEMO-SEM-LEITURA/review', {
        decision: 'approved',
        reason: 'Medição conferida pelo gestor.',
      })
    ).status,
    422,
  );
  assert.equal(
    (await request('/api/sessions/DEMO-ANOMALIA/review', { decision: 'rejected', reason: 'ok' }))
      .status,
    422,
  );
});
test('rejeição preserva registro original e trilha de auditoria', async () => {
  const pending = (await service.sessions('2026-09')).filter((s) => s.review_status === 'pending');
  for (const session of pending)
    assert.equal(
      (
        await request(`/api/sessions/${session.id}/review`, {
          decision: 'rejected',
          reason: 'Cenário sintético revisado: registro excluído para validar o fechamento.',
        })
      ).status,
      200,
    );
  const reviews = await request('/api/sessions/DEMO-ANOMALIA/reviews');
  assert.equal(reviews.data.length, 1);
  assert.equal(
    (await db.query("SELECT energy_wh FROM sessions WHERE id = 'DEMO-ANOMALIA'"))[0].energy_wh,
    50000,
  );
});
test('fatura reproduz 60 kWh em dois veículos, R$ 63 + R$ 20 = R$ 83', async () => {
  const result = await request('/api/invoices', {
    month: '2026-09',
    tariff: '1.05',
    fixed_fee: '20.00',
  });
  assert.equal(result.status, 200);
  assert.equal(result.data.length, 6);
  const invoice = result.data.find((i) => i.unit_id === '302');
  assert.equal(invoice.energy_wh, 60000);
  assert.equal(invoice.consumption_cents, 6300);
  assert.equal(invoice.total_cents, 8300);
  assert.deepEqual(invoice.session_ids, ['DEMO-302-25', 'DEMO-302-35']);
  const noUsage = result.data.find((i) => i.unit_id === '999');
  assert.equal(noUsage.energy_wh, 0);
  assert.equal(noUsage.consumption_cents, 0);
  assert.equal(noUsage.total_cents, 2000);
});
test('fechamento é idempotente, imutável e encerra importações no mês', async () => {
  assert.equal((await request('/api/invoices', { month: '2026-09' })).status, 200);
  assert.equal((await request('/api/invoices', { month: '2026-09', tariff: '2.00' })).status, 409);
  assert.equal(
    (
      await request('/api/sessions', {
        ...sample,
        id: 'AFTER-CLOSE',
        start_at: '2026-09-24T05:00:00-03:00',
        end_at: '2026-09-24T06:00:00-03:00',
      })
    ).status,
    409,
  );
});
test('filtro do morador retorna apenas sessões e faturas da unidade escolhida', async () => {
  assert(
    (await request('/api/sessions?month=2026-09&unit=302')).data.every((s) => s.unit_id === '302'),
  );
  assert.equal((await request('/api/invoices?month=2026-09&unit=302')).data.length, 1);
  assert.equal((await request('/api/sessions?month=2026-09&unit=%27%20OR%201%3D1')).data.length, 0);
});
test('exportação CSV contém os mesmos valores da fatura', async () => {
  const response = await fetch(base + '/api/invoices.csv?month=2026-09&unit=302');
  assert.equal(response.status, 200);
  assert.match(await response.text(), /60\.000;1\.050;20\.00;63\.00;83\.00/);
});
test('API valida JSON, meses, lote vazio e origem de mutações', async () => {
  assert.equal((await request('/api/sessions?month=2026-13')).status, 422);
  assert.equal((await request('/api/import', { sessions: [] })).status, 422);
  assert.equal((await request('/api/import', null)).status, 400);
  assert.equal((await fetch(base + '/api/import', { method: 'POST', body: '{bad' })).status, 400);
  assert.equal(
    (
      await fetch(base + '/api/import', {
        method: 'POST',
        headers: { Origin: 'https://example.com' },
        body: '{}',
      })
    ).status,
    403,
  );
});
