import { useRef, useState } from 'react';

export function useMutation() {
  const running = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  function clear() {
    setError('');
    setNotice('');
  }

  async function run(work, message) {
    if (running.current) return false;
    running.current = true;
    setBusy(true);
    clear();
    try {
      await work();
      setNotice(message);
      return true;
    } catch (failure) {
      setError(failure.message);
      return false;
    } finally {
      running.current = false;
      setBusy(false);
    }
  }
  return { busy, error, notice, run, clear };
}
