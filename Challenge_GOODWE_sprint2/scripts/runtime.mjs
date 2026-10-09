import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { spawn } from 'node:child_process';

export function python() {
  const local = resolve(
    '.venv',
    process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python',
  );
  return process.env.PYTHON || (existsSync(local) ? local : 'python');
}
export function run(command, args, options = {}) {
  const { env = process.env, ...rest } = options;
  const child = spawn(command, args, {
    stdio: 'inherit',
    windowsHide: true,
    ...rest,
    env: { ...env, PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' },
  });
  child.on('error', (error) => {
    console.error(error.message);
  });
  return child;
}
export async function waitFor(url, child) {
  for (let i = 0; i < 150; i++) {
    if (child?.exitCode != null) throw new Error('Um serviço encerrou antes de ficar disponível.');
    try {
      if ((await fetch(url, { signal: AbortSignal.timeout(1000) })).ok) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 200));
  }
  throw new Error(`Serviço não respondeu: ${url}`);
}
export function completion(child) {
  return new Promise((resolve, reject) => {
    child.once('exit', (code) => resolve(code ?? 1));
    child.once('error', reject);
  });
}
