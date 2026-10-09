import { readFile } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { ApplicationError, ensure } from '../../domain/errors.mjs';

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
};

export async function serveStatic(pathname, root) {
  let decoded;
  try {
    decoded = decodeURIComponent(pathname);
  } catch (cause) {
    throw new ApplicationError('bad_request', 'Caminho inválido.', { cause });
  }
  const filename = resolve(root, '.' + decoded);
  ensure(filename === root || filename.startsWith(root + sep), 'Caminho inválido.', 'forbidden');
  let actual = filename;
  let body;
  try {
    body = await readFile(actual);
  } catch (error) {
    if (!['ENOENT', 'EISDIR'].includes(error.code)) throw error;
    ensure(!extname(decoded), 'Arquivo não encontrado.', 'not_found');
    actual = resolve(root, 'index.html');
    body = await readFile(actual);
  }
  return { body, type: TYPES[extname(actual)] || 'application/octet-stream' };
}
