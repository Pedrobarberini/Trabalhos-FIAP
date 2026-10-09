import { ensure } from '../domain/errors.mjs';
import { monthValue, scaled } from '../domain/values.mjs';
import { consumptionCents } from '../domain/billing.mjs';

export class BillingService {
  constructor({ store, clock }) {
    this.store = store;
    this.clock = clock;
  }

  list(month, unit) {
    return this.store.invoices.list(monthValue(month), unit);
  }

  async generate({ month, tariff = '1.05', fixed_fee = '20.00' }) {
    monthValue(month);
    const tariffMillis = scaled(tariff, 1000, 'Tarifa por kWh', 100);
    const fixedCents = scaled(fixed_fee, 100, 'Taxa fixa', 10000);
    await this.store.transaction(async (repositories) => {
      const existing = await repositories.invoices.list(month);
      if (existing.length) {
        ensure(
          existing.every(
            (invoice) =>
              invoice.tariff_millis === tariffMillis && invoice.fixed_cents === fixedCents,
          ),
          'Faturas imutáveis: o mês já foi fechado com outra tarifa/taxa.',
          'conflict',
        );
        return;
      }
      const pending = await repositories.sessions.pending(month);
      ensure(
        !pending.length,
        `${pending.length} sessão(ões) aguardando revisão da IA. Revise antes de faturar.`,
        'conflict',
      );
      const units = await repositories.catalog.units();
      for (const unit of units) {
        const sessions = await repositories.sessions.billable(month, unit.id);
        const energyWh = sessions.reduce((sum, session) => sum + session.energy_wh, 0);
        const consumption = consumptionCents(energyWh, tariffMillis);
        const invoice = {
          id: `FAT-${month}-${unit.id}`,
          unit_id: unit.id,
          month,
          energy_wh: energyWh,
          tariff_millis: tariffMillis,
          fixed_cents: fixedCents,
          consumption_cents: consumption,
          total_cents: consumption + fixedCents,
          created_at: this.clock(),
        };
        await repositories.invoices.create(invoice);
        for (const session of sessions) await repositories.invoices.link(invoice.id, session.id);
      }
    });
    return this.list(month);
  }
}
