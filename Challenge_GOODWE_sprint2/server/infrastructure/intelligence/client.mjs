import { ApplicationError, ensure } from '../../domain/errors.mjs';

export class IntelligenceClient {
  constructor({ url, timeoutMs = 30000, fetcher = fetch }) {
    this.url = url;
    this.timeoutMs = timeoutMs;
    this.fetcher = fetcher;
  }

  async request(endpoint, body) {
    let response, payload;
    try {
      response = await this.fetcher(`${this.url}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(this.timeoutMs),
      });
      payload = await response.json();
    } catch (cause) {
      throw new ApplicationError(
        'service_unavailable',
        'Serviço de IA indisponível. Nenhuma sessão foi cobrada ou liberada automaticamente.',
        { cause },
      );
    }
    if (!response.ok)
      throw new ApplicationError(
        response.status === 422 ? 'validation' : 'service_unavailable',
        payload?.error || 'Falha no serviço de IA.',
      );
    return payload;
  }

  async analyze(history, candidates) {
    const analysis = await this.request('/analyze', { history, candidates });
    const valid =
      analysis &&
      typeof analysis.version === 'string' &&
      typeof analysis.model === 'string' &&
      Number.isInteger(analysis.training_samples) &&
      analysis.training_samples >= 0 &&
      Array.isArray(analysis.results) &&
      analysis.results.length === candidates.length;
    ensure(valid, 'Resposta inválida do módulo de IA.', 'service_unavailable');
    const ids = new Set();
    for (const result of analysis.results) {
      ensure(
        result &&
          candidates.some((candidate) => candidate.id === result.id) &&
          !ids.has(result.id) &&
          ['clear', 'pending'].includes(result.review_status) &&
          Array.isArray(result.reasons) &&
          result.reasons.every((reason) => typeof reason === 'string') &&
          (result.score === null || Number.isFinite(result.score)),
        'Resposta inválida do módulo de IA.',
        'service_unavailable',
      );
      ids.add(result.id);
    }
    return analysis;
  }

  async forecast(history, date, capacityKw) {
    const prediction = await this.request('/forecast', { history, date, capacity_kw: capacityKw });
    const valid =
      prediction &&
      prediction.date === date &&
      typeof prediction.model === 'string' &&
      typeof prediction.version === 'string' &&
      typeof prediction.recommendation === 'string' &&
      Number.isFinite(prediction.peak_kw) &&
      prediction.peak_kw >= 0 &&
      Number.isInteger(prediction.peak_hour) &&
      prediction.peak_hour >= 0 &&
      prediction.peak_hour < 24 &&
      Array.isArray(prediction.hours) &&
      prediction.hours.length === 24 &&
      new Set(prediction.hours.map((hour) => hour?.hour)).size === 24 &&
      prediction.hours.every(
        (hour) =>
          hour &&
          Number.isInteger(hour.hour) &&
          hour.hour >= 0 &&
          hour.hour < 24 &&
          Number.isFinite(hour.expected_kw) &&
          hour.expected_kw >= 0,
      );
    ensure(valid, 'Resposta inválida do módulo de previsão.', 'service_unavailable');
    return prediction;
  }
}
