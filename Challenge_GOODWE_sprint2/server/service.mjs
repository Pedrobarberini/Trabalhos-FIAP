import { randomUUID } from 'node:crypto';
import {
  assert,
  HttpError,
  normalizeSession,
  monthValue,
  scaled,
  consumptionCents,
  publicSession,
} from './domain.mjs';

export class ChargeOps {
  constructor(db, aiUrl = process.env.AI_URL || 'http://127.0.0.1:8001') {
    this.db = db;
    this.aiUrl = aiUrl;
  }
  async ai(endpoint, body) {
    let response;
    try {
      response = await fetch(`${this.aiUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(30000),
      });
    } catch {
      throw new HttpError(
        503,
        'Serviço de IA indisponível. Nenhuma sessão foi cobrada ou liberada automaticamente.',
      );
    }
    const payload = await response.json();
    if (!response.ok)
      throw new HttpError(
        response.status === 422 ? 422 : 503,
        payload.error || 'Falha no serviço de IA.',
      );
    return payload;
  }
  async catalog() {
    const [units, users, vehicles, chargers] = await Promise.all(
      ['units', 'users', 'vehicles', 'chargers'].map((table) =>
        this.db.query(`SELECT * FROM ${table} ORDER BY id`),
      ),
    );
    return { units, users, vehicles, chargers, mode: 'simulation', database: this.db.dialect };
  }
  async sessions(month, unit) {
    const values = [monthValue(month)];
    let sql = 'SELECT * FROM sessions WHERE billing_month = $1';
    if (unit) {
      sql += ' AND unit_id = $2';
      values.push(unit);
    }
    return (await this.db.query(`${sql} ORDER BY start_at DESC, id`, values)).map(publicSession);
  }
  async ingest(inputs) {
    assert(
      Array.isArray(inputs) && inputs.length > 0 && inputs.length <= 100,
      'Envie entre 1 e 100 sessões.',
    );
    const catalog = await this.catalog();
    const rows = inputs.map((input) =>
      normalizeSession(
        input,
        catalog.vehicles.find((v) => v.id === input?.vehicle_id),
        catalog.users.find((u) => u.id === input?.user_id),
        catalog.chargers.find((c) => c.id === input?.charger_id),
      ),
    );
    assert(
      new Set(rows.map((s) => s.id)).size === rows.length,
      'Lote contém identificadores duplicados.',
      409,
    );
    return this.db.transaction(async (tx) => {
      for (const row of rows) {
        assert(
          !(await tx.query('SELECT id FROM sessions WHERE id = $1', [row.id])).length,
          `Sessão ${row.id} já registrada.`,
          409,
        );
        assert(
          !(await tx.query('SELECT id FROM invoices WHERE month = $1', [row.billing_month])).length,
          `Mês ${row.billing_month} já faturado; ingestão encerrada.`,
          409,
        );
        const overlap = await tx.query(
          'SELECT id FROM sessions WHERE charger_id = $1 AND start_at < $2 AND end_at > $3',
          [row.charger_id, row.end_at, row.start_at],
        );
        assert(!overlap.length, `Carregador ocupado no intervalo da sessão ${row.id}.`, 409);
        assert(
          !rows.some(
            (other) =>
              other !== row &&
              other.charger_id === row.charger_id &&
              other.start_at < row.end_at &&
              other.end_at > row.start_at,
          ),
          'Lote contém sessões simultâneas no mesmo carregador.',
          409,
        );
      }
      const history = await tx.query(
        "SELECT * FROM sessions WHERE review_status IN ('clear', 'approved') AND energy_wh IS NOT NULL",
      );
      const analysis = await this.ai('/analyze', { history, candidates: rows });
      const inserted = [];
      for (const row of rows) {
        const result = analysis.results.find((item) => item.id === row.id);
        assert(
          result && ['clear', 'pending'].includes(result.review_status),
          'Resposta inválida do módulo de IA.',
          503,
        );
        const record = {
          ...row,
          review_status: result.review_status,
          reasons: JSON.stringify(result.reasons),
          anomaly_score: result.score,
          model_version: analysis.version,
          created_at: new Date().toISOString(),
        };
        await this.insert(tx, 'sessions', record);
        inserted.push(publicSession(record));
      }
      return {
        sessions: inserted,
        analysis: {
          model: analysis.model,
          version: analysis.version,
          training_samples: analysis.training_samples,
        },
      };
    });
  }
  async insert(tx, table, row) {
    const entries = Object.entries(row);
    await tx.query(
      `INSERT INTO ${table} (${entries.map(([key]) => key).join(',')}) VALUES (${entries.map((_, i) => `$${i + 1}`).join(',')})`,
      entries.map(([, value]) => value),
    );
  }
  async review(id, { decision, reason }) {
    assert(['approved', 'rejected'].includes(decision), 'Decisão deve ser approved ou rejected.');
    assert(
      typeof reason === 'string' && reason.trim().length >= 10 && reason.length <= 500,
      'Justifique a revisão com 10 a 500 caracteres.',
    );
    return this.db.transaction(async (tx) => {
      const [row] = await tx.query('SELECT * FROM sessions WHERE id = $1', [id]);
      assert(row, 'Sessão não encontrada.', 404);
      assert(
        row.review_status === 'pending',
        'Somente sessões pendentes podem ser revisadas.',
        409,
      );
      assert(
        !(await tx.query('SELECT id FROM invoices WHERE month = $1', [row.billing_month])).length,
        'Mês já faturado.',
        409,
      );
      assert(
        decision !== 'approved' || row.energy_wh != null,
        'Sem medição válida: rejeite o registro e importe uma sessão corrigida com novo identificador.',
      );
      await this.insert(tx, 'reviews', {
        id: randomUUID(),
        session_id: id,
        decision,
        reason: reason.trim(),
        created_at: new Date().toISOString(),
      });
      await tx.query('UPDATE sessions SET review_status = $1 WHERE id = $2', [decision, id]);
      return publicSession({ ...row, review_status: decision });
    });
  }
  async invoices(month, unit) {
    const args = [monthValue(month)];
    let sql = 'SELECT * FROM invoices WHERE month = $1';
    if (unit) {
      sql += ' AND unit_id = $2';
      args.push(unit);
    }
    const invoices = await this.db.query(`${sql} ORDER BY unit_id`, args);
    for (const invoice of invoices)
      invoice.session_ids = (
        await this.db.query(
          'SELECT session_id FROM invoice_sessions WHERE invoice_id = $1 ORDER BY session_id',
          [invoice.id],
        )
      ).map((s) => s.session_id);
    return invoices;
  }
  async generateInvoices({ month, tariff = '1.05', fixed_fee = '20.00' }) {
    monthValue(month);
    const tariffMillis = scaled(tariff, 1000, 'Tarifa por kWh', 100);
    const fixedCents = scaled(fixed_fee, 100, 'Taxa fixa', 10000);
    await this.db.transaction(async (tx) => {
      const existing = await tx.query('SELECT * FROM invoices WHERE month = $1', [month]);
      if (existing.length) {
        assert(
          existing.every((i) => i.tariff_millis === tariffMillis && i.fixed_cents === fixedCents),
          'Faturas imutáveis: o mês já foi fechado com outra tarifa/taxa.',
          409,
        );
        return;
      }
      const pending = await tx.query(
        "SELECT id FROM sessions WHERE billing_month = $1 AND review_status = 'pending'",
        [month],
      );
      assert(
        !pending.length,
        `${pending.length} sessão(ões) aguardando revisão da IA. Revise antes de faturar.`,
        409,
      );
      const units = await tx.query('SELECT * FROM units ORDER BY id');
      for (const unit of units) {
        const sessions = await tx.query(
          "SELECT id, energy_wh FROM sessions WHERE billing_month = $1 AND unit_id = $2 AND review_status IN ('clear', 'approved') AND energy_wh IS NOT NULL",
          [month, unit.id],
        );
        const energyWh = sessions.reduce((sum, s) => sum + s.energy_wh, 0);
        const cents = consumptionCents(energyWh, tariffMillis);
        const invoice = {
          id: `FAT-${month}-${unit.id}`,
          unit_id: unit.id,
          month,
          energy_wh: energyWh,
          tariff_millis: tariffMillis,
          fixed_cents: fixedCents,
          consumption_cents: cents,
          total_cents: cents + fixedCents,
          created_at: new Date().toISOString(),
        };
        await this.insert(tx, 'invoices', invoice);
        for (const session of sessions)
          await this.insert(tx, 'invoice_sessions', {
            invoice_id: invoice.id,
            session_id: session.id,
          });
      }
    });
    return this.invoices(month);
  }
  async forecast(date) {
    assert(
      typeof date === 'string' && /^20\d{2}-\d{2}-\d{2}$/.test(date),
      'Data inválida. Use AAAA-MM-DD.',
    );
    const history = await this.db.query(
      "SELECT * FROM sessions WHERE review_status IN ('clear', 'approved') AND energy_wh IS NOT NULL",
    );
    const chargers = await this.db.query('SELECT max_kw FROM chargers');
    return this.ai('/forecast', {
      history,
      date,
      capacity_kw: chargers.reduce((sum, c) => sum + c.max_kw, 0),
    });
  }
  async dashboard(month) {
    const sessions = await this.sessions(month);
    const invoices = await this.invoices(month);
    const eligible = sessions.filter((s) => ['clear', 'approved'].includes(s.review_status));
    return {
      month,
      sessions: sessions.length,
      energy_kwh: eligible.reduce((sum, s) => sum + (s.energy_wh || 0), 0) / 1000,
      pending: sessions.filter((s) => s.review_status === 'pending').length,
      rejected: sessions.filter((s) => s.review_status === 'rejected').length,
      invoices: invoices.length,
      total_cents: invoices.reduce((sum, i) => sum + i.total_cents, 0),
      recent: sessions.slice(0, 5),
      alerts: sessions.filter((s) => s.review_status === 'pending'),
    };
  }
}
