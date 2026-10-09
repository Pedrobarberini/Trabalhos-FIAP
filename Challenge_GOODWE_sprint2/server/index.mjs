import { loadConfig } from './config.mjs';
import { openDatabase } from './infrastructure/database/index.mjs';
import { IntelligenceClient } from './infrastructure/intelligence/client.mjs';
import { createApplication } from './bootstrap.mjs';
import { createHttpServer } from './presentation/http/server.mjs';

const config = loadConfig();
const database = await openDatabase(config.database);
try {
  const app = createApplication(database, {
    intelligence: new IntelligenceClient(config.intelligence),
  });
  await app.initializeDemo();
  const server = createHttpServer(app);
  server.listen(config.port, config.host, () =>
    console.log(`EV ChargeOps: http://localhost:${config.port}`),
  );
  let closing = false;
  async function stop() {
    if (closing) return;
    closing = true;
    server.closeAllConnections();
    await new Promise((resolve) => server.close(resolve));
    await database.close();
  }
  for (const signal of ['SIGINT', 'SIGTERM'])
    process.once(signal, () => stop().then(() => process.exit(0)));
  server.once('error', async (error) => {
    console.error(error.message);
    await stop();
    process.exitCode = 1;
  });
} catch (error) {
  await database.close();
  throw error;
}
