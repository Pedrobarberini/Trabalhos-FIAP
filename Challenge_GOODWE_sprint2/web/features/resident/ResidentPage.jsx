import React, { useState } from 'react';
import { brl, energyNumber } from '../../shared/format.mjs';
import { Stat } from '../../shared/components/Stat.jsx';
import { PanelTitle } from '../../shared/components/PanelTitle.jsx';
import { SessionsTable } from '../sessions/SessionsTable.jsx';
export function ResidentPage({ catalog, sessions, invoices }) {
  const [unit, setUnit] = useState('302');
  const own = sessions.filter((session) => session.unit_id === unit);
  const ownInvoice = invoices.find((invoice) => invoice.unit_id === unit);
  const ownEnergy =
    own
      .filter((session) => ['clear', 'approved'].includes(session.review_status))
      .reduce((sum, session) => sum + (session.energy_wh || 0), 0) / 1000;
  return (
    <>
      <div className="resident-intro">
        <div>
          <span className="eyebrow">SEU CONSUMO, COM CLAREZA</span>
          <h2>Olá, {catalog?.users.find((u) => u.unit_id === unit)?.name.split(' ')[0]}.</h2>
          <p>As recargas de todos os veículos da unidade aparecem juntas.</p>
        </div>
        <label>
          Unidade demonstrativa
          <select
            aria-label="Unidade do morador"
            value={unit}
            onChange={(e) => setUnit(e.target.value)}
          >
            {catalog?.units.map((u) => (
              <option key={u.id} value={u.id}>
                {u.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <section className="stats resident-stats">
        <Stat
          label="Meu consumo liberado"
          value={energyNumber(ownEnergy)}
          suffix="kWh"
          icon="bolt"
          note={`${own.length} sessões no mês`}
        />
        <Stat
          label="Minha fatura"
          value={ownInvoice ? brl(ownInvoice.total_cents) : 'Em aberto'}
          icon="invoices"
          note={
            ownInvoice
              ? `Energia ${brl(ownInvoice.consumption_cents)} + taxa ${brl(ownInvoice.fixed_cents)}`
              : 'Disponível após o fechamento do gestor'
          }
        />
        <Stat
          label="Sessões pendentes"
          value={own.filter((s) => s.review_status === 'pending').length}
          icon="clock"
          note="Aguardando conferência do gestor"
        />
      </section>
      <section className="panel">
        <PanelTitle
          title="Meu histórico de recargas"
          caption="Consumo calculado pela diferença entre as leituras válidas do medidor."
        />
        <SessionsTable sessions={own} small />
      </section>
      <div className="footnote">
        Este seletor demonstra a visão do morador. Login e controle de acesso por perfil são
        evoluções para produção.
      </div>
    </>
  );
}
