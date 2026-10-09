import { insertRecord } from './insert-record.mjs';

const TABLES = ['units', 'users', 'vehicles', 'chargers'];

export class CatalogRepository {
  constructor(connection) {
    this.connection = connection;
  }

  async list() {
    const rows = await Promise.all(
      TABLES.map((table) => this.connection.query(`SELECT * FROM ${table} ORDER BY id`)),
    );
    return Object.fromEntries(TABLES.map((table, index) => [table, rows[index]]));
  }

  async hasUnits() {
    return (await this.connection.query('SELECT id FROM units LIMIT 1')).length > 0;
  }

  units() {
    return this.connection.query('SELECT * FROM units ORDER BY id');
  }
  chargers() {
    return this.connection.query('SELECT * FROM chargers ORDER BY id');
  }

  async create(catalog) {
    for (const table of TABLES) {
      for (const record of catalog[table]) await insertRecord(this.connection, table, record);
    }
  }
}
