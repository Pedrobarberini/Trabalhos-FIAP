import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeSession, consumptionCents, scaled } from '../server/domain.mjs';

const vehicle = { id: 'V1', user_id: 'U1' },
  user = { id: 'U1', unit_id: '302' },
  charger = { max_kw: 7.2 };
const base = {
  id: 'S1',
  unit_id: '302',
  user_id: 'U1',
  vehicle_id: 'V1',
  charger_id: 'C1',
  start_at: '2026-09-01T10:00:00-03:00',
  end_at: '2026-09-01T11:00:00-03:00',
  status: 'completed',
  start_meter_kwh: 100,
  end_meter_kwh: 105.2,
};
const normalize = (overrides) =>
  normalizeSession({ ...base, ...overrides }, vehicle, user, charger);
test('consumo é a diferença do medidor, armazenada em Wh inteiros', () => {
  assert.equal(normalize({}).energy_wh, 5200);
  assert.equal(normalize({}).duration_minutes, 60);
});
test('sessão interrompida usa a última leitura válida e ignora medidor final', () => {
  assert.equal(
    normalize({ status: 'interrupted', last_valid_meter_kwh: 103.5, end_meter_kwh: 999 }).energy_wh,
    3500,
  );
});
test('leituras ausentes ou regressivas não viram consumo cobrável', () => {
  assert.equal(normalize({ status: 'interrupted' }).energy_wh, null);
  assert.equal(normalize({ end_meter_kwh: 99 }).energy_wh, null);
  assert.match(normalize({ end_meter_kwh: 99 }).reasons[0], /regressivo/);
});
test('potência impossível exige revisão física', () =>
  assert.match(normalize({ end_meter_kwh: 150 }).reasons[0], /limite nominal/));
test('competência considera o fim no fuso de São Paulo', () => {
  assert.equal(
    normalize({ start_at: '2026-10-01T01:00:00Z', end_at: '2026-10-01T02:00:00Z' }).billing_month,
    '2026-09',
  );
});
test('rejeita calendário inexistente, ausência de fuso e duração negativa', () => {
  for (const change of [
    { start_at: '2026-02-30T10:00:00-03:00' },
    { end_at: '2026-09-01T11:00:00' },
    { end_at: base.start_at },
  ])
    assert.throws(() => normalize(change));
});
test('rejeita associação incorreta de usuário e unidade', () =>
  assert.throws(() => normalize({ unit_id: '999' }), /não correspondem/));
test('valida casas decimais e rejeita NaN, infinito e valores negativos', () => {
  for (const value of [-1, NaN, Infinity, '1.0001', null, true])
    assert.throws(() => scaled(value, 1000, 'Teste', 100));
});
test('arredondamento financeiro ocorre depois da soma, com inteiros', () => {
  assert.equal(consumptionCents(60000, 1050), 6300);
  assert.equal(consumptionCents(5, 1000), 1);
  assert.equal(consumptionCents(4, 1000), 0);
});
