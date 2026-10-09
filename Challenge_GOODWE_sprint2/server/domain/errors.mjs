export class ApplicationError extends Error {
  constructor(code, message, options) {
    super(message, options);
    this.name = 'ApplicationError';
    this.code = code;
  }
}

export function ensure(condition, message, code = 'validation') {
  if (!condition) throw new ApplicationError(code, message);
}
