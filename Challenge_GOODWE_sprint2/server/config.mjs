function port(value, fallback) {
  const parsed = Number(value ?? fallback);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 65535) {
    throw new Error('A porta deve ser um número inteiro entre 1 e 65535.');
  }
  return parsed;
}

export function loadConfig(env = process.env) {
  const aiPort = port(env.AI_PORT, 8001);
  return Object.freeze({
    host: env.HOST || '127.0.0.1',
    port: port(env.PORT, 3000),
    database: { url: env.DATABASE_URL || '', path: env.DB_PATH || 'data/chargeops.sqlite' },
    intelligence: { url: env.AI_URL || `http://127.0.0.1:${aiPort}`, timeoutMs: 30000 },
    aiPort,
    externalIntelligence: Boolean(env.AI_URL),
  });
}
