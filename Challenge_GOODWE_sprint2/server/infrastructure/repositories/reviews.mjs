import { insertRecord } from './insert-record.mjs';

export class ReviewRepository {
  constructor(connection) {
    this.connection = connection;
  }
  list(sessionId) {
    return this.connection.query(
      'SELECT * FROM reviews WHERE session_id = $1 ORDER BY created_at',
      [sessionId],
    );
  }
  create(review) {
    return insertRecord(this.connection, 'reviews', review);
  }
}
