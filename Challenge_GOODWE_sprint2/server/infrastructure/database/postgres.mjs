const MUTATION_LOCK = 260202;

export async function createPostgresDatabase(url) {
  const { default: pg } = await import('pg');
  const pool = new pg.Pool({ connectionString: url });
  return {
    dialect: 'postgresql',
    query: async (sql, parameters = []) => (await pool.query(sql, parameters)).rows,
    async transaction(work) {
      const client = await pool.connect();
      try {
        await client.query('BEGIN');
        await client.query('SELECT pg_advisory_xact_lock($1)', [MUTATION_LOCK]);
        const connection = {
          query: async (sql, parameters = []) => (await client.query(sql, parameters)).rows,
        };
        const result = await work(connection);
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
}
