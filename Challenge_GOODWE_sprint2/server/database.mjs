import { readFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

// Um cliente por transação: impede requisições concorrentes de misturar COMMITs.
export async function openDatabase({
  url = process.env.DATABASE_URL,
  path = process.env.DB_PATH || 'data/chargeops.sqlite',
} = {}) {
  let db;
  if (url) {
    const { default: pg } = await import('pg');
    const pool = new pg.Pool({ connectionString: url });
    db = {
      dialect: 'postgresql',
      query: async (sql, args = []) => (await pool.query(sql, args)).rows,
      async transaction(fn) {
        const client = await pool.connect();
        try {
          await client.query('BEGIN');
          // Serializa ingestão, revisões e fechamento mensal, inclusive entre processos.
          await client.query('SELECT pg_advisory_xact_lock(260202)');
          const tx = { query: async (sql, args = []) => (await client.query(sql, args)).rows };
          const result = await fn(tx);
          await client.query('COMMIT');
          return result;
        } catch (error) {
          await client.query('ROLLBACK');
          throw error;
        } finally {
          client.release();
        }
      },
      close: () => pool.end(),
    };
  } else {
    const { DatabaseSync } = await import('node:sqlite');
    if (path !== ':memory:') mkdirSync(dirname(path), { recursive: true });
    const sqlite = new DatabaseSync(path);
    sqlite.exec('PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;');
    let queue = Promise.resolve();
    db = {
      dialect: 'sqlite',
      async query(sql, args = []) {
        // PostgreSQL usa $1; SQLite recebe parâmetros posicionais na ordem de ocorrência.
        const params = [];
        const normalized = sql.replace(/\$(\d+)/g, (_, n) => {
          params.push(args[Number(n) - 1]);
          return '?';
        });
        const statement = sqlite.prepare(normalized);
        return statement.all(...params);
      },
      transaction(fn) {
        const task = queue.then(async () => {
          sqlite.exec('BEGIN IMMEDIATE');
          try {
            const result = await fn(db);
            sqlite.exec('COMMIT');
            return result;
          } catch (error) {
            sqlite.exec('ROLLBACK');
            throw error;
          }
        });
        queue = task.catch(() => {});
        return task;
      },
      close: async () => {
        await queue;
        sqlite.close();
      },
    };
  }
  const schema = readFileSync(new URL('../db/schema.sql', import.meta.url), 'utf8');
  for (const statement of schema.split(';').filter((s) => s.trim())) await db.query(statement);
  return db;
}
