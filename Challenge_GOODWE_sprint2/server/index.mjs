import { openDatabase } from './database.mjs';
import { ChargeOps } from './service.mjs';
import { seed } from './seed.mjs';
import { createHttpServer } from './http.mjs';

const db = await openDatabase();
const service = new ChargeOps(db);
await seed(service);
const server = createHttpServer(service);
const port = Number(process.env.PORT || 3000);
server.listen(port, process.env.HOST || '127.0.0.1', () =>
  console.log(`EV ChargeOps: http://localhost:${port}`),
);
for (const signal of ['SIGINT', 'SIGTERM'])
  process.on(signal, () =>
    server.close(async () => {
      await db.close();
      process.exit(0);
    }),
  );
