export class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}
export function assert(condition, message, status = 422) {
  if (!condition) throw new HttpError(status, message);
}
export function monthValue(value) {
  assert(
    typeof value === 'string' && /^20\d{2}-(0[1-9]|1[0-2])$/.test(value),
    'Mês inválido. Use AAAA-MM.',
  );
  return value;
}
export function scaled(value, scale, name, maximum) {
  assert(typeof value === 'number' || typeof value === 'string', `${name}: informe um número.`);
  const text = String(value);
  assert(/^\d+(\.\d+)?$/.test(text), `${name}: número não negativo inválido.`);
  const number = Number(text);
  const result = Math.round(number * scale);
  assert(
    Number.isFinite(number) && number <= maximum && Math.abs(number * scale - result) < 1e-6,
    `${name}: valor fora do limite ou com casas decimais em excesso.`,
  );
  return result;
}
function timestamp(value, field) {
  assert(
    typeof value === 'string' &&
      /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,3})?)?(Z|[+-]\d{2}:\d{2})$/.test(value),
    `${field}: informe data ISO 8601 com fuso horário.`,
  );
  const result = new Date(value);
  assert(!Number.isNaN(result.getTime()), `${field}: data inválida.`);
  // Date aceita 30 de fevereiro e normaliza; valide o dia do calendário de origem.
  const [year, month, day] = value.slice(0, 10).split('-').map(Number);
  assert(
    month >= 1 && month <= 12 && day >= 1 && day <= new Date(Date.UTC(year, month, 0)).getUTCDate(),
    `${field}: dia inexistente.`,
  );
  return result;
}
export function localMonth(date) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Sao_Paulo',
    year: 'numeric',
    month: '2-digit',
  }).formatToParts(date);
  return `${parts.find((p) => p.type === 'year').value}-${parts.find((p) => p.type === 'month').value}`;
}
export function normalizeSession(input, vehicle, user, charger) {
  assert(
    input && typeof input === 'object' && !Array.isArray(input),
    'Sessão deve ser um objeto JSON.',
  );
  assert(
    typeof input.id === 'string' && /^[A-Za-z0-9_-]{1,80}$/.test(input.id),
    'Identificador de sessão inválido.',
  );
  assert(vehicle && user && charger, 'Usuário, veículo ou carregador não cadastrado.');
  assert(
    vehicle.user_id === input.user_id && user.unit_id === input.unit_id,
    'Veículo, usuário e unidade não correspondem.',
  );
  assert(
    ['completed', 'interrupted'].includes(input.status),
    'Status deve ser completed ou interrupted.',
  );
  const start = timestamp(input.start_at, 'Início');
  const end = timestamp(input.end_at, 'Fim');
  const duration = (end - start) / 60000;
  assert(duration > 0 && duration <= 7 * 24 * 60, 'Duração deve ser positiva e de até sete dias.');
  const startWh = scaled(input.start_meter_kwh, 1000, 'Medidor inicial', 1000000);
  const reading = input.status === 'interrupted' ? input.last_valid_meter_kwh : input.end_meter_kwh;
  const finalWh = reading == null ? null : scaled(reading, 1000, 'Medidor final válido', 1000000);
  const reasons = [];
  let energyWh = finalWh == null ? null : finalWh - startWh;
  if (energyWh == null)
    reasons.push('Medição final válida ausente; consumo não pode ser estimado para cobrança.');
  if (energyWh < 0) {
    energyWh = null;
    reasons.push('Medidor regressivo; conferir as leituras originais.');
  }
  if (energyWh != null && energyWh / 1000 / (duration / 60) > charger.max_kw * 1.1)
    reasons.push('Potência média acima do limite nominal do carregador (+10% de tolerância).');
  return {
    id: input.id,
    source: input.source === 'sems-import' ? 'sems-import' : 'simulation',
    user_id: input.user_id,
    vehicle_id: input.vehicle_id,
    charger_id: input.charger_id,
    unit_id: input.unit_id,
    start_at: start.toISOString(),
    end_at: end.toISOString(),
    billing_month: localMonth(end),
    start_wh: startWh,
    final_wh: finalWh,
    energy_wh: energyWh,
    duration_minutes: duration,
    status: input.status,
    reasons,
  };
}
export function consumptionCents(energyWh, tariffMillis) {
  return Number((BigInt(energyWh) * BigInt(tariffMillis) + 5000n) / 10000n);
}
export function publicSession(row) {
  return {
    ...row,
    reasons: typeof row.reasons === 'string' ? JSON.parse(row.reasons) : row.reasons,
    energy_kwh: row.energy_wh == null ? null : row.energy_wh / 1000,
    average_kw: row.energy_wh == null ? null : row.energy_wh / 1000 / (row.duration_minutes / 60),
  };
}
