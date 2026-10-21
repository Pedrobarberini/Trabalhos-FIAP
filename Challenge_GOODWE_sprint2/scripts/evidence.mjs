import assert from 'node:assert/strict';
import { createServer } from 'node:net';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { python, run, waitFor } from './runtime.mjs';
import { openDatabase } from '../server/infrastructure/database/index.mjs';
import { IntelligenceClient } from '../server/infrastructure/intelligence/client.mjs';
import { createApplication } from '../server/bootstrap.mjs';
import { createHttpServer } from '../server/presentation/http/server.mjs';

const folder = resolve('docs/evidencias');
await mkdir(folder, { recursive: true });

async function capture(args, filename) {
  const child = run(process.execPath, args, { stdio: ['ignore', 'pipe', 'pipe'] });
  const chunks = [];
  for (const stream of [child.stdout, child.stderr])
    stream.on('data', (chunk) => chunks.push(chunk));
  const code = await new Promise((resolve, reject) => {
    child.once('error', reject);
    child.once('close', resolve);
  });
  const output = Buffer.concat(chunks).toString('utf8').replaceAll('\r\n', '\n');
  await writeFile(
    resolve(folder, filename),
    `Comando: node ${args.join(' ')}\nData UTC: ${new Date().toISOString()}\nCódigo de saída: ${code}\n\n${output}`,
    'utf8',
  );
  assert.equal(code, 0, `Falha em ${filename}. Consulte o registro da execução.`);
  return output;
}

console.log('Compilando a interface e registrando a saída…');
await capture(['node_modules/vite/bin/vite.js', 'build'], 'build.txt');
console.log('Executando os testes Node.js e Python…');
const testOutput = await capture(['scripts/test.mjs'], 'testes.txt');
assert.match(testOutput, /Ran 5 tests/);
assert.match(testOutput, /pass\s+35/);

const reservation = createServer();
await new Promise((resolve) => reservation.listen(0, '127.0.0.1', resolve));
const aiPort = reservation.address().port;
await new Promise((resolve) => reservation.close(resolve));
const ai = run(python(), ['ai/service.py'], {
  env: { ...process.env, AI_HOST: '127.0.0.1', AI_PORT: String(aiPort) },
});

let database, server;
const evidence = {
  executed_at_utc: new Date().toISOString(),
  node_version: process.version,
  mode: 'simulation',
  database: 'sqlite :memory:',
  tests: { node_passed: 35, python_passed: 5, total_passed: 40 },
  requests: [],
  assertions: [],
};

try {
  await waitFor(`http://127.0.0.1:${aiPort}/health`, ai);
  database = await openDatabase({ path: ':memory:', url: '' });
  const app = createApplication(database, {
    intelligence: new IntelligenceClient({ url: `http://127.0.0.1:${aiPort}` }),
  });
  await app.initializeDemo();
  server = createHttpServer(app);
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const base = `http://127.0.0.1:${server.address().port}`;

  async function request(path, body, expectedStatus = 200) {
    const method = body === undefined ? 'GET' : 'POST';
    const response = await fetch(
      base + path,
      body === undefined
        ? {}
        : {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
          },
    );
    const payload = response.headers.get('content-type')?.includes('application/json')
      ? await response.json()
      : await response.text();
    evidence.requests.push({
      method,
      path,
      ...(body === undefined ? {} : { body }),
      expected_status: expectedStatus,
      status: response.status,
      response: payload,
    });
    assert.equal(response.status, expectedStatus, `${method} ${path}`);
    return payload;
  }

  await request('/api/health');
  const initial = await request('/api/dashboard?month=2026-09');
  assert.equal(initial.sessions, 184);
  assert.equal(initial.pending, 2);
  evidence.initial_dashboard = initial;

  const forecast = await request('/api/forecast?date=2026-10-01');
  assert.equal(forecast.model, 'RandomForestRegressor');
  assert.equal(forecast.hours.length, 24);
  assert.equal(forecast.training_days, 61);
  evidence.forecast = forecast;

  const session = {
    id: 'EVIDENCIA-501',
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
  const registration = await request('/api/sessions', session, 201);
  assert.equal(registration.sessions[0].energy_wh, 5200);
  assert.match(registration.sessions[0].model_version, /chargeops/);
  await request('/api/sessions', session, 409);
  await request('/api/invoices', { month: '2026-09', tariff: '1.05', fixed_fee: '20.00' }, 409);

  if (registration.sessions[0].review_status === 'pending') {
    await request('/api/sessions/EVIDENCIA-501/review', {
      decision: 'approved',
      reason: 'Sessão sintética conferida: medidor de 100 para 105,2 kWh em uma hora.',
    });
  }
  for (const id of ['DEMO-ANOMALIA', 'DEMO-SEM-LEITURA']) {
    await request(`/api/sessions/${id}/review`, {
      decision: 'rejected',
      reason: 'Cenário sintético de validação: registro inconsistente excluído do faturamento.',
    });
  }
  const audit = await request('/api/sessions/DEMO-ANOMALIA/reviews');
  assert.equal(audit.length, 1);

  const values = { month: '2026-09', tariff: '1.05', fixed_fee: '20.00' };
  const invoices = await request('/api/invoices', values);
  const unit302 = invoices.find((invoice) => invoice.unit_id === '302');
  const unit999 = invoices.find((invoice) => invoice.unit_id === '999');
  assert.equal(invoices.length, 6);
  assert.equal(unit302.energy_wh, 60000);
  assert.equal(unit302.consumption_cents, 6300);
  assert.equal(unit302.total_cents, 8300);
  assert.equal(unit999.energy_wh, 0);
  assert.equal(unit999.total_cents, 2000);
  assert.deepEqual(await request('/api/invoices', values), invoices);
  const csv = await request('/api/invoices.csv?month=2026-09');
  assert.match(csv, /60\.000;1\.050;20\.00;63\.00;83\.00/);
  await writeFile(resolve(folder, 'faturas.csv'), csv, 'utf8');
  const resident = await request('/api/sessions?month=2026-09&unit=302');
  assert.equal(resident.length, 2);
  assert(resident.every((item) => item.unit_id === '302'));
  const final = await request('/api/dashboard?month=2026-09');
  assert.equal(final.sessions, 185);
  assert.equal(final.pending, 0);
  assert.equal(final.invoices, 6);

  evidence.final_dashboard = final;
  evidence.unit_302_invoice = unit302;
  evidence.assertions = [
    'Cenário inicial: 184 sessões em setembro e 2 pendências analisadas pela IA.',
    'Nova sessão: 105,2 - 100 = 5,2 kWh, com versão do modelo registrada.',
    'Reenvio duplicado: HTTP 409, sem duplicação de consumo.',
    'Fechamento com pendências: HTTP 409.',
    'Revisões justificadas preservam trilha de auditoria.',
    'Unidade 302: dois veículos, 60 kWh, R$ 63 de energia e R$ 20 de taxa = R$ 83.',
    'Unidade 999 sem recarga: consumo variável zero e taxa configurada de R$ 20.',
    'Repetição do fechamento mantém as mesmas faturas.',
    'CSV exportado corresponde aos valores calculados.',
    'Consulta por unidade retorna apenas as duas sessões da unidade 302.',
    'Previsão: 24 horas, histórico de 61 dias e comparação com média histórica.',
    'Cenário final: 185 sessões, nenhuma pendência e 6 faturas.',
  ];
  await writeFile(
    resolve(folder, 'execucao.json'),
    JSON.stringify(evidence, null, 2) + '\n',
    'utf8',
  );
  console.log('Evidências verificadas: build, 40 testes, fluxo HTTP, IA e exportação CSV.');
  console.log('Arquivos gerados em docs/evidencias/. Banco local preservado.');
} finally {
  if (server) {
    server.closeAllConnections();
    await new Promise((resolve) => server.close(resolve));
  }
  if (database) await database.close();
  ai.kill();
}
