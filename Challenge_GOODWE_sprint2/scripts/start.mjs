import { existsSync } from 'node:fs';
import { python, run, completion, waitFor } from './runtime.mjs';

const children = [];
function stop() {
  for (const child of children) child.kill();
}
for (const signal of ['SIGINT', 'SIGTERM'])
  process.on(signal, () => {
    stop();
    process.exit(0);
  });
try {
  if (!existsSync('dist/index.html')) {
    const code = await completion(
      run(process.execPath, ['node_modules/vite/bin/vite.js', 'build']),
    );
    if (code) process.exit(code);
  }
  if (!process.env.AI_URL) {
    const ai = run(python(), ['ai/service.py']);
    children.push(ai);
    await waitFor(`http://127.0.0.1:${process.env.AI_PORT || 8001}/health`, ai);
    process.env.AI_URL = `http://127.0.0.1:${process.env.AI_PORT || 8001}`;
  }
  const api = run(process.execPath, ['server/index.mjs']);
  children.push(api);
  process.exitCode = await completion(api);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
} finally {
  stop();
}
