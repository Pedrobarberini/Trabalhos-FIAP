import { ensure } from './errors.mjs';
import { timestamp, scaled, localMonth } from './values.mjs';
export function normalizeSession(input, vehicle, user, charger) {
  ensure(
    input && typeof input === 'object' && !Array.isArray(input),
    'Sessão deve ser um objeto JSON.',
  );
  ensure(
    typeof input.id === 'string' && /^[A-Za-z0-9_-]{1,80}$/.test(input.id),
    'Identificador de sessão inválido.',
  );
  ensure(vehicle && user && charger, 'Usuário, veículo ou carregador não cadastrado.');
  ensure(
    vehicle.user_id === input.user_id && user.unit_id === input.unit_id,
    'Veículo, usuário e unidade não correspondem.',
  );
  ensure(
    ['completed', 'interrupted'].includes(input.status),
    'Status deve ser completed ou interrupted.',
  );
  const start = timestamp(input.start_at, 'Início');
  const end = timestamp(input.end_at, 'Fim');
  const duration = (end - start) / 60000;
  ensure(duration > 0 && duration <= 7 * 24 * 60, 'Duração deve ser positiva e de até sete dias.');
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

export function normalizeBatch(inputs, catalog) {
  ensure(
    Array.isArray(inputs) && inputs.length > 0 && inputs.length <= 100,
    'Envie entre 1 e 100 sessões.',
  );
  const index = (rows) => new Map(rows.map((row) => [row.id, row]));
  const vehicles = index(catalog.vehicles);
  const users = index(catalog.users);
  const chargers = index(catalog.chargers);
  const sessions = inputs.map((input) =>
    normalizeSession(
      input,
      vehicles.get(input?.vehicle_id),
      users.get(input?.user_id),
      chargers.get(input?.charger_id),
    ),
  );
  ensure(
    new Set(sessions.map((session) => session.id)).size === sessions.length,
    'Lote contém identificadores duplicados.',
    'conflict',
  );
  const schedules = new Map();
  for (const session of sessions) {
    const schedule = schedules.get(session.charger_id) || [];
    schedule.push(session);
    schedules.set(session.charger_id, schedule);
  }
  for (const schedule of schedules.values()) {
    schedule.sort((left, right) => left.start_at.localeCompare(right.start_at));
    for (let index = 1; index < schedule.length; index++) {
      ensure(
        schedule[index - 1].end_at <= schedule[index].start_at,
        'Lote contém sessões simultâneas no mesmo carregador.',
        'conflict',
      );
    }
  }
  return sessions;
}
