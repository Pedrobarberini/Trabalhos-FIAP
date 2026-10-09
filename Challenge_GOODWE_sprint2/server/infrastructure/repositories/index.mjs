import { CatalogRepository } from './catalog.mjs';
import { SessionRepository } from './sessions.mjs';
import { InvoiceRepository } from './invoices.mjs';
import { ReviewRepository } from './reviews.mjs';

export function createRepositories(connection) {
  return {
    catalog: new CatalogRepository(connection),
    sessions: new SessionRepository(connection),
    invoices: new InvoiceRepository(connection),
    reviews: new ReviewRepository(connection),
  };
}

export function createStore(database) {
  return {
    ...createRepositories(database),
    transaction: (work) =>
      database.transaction((connection) => work(createRepositories(connection))),
  };
}
