import { createServer } from 'node:net';
import { mkdirSync, writeFileSync } from 'node:fs';
import { python, run, waitFor, completion } from './runtime.mjs';

export async function freePort() {
  const server = createServer();
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  await new Promise((r) => server.close(r));
  return port;
}
const transcript = [];
function testProcess(command, args, options = {}) {
  const child = run(command, args, { ...options, stdio: ['ignore', 'pipe', 'pipe'] });
  for (const stream of [child.stdout, child.stderr])
    stream.on('data', (chunk) => {
      process.stdout.write(chunk);
      transcript.push(chunk.toString('utf8'));
    });
  return child;
}
const pythonCode = await completion(
  testProcess(python(), ['-m', 'unittest', 'discover', '-s', 'ai', '-p', 'test_*.py', '-v']),
);
if (pythonCode) process.exit(pythonCode);
const port = await freePort();
const ai = run(python(), ['ai/service.py'], { env: { ...process.env, AI_PORT: String(port) } });
try {
  await waitFor(`http://127.0.0.1:${port}/health`, ai);
  process.exitCode = await completion(
    testProcess(
      process.execPath,
      ['--test', '--test-concurrency=1', 'tests/domain.test.mjs', 'tests/integration.test.mjs'],
      {
        env: { ...process.env, AI_URL: `http://127.0.0.1:${port}` },
      },
    ),
  );
} catch (error) {
  console.error(error);
  process.exitCode = 1;
} finally {
  ai.kill();
  if (process.argv.includes('--report')) {
    mkdirSync('docs/evidence', { recursive: true });
    writeFileSync('docs/evidence/tests.txt', transcript.join(''));
  }
}
