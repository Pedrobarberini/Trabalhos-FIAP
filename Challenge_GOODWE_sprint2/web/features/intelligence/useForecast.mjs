import { useEffect, useState } from 'react';
import { chargeOpsApi } from '../../shared/api/client.mjs';
import { nextDate } from '../../shared/format.mjs';

export function useForecast(month, revision) {
  const [forecast, setForecast] = useState(null);
  const [forecastError, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    setForecast(null);
    setError('');
    chargeOpsApi
      .forecast(nextDate(month), controller.signal)
      .then((result) => {
        if (!controller.signal.aborted) setForecast(result);
      })
      .catch((failure) => {
        if (!controller.signal.aborted) setError(failure.message);
      });
    return () => controller.abort();
  }, [month, revision]);
  return { forecast, forecastError };
}
