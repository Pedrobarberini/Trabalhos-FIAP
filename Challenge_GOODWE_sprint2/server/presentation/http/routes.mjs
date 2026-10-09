import { invoicesToCsv } from './csv.mjs';

const result = (body, status = 200) => ({ status, body });
const route = (method, path, handle) => ({ method, pattern: new RegExp(`^${path}$`), handle });
const query = (url) => ({
  month: url.searchParams.get('month') || '2026-09',
  unit: url.searchParams.get('unit') || undefined,
});

export function createRoutes(app) {
  return [
    route('GET', '/api/health', () => result({ status: 'ok', ...app.metadata })),
    route('GET', '/api/catalog', async () => result(await app.catalog.list())),
    route('GET', '/api/dashboard', async ({ url }) =>
      result(await app.dashboard.summarize(query(url).month)),
    ),
    route('GET', '/api/sessions', async ({ url }) => {
      const { month, unit } = query(url);
      return result(await app.sessions.list(month, unit));
    }),
    route('GET', '/api/sessions/([\\w-]+)/reviews', async ({ params }) =>
      result(await app.sessions.reviews(params[0])),
    ),
    route('GET', '/api/invoices', async ({ url }) => {
      const { month, unit } = query(url);
      return result(await app.billing.list(month, unit));
    }),
    route('GET', '/api/invoices\\.csv', async ({ url }) => {
      const { month, unit } = query(url);
      const invoices = await app.billing.list(month, unit);
      return {
        body: invoicesToCsv(invoices),
        type: 'text/csv; charset=utf-8',
        headers: { 'Content-Disposition': `attachment; filename="faturas-${month}.csv"` },
      };
    }),
    route('GET', '/api/forecast', async ({ url }) =>
      result(await app.forecast.predict(url.searchParams.get('date') || '2026-10-01')),
    ),
    route('POST', '/api/sessions', async ({ body }) =>
      result(await app.sessions.register([body]), 201),
    ),
    route('POST', '/api/import', async ({ body }) =>
      result(await app.sessions.register(body.sessions), 201),
    ),
    route('POST', '/api/invoices', async ({ body }) => result(await app.billing.generate(body))),
    route('POST', '/api/sessions/([\\w-]+)/review', async ({ params, body }) =>
      result(await app.sessions.review(params[0], body)),
    ),
  ];
}
