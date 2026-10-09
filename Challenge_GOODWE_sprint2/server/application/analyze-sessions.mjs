export async function analyzeSessions(intelligence, history, candidates, now) {
  const analysis = await intelligence.analyze(history, candidates);
  const results = new Map(analysis.results.map((result) => [result.id, result]));
  const sessions = candidates.map((candidate) => {
    const result = results.get(candidate.id);
    const reasons = [...new Set([...candidate.reasons, ...result.reasons])];
    return {
      ...candidate,
      reasons,
      review_status: reasons.length ? 'pending' : result.review_status,
      anomaly_score: result.score,
      model_version: analysis.version,
      created_at: now,
    };
  });
  return {
    sessions,
    analysis: {
      model: analysis.model,
      version: analysis.version,
      training_samples: analysis.training_samples,
    },
  };
}
