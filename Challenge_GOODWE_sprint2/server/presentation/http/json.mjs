import { ApplicationError, ensure } from '../../domain/errors.mjs';

const MAX_BODY_BYTES = 1000000;

export async function readJson(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    ensure(size <= MAX_BODY_BYTES, 'JSON excede o limite de 1 MB.', 'payload_too_large');
    chunks.push(chunk);
  }
  let body;
  try {
    body = JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch (cause) {
    throw new ApplicationError('bad_request', 'JSON inválido.', { cause });
  }
  ensure(
    body && typeof body === 'object' && !Array.isArray(body),
    'Envie um objeto JSON.',
    'bad_request',
  );
  return body;
}

export function sendResponse(
  response,
  { status = 200, body, type = 'application/json; charset=utf-8', headers = {} },
) {
  response.writeHead(status, {
    'Content-Type': type,
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    ...headers,
  });
  response.end(type.startsWith('application/json') ? JSON.stringify(body) : body);
}
