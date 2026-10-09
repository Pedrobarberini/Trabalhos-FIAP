import { ApplicationError } from '../../domain/errors.mjs';

const STATUS = Object.freeze({
  bad_request: 400,
  forbidden: 403,
  not_found: 404,
  method_not_allowed: 405,
  conflict: 409,
  payload_too_large: 413,
  validation: 422,
  service_unavailable: 503,
});

export function errorResponse(error, logger) {
  if (error instanceof ApplicationError)
    return { status: STATUS[error.code] || 500, body: { error: error.message } };
  logger.error(error);
  return { status: 500, body: { error: 'Erro interno. Consulte o terminal do servidor.' } };
}
