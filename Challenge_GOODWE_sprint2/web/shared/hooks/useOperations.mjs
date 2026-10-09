import { useEffect, useState, useCallback } from 'react';
import { chargeOpsApi } from '../api/client.mjs';

export function useOperations(month) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [revision, setRevision] = useState(0);
  const refresh = useCallback(() => setRevision((value) => value + 1), []);

  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setError('');
    chargeOpsApi
      .operations(month, controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) setData(result);
      })
      .catch((failure) => {
        if (!controller.signal.aborted) setError(failure.message);
      });
    return () => controller.abort();
  }, [month, revision]);

  return { data, error, refresh, revision };
}
