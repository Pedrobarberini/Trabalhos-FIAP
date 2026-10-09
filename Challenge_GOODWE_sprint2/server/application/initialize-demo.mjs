import { normalizeBatch } from '../domain/session.mjs';
import { analyzeSessions } from './analyze-sessions.mjs';

export async function initializeDemo({ store, intelligence, clock }, datasetFactory) {
  await store.transaction(async (repositories) => {
    if (await repositories.catalog.hasUnits()) return;
    const { catalog, history, examples } = datasetFactory();
    await repositories.catalog.create(catalog);
    for (const session of history) await repositories.sessions.create(session);
    const candidates = normalizeBatch(examples, catalog);
    const result = await analyzeSessions(intelligence, history, candidates, clock());
    for (const session of result.sessions) {
      const approveReference = session.unit_id === '302' && session.review_status === 'pending';
      await repositories.sessions.create({
        ...session,
        review_status: approveReference ? 'approved' : session.review_status,
      });
      if (approveReference)
        await repositories.reviews.create({
          id: `SEED-REVIEW-${session.id}`,
          session_id: session.id,
          decision: 'approved',
          reason:
            'Cenário sintético de referência conferido: leituras de medidor e duração corretas.',
          created_at: clock(),
        });
    }
  });
}
