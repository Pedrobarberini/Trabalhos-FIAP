export const brl = (cents) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100);
export const number = (n) => new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format(n);
export const energyNumber = (n) =>
  new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 3 }).format(n);
export const date = (value) =>
  new Intl.DateTimeFormat('pt-BR', {
    timeZone: 'America/Sao_Paulo',
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
export const nextDate = (month) => {
  const dt = new Date(`${month}-01T12:00:00Z`);
  dt.setUTCMonth(dt.getUTCMonth() + 1);
  return dt.toISOString().slice(0, 10);
};
