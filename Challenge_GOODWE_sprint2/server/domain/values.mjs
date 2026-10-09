import { ensure } from './errors.mjs';
export function monthValue(value) {
  ensure(
    typeof value === 'string' && /^20\d{2}-(0[1-9]|1[0-2])$/.test(value),
    'Mês inválido. Use AAAA-MM.',
  );
  return value;
}
export function scaled(value, scale, name, maximum) {
  ensure(typeof value === 'number' || typeof value === 'string', `${name}: informe um número.`);
  const text = String(value);
  ensure(/^\d+(\.\d+)?$/.test(text), `${name}: número não negativo inválido.`);
  const number = Number(text);
  const result = Math.round(number * scale);
  ensure(
    Number.isFinite(number) && number <= maximum && Math.abs(number * scale - result) < 1e-6,
    `${name}: valor fora do limite ou com casas decimais em excesso.`,
  );
  return result;
}
export function timestamp(value, field) {
  ensure(
    typeof value === 'string' &&
      /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,3})?)?(Z|[+-]\d{2}:\d{2})$/.test(value),
    `${field}: informe data ISO 8601 com fuso horário.`,
  );
  const result = new Date(value);
  ensure(!Number.isNaN(result.getTime()), `${field}: data inválida.`);
  // Date aceita 30 de fevereiro e normaliza; valide o dia do calendário de origem.
  const [year, month, day] = value.slice(0, 10).split('-').map(Number);
  ensure(
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
