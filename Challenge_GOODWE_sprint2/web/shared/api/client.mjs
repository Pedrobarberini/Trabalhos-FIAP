function queryString(parameters) {
  return new URLSearchParams(
    Object.entries(parameters).filter(([, value]) => value != null),
  ).toString();
}

async function request(path, { body, signal } = {}) {
  const response = await fetch(`/api${path}`, {
    signal,
    ...(body === undefined
      ? {}
      : {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        }),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || 'Falha ao carregar dados.');
  return payload;
}

export const chargeOpsApi = Object.freeze({
  async operations(month, signal) {
    const query = queryString({ month });
    const [catalog, dashboard, sessions, invoices] = await Promise.all([
      request('/catalog', { signal }),
      request(`/dashboard?${query}`, { signal }),
      request(`/sessions?${query}`, { signal }),
      request(`/invoices?${query}`, { signal }),
    ]);
    return { catalog, dashboard, sessions, invoices };
  },
  forecast: (date, signal) => request(`/forecast?${queryString({ date })}`, { signal }),
  register: (body) => request('/sessions', { body }),
  import: (body) => request('/import', { body }),
  review: (id, body) => request(`/sessions/${encodeURIComponent(id)}/review`, { body }),
  generateInvoices: (body) => request('/invoices', { body }),
  invoiceExport: (month) => `/api/invoices.csv?${queryString({ month })}`,
});
