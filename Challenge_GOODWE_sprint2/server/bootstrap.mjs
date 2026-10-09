import { randomUUID } from 'node:crypto';
import { SessionService } from './application/sessions.mjs';
import { BillingService } from './application/billing.mjs';
import { ForecastService } from './application/forecast.mjs';
import { DashboardService } from './application/dashboard.mjs';
import { initializeDemo } from './application/initialize-demo.mjs';
import { createStore } from './infrastructure/repositories/index.mjs';
import { createDemoDataset } from './infrastructure/demo/dataset.mjs';

export function createApplication(
  database,
  { intelligence, clock = () => new Date().toISOString(), idGenerator = randomUUID } = {},
) {
  if (!intelligence) throw new TypeError('Informe o serviço de inteligência da aplicação.');
  const store = createStore(database);
  const dependencies = { store, intelligence, clock, idGenerator };
  const metadata = Object.freeze({ mode: 'simulation', database: database.dialect });
  const sessions = new SessionService(dependencies);
  const billing = new BillingService(dependencies);
  return {
    metadata,
    intelligence,
    sessions,
    billing,
    catalog: { list: async () => ({ ...(await store.catalog.list()), ...metadata }) },
    dashboard: new DashboardService({ sessions, billing }),
    forecast: new ForecastService(dependencies),
    initializeDemo: () => initializeDemo(dependencies, createDemoDataset),
  };
}
