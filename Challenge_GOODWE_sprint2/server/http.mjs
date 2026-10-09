import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { HttpError } from './domain.mjs';

async function readJson(req) {
  const buffers = [];
  let length = 0;
  for await (const chunk of req) {
    length += chunk.length;
    if (length > 1000000) throw new HttpError(413, 'JSON excede o limite de 1 MB.');
    buffers.push(chunk);
  }
  let data;
  try {
    data = JSON.parse(Buffer.concat(buffers).toString('utf8'));
  } catch {
    throw new HttpError(400, 'JSON inválido.');
  }
  if (data == null || typeof data !== 'object' || Array.isArray(data))
    throw new HttpError(400, 'Envie um objeto JSON.');
  return data;
}
export function createHttpServer(service, { staticRoot = resolve('dist') } = {}) {
  return createServer(async (req, res) => {
    const send = (status, value, type = 'application/json; charset=utf-8') => {
      res.writeHead(status, {
        'Content-Type': type,
        'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff',
      });
      res.end(type.startsWith('application/json') ? JSON.stringify(value) : value);
    };
    try {
      const url = new URL(req.url, 'http://localhost');
      const path = url.pathname;
      const month = url.searchParams.get('month') || '2026-09';
      const unit = url.searchParams.get('unit') || undefined;
      // O protótipo é local. Recusa mutações originadas por outro site.
      if (
        req.method === 'POST' &&
        req.headers.origin &&
        new URL(req.headers.origin).host !== req.headers.host
      )
        throw new HttpError(403, 'Origem da requisição não permitida.');
      if (req.method === 'GET') {
        if (path === '/api/health')
          return send(200, { status: 'ok', mode: 'simulation', database: service.db.dialect });
        if (path === '/api/catalog') return send(200, await service.catalog());
        if (path === '/api/dashboard') return send(200, await service.dashboard(month));
        if (path === '/api/sessions') return send(200, await service.sessions(month, unit));
        if (/^\/api\/sessions\/[\w-]+\/reviews$/.test(path))
          return send(
            200,
            await service.db.query(
              'SELECT * FROM reviews WHERE session_id = $1 ORDER BY created_at',
              [path.split('/')[3]],
            ),
          );
        if (path === '/api/invoices') return send(200, await service.invoices(month, unit));
        if (path === '/api/forecast')
          return send(200, await service.forecast(url.searchParams.get('date') || '2026-10-01'));
        if (path === '/api/invoices.csv') {
          const invoices = await service.invoices(month, unit);
          const csv = [
            'fatura;unidade;mes;energia_kwh;tarifa_brl_kwh;taxa_brl;consumo_brl;total_brl',
            ...invoices.map((i) =>
              [
                i.id,
                i.unit_id,
                i.month,
                (i.energy_wh / 1000).toFixed(3),
                (i.tariff_millis / 1000).toFixed(3),
                (i.fixed_cents / 100).toFixed(2),
                (i.consumption_cents / 100).toFixed(2),
                (i.total_cents / 100).toFixed(2),
              ].join(';'),
            ),
          ].join('\r\n');
          res.setHeader('Content-Disposition', `attachment; filename="faturas-${month}.csv"`);
          return send(200, '\uFEFF' + csv, 'text/csv; charset=utf-8');
        }
      }
      if (req.method === 'POST') {
        if (path === '/api/sessions') return send(201, await service.ingest([await readJson(req)]));
        if (path === '/api/import')
          return send(201, await service.ingest((await readJson(req)).sessions));
        if (path === '/api/invoices')
          return send(200, await service.generateInvoices(await readJson(req)));
        if (/^\/api\/sessions\/[\w-]+\/review$/.test(path))
          return send(200, await service.review(path.split('/')[3], await readJson(req)));
      }
      if (path.startsWith('/api/')) throw new HttpError(404, 'Endpoint não encontrado.');
      if (req.method !== 'GET') throw new HttpError(405, 'Método não permitido.');
      const filename = resolve(staticRoot, '.' + decodeURIComponent(path));
      if (filename !== staticRoot && !filename.startsWith(staticRoot + sep))
        throw new HttpError(403, 'Caminho inválido.');
      let data,
        actual = filename;
      try {
        data = await readFile(actual);
      } catch {
        actual = resolve(staticRoot, 'index.html');
        data = await readFile(actual);
      }
      const types = {
        '.html': 'text/html; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.svg': 'image/svg+xml',
      };
      return send(200, data, types[extname(actual)] || 'application/octet-stream');
    } catch (error) {
      if (!error.status) console.error(error);
      send(error.status || 500, {
        error: error.status ? error.message : 'Erro interno. Consulte o terminal do servidor.',
      });
    }
  });
}
