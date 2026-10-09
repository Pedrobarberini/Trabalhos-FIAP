import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

export function createSqliteDatabase(path) {
  if (path !== ':memory:') mkdirSync(dirname(path), { recursive: true });
  const connection = new DatabaseSync(path);
  connection.exec('PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;');
  let queue = Promise.resolve();

  const transactionConnection = {
    async query(sql, parameters = []) {
      const positional = [];
      const statement = sql.replace(/\$(\d+)/g, (_, index) => {
        positional.push(parameters[Number(index) - 1]);
        return '?';
      });
      return connection.prepare(statement).all(...positional);
    },
  };
  const database = {
    dialect: 'sqlite',
    async query(sql, parameters = []) {
      await queue;
      return transactionConnection.query(sql, parameters);
    },
    transaction(work) {
      const task = queue.then(async () => {
        connection.exec('BEGIN IMMEDIATE');
        try {
          const result = await work(transactionConnection);
          connection.exec('COMMIT');
          return result;
        } catch (error) {
          connection.exec('ROLLBACK');
          throw error;
        }
      });
      queue = task.catch(() => {});
      return task;
    },
    async close() {
      await queue;
      connection.close();
    },
  };
  return database;
}
