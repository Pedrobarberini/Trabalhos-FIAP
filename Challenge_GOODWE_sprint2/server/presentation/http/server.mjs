import { createServer } from 'node:http';
import { resolve } from 'node:path';
import { ensure } from '../../domain/errors.mjs';
import { readJson, sendResponse } from './json.mjs';
import { errorResponse } from './errors.mjs';
import { createRoutes } from './routes.mjs';
import { serveStatic } from './static-files.mjs';

function validateOrigin(request) {
  if (request.method !== 'POST' || !request.headers.origin) return;
  let origin;
  try {
    origin = new URL(request.headers.origin);
  } catch {}
  ensure(origin?.host === request.headers.host, 'Origem da requisição não permitida.', 'forbidden');
}

export function createHttpServer(app, { staticRoot = resolve('dist'), logger = console } = {}) {
  const routes = createRoutes(app);
  return createServer(async (request, response) => {
    try {
      validateOrigin(request);
      const url = new URL(request.url, 'http://localhost');
      const route = routes.find(
        (candidate) => candidate.method === request.method && candidate.pattern.test(url.pathname),
      );
      if (route) {
        const body = request.method === 'POST' ? await readJson(request) : undefined;
        const params = route.pattern.exec(url.pathname).slice(1);
        return sendResponse(response, await route.handle({ url, body, params }));
      }
      ensure(!url.pathname.startsWith('/api/'), 'Endpoint não encontrado.', 'not_found');
      ensure(request.method === 'GET', 'Método não permitido.', 'method_not_allowed');
      return sendResponse(response, await serveStatic(url.pathname, resolve(staticRoot)));
    } catch (error) {
      sendResponse(response, errorResponse(error, logger));
    }
  });
}
