const HEADERS = 'fatura;unidade;mes;energia_kwh;tarifa_brl_kwh;taxa_brl;consumo_brl;total_brl';

export function invoicesToCsv(invoices) {
  const rows = invoices.map((invoice) =>
    [
      invoice.id,
      invoice.unit_id,
      invoice.month,
      (invoice.energy_wh / 1000).toFixed(3),
      (invoice.tariff_millis / 1000).toFixed(3),
      (invoice.fixed_cents / 100).toFixed(2),
      (invoice.consumption_cents / 100).toFixed(2),
      (invoice.total_cents / 100).toFixed(2),
    ].join(';'),
  );
  return '\uFEFF' + [HEADERS, ...rows].join('\r\n');
}
