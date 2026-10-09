import { insertRecord } from './insert-record.mjs';

export class InvoiceRepository {
  constructor(connection) {
    this.connection = connection;
  }

  async list(month, unit) {
    const parameters = [month];
    const filter = unit ? ' AND unit_id = $2' : '';
    if (unit) parameters.push(unit);
    const invoices = await this.connection.query(
      `SELECT * FROM invoices WHERE month = $1${filter} ORDER BY unit_id`,
      parameters,
    );
    const links = await this.connection.query(
      `SELECT invoice_sessions.invoice_id, invoice_sessions.session_id FROM invoice_sessions JOIN invoices ON invoices.id = invoice_sessions.invoice_id WHERE invoices.month = $1${unit ? ' AND invoices.unit_id = $2' : ''} ORDER BY invoice_sessions.session_id`,
      parameters,
    );
    const sessionIds = new Map(invoices.map((invoice) => [invoice.id, []]));
    for (const link of links) sessionIds.get(link.invoice_id)?.push(link.session_id);
    return invoices.map((invoice) => ({ ...invoice, session_ids: sessionIds.get(invoice.id) }));
  }

  async hasMonth(month) {
    return (
      (await this.connection.query('SELECT id FROM invoices WHERE month = $1 LIMIT 1', [month]))
        .length > 0
    );
  }

  create(invoice) {
    return insertRecord(this.connection, 'invoices', invoice);
  }
  link(invoiceId, sessionId) {
    return insertRecord(this.connection, 'invoice_sessions', {
      invoice_id: invoiceId,
      session_id: sessionId,
    });
  }
}
