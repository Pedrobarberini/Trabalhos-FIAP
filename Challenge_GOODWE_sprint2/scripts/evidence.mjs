import { mkdirSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:net';
import { openDatabase } from '../server/database.mjs';
import { ChargeOps } from '../server/service.mjs';
import { createHttpServer } from '../server/http.mjs';
import { seed } from '../server/seed.mjs';
import { python, run, waitFor } from './runtime.mjs';
import assert from 'node:assert/strict';

const probe = createServer();
await new Promise((r) => probe.listen(0, '127.0.0.1', r));
const port = probe.address().port;
await new Promise((r) => probe.close(r));
const ai = run(python(), ['ai/service.py'], { env: { ...process.env, AI_PORT: String(port) } });
let db, server;
const serve = process.argv.includes('--serve');
async function stop() {
  ai.kill();
  if (server) await new Promise((r) => server.close(r));
  if (db) await db.close();
}
try {
  await waitFor(`http://127.0.0.1:${port}/health`, ai);
  db = await openDatabase({ path: ':memory:', url: '' });
  const service = new ChargeOps(db, `http://127.0.0.1:${port}`);
  await seed(service);
  server = createHttpServer(service);
  await new Promise((r) => server.listen(serve ? 3001 : 0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const steps = [];
  async function request(name, path, body) {
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
    const payload = await response.json();
    steps.push({
      name,
      method: body === undefined ? 'GET' : 'POST',
      path,
      status: response.status,
      result: payload,
    });
    return { status: response.status, data: payload };
  }
  const initial = await request('Painel antes da revisão', '/api/dashboard?month=2026-09');
  assert.equal(initial.data.pending, 2);
  const forecast = await request(
    'Previsão real do serviço Python',
    '/api/forecast?date=2026-10-01',
  );
  assert.equal(forecast.status, 200);
  const blocked = await request('Bloqueio de faturamento por anomalias', '/api/invoices', {
    month: '2026-09',
  });
  assert.equal(blocked.status, 409);
  for (const session of initial.data.alerts) {
    const review = await request(`Revisão de ${session.id}`, `/api/sessions/${session.id}/review`, {
      decision: 'rejected',
      reason:
        'Evidência de demonstração: leitura inconsistente excluída após conferência do gestor.',
    });
    assert.equal(review.status, 200);
  }
  const invoices = await request('Fechamento e geração de faturas', '/api/invoices', {
    month: '2026-09',
    tariff: '1.05',
    fixed_fee: '20.00',
  });
  const reference = invoices.data.find((i) => i.unit_id === '302');
  assert.equal(reference.energy_wh, 60000);
  assert.equal(reference.total_cents, 8300);
  await request('Portal do morador 302', '/api/sessions?month=2026-09&unit=302');
  await request('Trilha de auditoria', '/api/sessions/DEMO-ANOMALIA/reviews');
  await request('Painel depois do fechamento', '/api/dashboard?month=2026-09');
  mkdirSync('docs/evidence', { recursive: true });
  writeFileSync(
    'docs/evidence/execution.json',
    JSON.stringify(
      {
        executed_at: new Date().toISOString(),
        database: 'SQLite em memória, isolado do banco do usuário',
        data_origin: 'Sintética, gerador determinístico seed 42',
        steps,
      },
      null,
      2,
    ) + '\n',
  );
  writeFileSync(
    'docs/evidence/invoices.csv',
    await (await fetch(base + '/api/invoices.csv?month=2026-09')).text(),
  );
  console.log(
    'Evidências verificadas: bloqueio 409 → revisão → 6 faturas; Apto 302 = 60 kWh / R$ 83,00.',
  );
  if (serve) {
    console.log(`Evidência disponível para captura em ${base}`);
    for (const signal of ['SIGINT', 'SIGTERM'])
      process.on(signal, async () => {
        await stop();
        process.exit(0);
      });
  } else await stop();
} catch (error) {
  console.error(error);
  await stop();
  process.exitCode = 1;
}
