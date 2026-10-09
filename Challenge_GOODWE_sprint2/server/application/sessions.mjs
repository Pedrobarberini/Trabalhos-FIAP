import { ensure } from '../domain/errors.mjs';
import { normalizeBatch } from '../domain/session.mjs';
import { monthValue } from '../domain/values.mjs';
import { publicSession } from './presenters/session.mjs';
import { analyzeSessions } from './analyze-sessions.mjs';

export class SessionService {
  constructor({ store, intelligence, clock, idGenerator }) {
    Object.assign(this, { store, intelligence, clock, idGenerator });
  }

  async list(month, unit) {
    return (await this.store.sessions.list(monthValue(month), unit)).map(publicSession);
  }

  async register(inputs) {
    const candidates = normalizeBatch(inputs, await this.store.catalog.list());
    return this.store.transaction(async (repositories) => {
      for (const session of candidates) {
        ensure(
          !(await repositories.sessions.find(session.id)),
          `Sessão ${session.id} já registrada.`,
          'conflict',
        );
        ensure(
          !(await repositories.invoices.hasMonth(session.billing_month)),
          `Mês ${session.billing_month} já faturado; ingestão encerrada.`,
          'conflict',
        );
        ensure(
          !(await repositories.sessions.overlaps(session)),
          `Carregador ocupado no intervalo da sessão ${session.id}.`,
          'conflict',
        );
      }
      const history = await repositories.sessions.validated();
      const result = await analyzeSessions(this.intelligence, history, candidates, this.clock());
      for (const session of result.sessions) await repositories.sessions.create(session);
      return { ...result, sessions: result.sessions.map(publicSession) };
    });
  }

  async review(id, { decision, reason }) {
    ensure(['approved', 'rejected'].includes(decision), 'Decisão deve ser approved ou rejected.');
    ensure(
      typeof reason === 'string' && reason.trim().length >= 10 && reason.length <= 500,
      'Justifique a revisão com 10 a 500 caracteres.',
    );
    return this.store.transaction(async (repositories) => {
      const session = await repositories.sessions.find(id);
      ensure(session, 'Sessão não encontrada.', 'not_found');
      ensure(
        session.review_status === 'pending',
        'Somente sessões pendentes podem ser revisadas.',
        'conflict',
      );
      ensure(
        !(await repositories.invoices.hasMonth(session.billing_month)),
        'Mês já faturado.',
        'conflict',
      );
      ensure(
        decision !== 'approved' || session.energy_wh != null,
        'Sem medição válida: rejeite o registro e importe uma sessão corrigida com novo identificador.',
      );
      await repositories.reviews.create({
        id: this.idGenerator(),
        session_id: id,
        decision,
        reason: reason.trim(),
        created_at: this.clock(),
      });
      await repositories.sessions.updateReview(id, decision);
      return publicSession({ ...session, review_status: decision });
    });
  }

  reviews(id) {
    return this.store.reviews.list(id);
  }
}
