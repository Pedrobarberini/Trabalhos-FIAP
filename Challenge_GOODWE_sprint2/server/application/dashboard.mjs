export class DashboardService {
  constructor({ sessions, billing }) {
    this.sessions = sessions;
    this.billing = billing;
  }

  async summarize(month) {
    const [sessions, invoices] = await Promise.all([
      this.sessions.list(month),
      this.billing.list(month),
    ]);
    const eligible = sessions.filter((session) =>
      ['clear', 'approved'].includes(session.review_status),
    );
    const alerts = sessions.filter((session) => session.review_status === 'pending');
    return {
      month,
      sessions: sessions.length,
      energy_kwh: eligible.reduce((sum, session) => sum + (session.energy_wh || 0), 0) / 1000,
      pending: alerts.length,
      rejected: sessions.filter((session) => session.review_status === 'rejected').length,
      invoices: invoices.length,
      total_cents: invoices.reduce((sum, invoice) => sum + invoice.total_cents, 0),
      recent: sessions.slice(0, 5),
      alerts,
    };
  }
}
