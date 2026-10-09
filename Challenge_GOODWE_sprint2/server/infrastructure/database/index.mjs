import { readFile } from 'node:fs/promises';
import { createPostgresDatabase } from './postgres.mjs';

export async function openDatabase({ url = '', path = 'data/chargeops.sqlite' } = {}) {
  const database = url
    ? await createPostgresDatabase(url)
    : (await import('./sqlite.mjs')).createSqliteDatabase(path);
  try {
    const schema = await readFile(new URL('../../../db/schema.sql', import.meta.url), 'utf8');
    for (const statement of schema.split(';').filter((sql) => sql.trim())) {
      await database.query(statement);
    }
    return database;
  } catch (error) {
    await database.close();
    throw error;
  }
}
