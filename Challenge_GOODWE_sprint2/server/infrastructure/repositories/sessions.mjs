import { insertRecord } from './insert-record.mjs';

const decode = (row) => row && { ...row, reasons: JSON.parse(row.reasons) };

export class SessionRepository {
  constructor(connection) {
    this.connection = connection;
  }

  async list(month, unit) {
    const parameters = [month];
    const filter = unit ? ' AND unit_id = $2' : '';
    if (unit) parameters.push(unit);
    return (
      await this.connection.query(
        `SELECT * FROM sessions WHERE billing_month = $1${filter} ORDER BY start_at DESC, id`,
        parameters,
      )
    ).map(decode);
  }

  async find(id) {
    return decode((await this.connection.query('SELECT * FROM sessions WHERE id = $1', [id]))[0]);
  }

  async overlaps(session) {
    return (
      (
        await this.connection.query(
          'SELECT id FROM sessions WHERE charger_id = $1 AND start_at < $2 AND end_at > $3',
          [session.charger_id, session.end_at, session.start_at],
        )
      ).length > 0
    );
  }

  async validated() {
    return (
      await this.connection.query(
        "SELECT * FROM sessions WHERE review_status IN ('clear', 'approved') AND energy_wh IS NOT NULL",
      )
    ).map(decode);
  }

  pending(month) {
    return this.connection.query(
      "SELECT id FROM sessions WHERE billing_month = $1 AND review_status = 'pending'",
      [month],
    );
  }

  billable(month, unit) {
    return this.connection.query(
      "SELECT id, energy_wh FROM sessions WHERE billing_month = $1 AND unit_id = $2 AND review_status IN ('clear', 'approved') AND energy_wh IS NOT NULL",
      [month, unit],
    );
  }

  create(session) {
    return insertRecord(this.connection, 'sessions', {
      ...session,
      reasons: JSON.stringify(session.reasons),
    });
  }
  updateReview(id, status) {
    return this.connection.query('UPDATE sessions SET review_status = $1 WHERE id = $2', [
      status,
      id,
    ]);
  }
}
