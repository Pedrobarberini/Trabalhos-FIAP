import { ensure } from '../domain/errors.mjs';

export class ForecastService {
  constructor({ store, intelligence }) {
    this.store = store;
    this.intelligence = intelligence;
  }

  async predict(date) {
    ensure(
      typeof date === 'string' && /^20\d{2}-\d{2}-\d{2}$/.test(date),
      'Data inválida. Use AAAA-MM-DD.',
    );
    const [history, chargers] = await Promise.all([
      this.store.sessions.validated(),
      this.store.catalog.chargers(),
    ]);
    return this.intelligence.forecast(
      history,
      date,
      chargers.reduce((sum, charger) => sum + charger.max_kw, 0),
    );
  }
}
