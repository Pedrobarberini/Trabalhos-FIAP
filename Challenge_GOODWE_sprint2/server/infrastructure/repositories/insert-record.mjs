const TABLES = new Set([
  'units',
  'users',
  'vehicles',
  'chargers',
  'sessions',
  'reviews',
  'invoices',
  'invoice_sessions',
]);

export async function insertRecord(connection, table, record) {
  if (!TABLES.has(table)) throw new Error('Tabela de persistência inválida.');
  const entries = Object.entries(record);
  const columns = entries.map(([column]) => column).join(',');
  const placeholders = entries.map((_, index) => `$${index + 1}`).join(',');
  await connection.query(
    `INSERT INTO ${table} (${columns}) VALUES (${placeholders})`,
    entries.map(([, value]) => value),
  );
}
