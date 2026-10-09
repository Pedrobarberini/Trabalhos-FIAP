import React from 'react';
import { brl, number, nextDate } from '../../shared/format.mjs';
import { Icon } from '../../shared/components/Icon.jsx';
import { Stat } from '../../shared/components/Stat.jsx';
import { PanelTitle } from '../../shared/components/PanelTitle.jsx';
import { Forecast } from '../intelligence/ForecastChart.jsx';
import { SessionsTable } from '../sessions/SessionsTable.jsx';
export function OverviewPage({
  dashboard,
  catalog,
  forecast,
  forecastError,
  month,
  onOpenSessions,
  onOpenInvoices,
}) {
  return (
    <>
      <section className="hero">
        <div>
          <span className="hero-label">
            <Icon size={15} /> RECARGA COMPARTILHADA, GESTÃO INTELIGENTE
          </span>
          <h2>
            Energia compartilhada.
            <br />
            <em>Contas individuais.</em>
          </h2>
          <p>
            Do registro à fatura, cada sessão passa por uma análise
            <br className="desktop" /> de IA para um rateio transparente por consumo.
          </p>
          <button onClick={onOpenInvoices}>
            Acompanhar o rateio <Icon type="arrow" size={18} />
          </button>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="orbit orbit-a" />
          <div className="orbit orbit-b" />
          <div className="big-bolt">
            <Icon size={96} />
          </div>
          <span className="art-chip">
            <i /> 2 pontos de recarga
          </span>
          <span className="art-kwh">
            kWh <small>→ dados → decisões</small>
          </span>
        </div>
      </section>
      <section className="stats">
        <Stat
          label="Consumo liberado"
          value={number(dashboard.energy_kwh)}
          suffix="kWh"
          icon="bolt"
          note={`${dashboard.sessions} sessões registradas`}
        />
        <Stat
          label="Valor faturado"
          value={brl(dashboard.total_cents)}
          icon="invoices"
          note={
            dashboard.invoices
              ? `${dashboard.invoices} faturas individuais`
              : 'Aguardando fechamento do mês'
          }
        />
        <Stat
          label="Carregadores cadastrados"
          value={catalog?.chargers.length || 0}
          suffix="pontos"
          icon="charger"
          note="14,4 kW de capacidade conjunta"
        />
        <Stat
          label="Sessões em revisão"
          value={dashboard.pending}
          suffix="alertas"
          icon="intelligence"
          note="Validação antes da cobrança"
          alert={dashboard.pending > 0}
        />
      </section>
      <div className="two-col">
        <section className="panel">
          <PanelTitle
            title="Demanda nas próximas 24 horas"
            caption={`Previsão para ${nextDate(month).split('-').reverse().join('/')}`}
            tag="IA · RANDOM FOREST"
          />
          <Forecast value={forecast} error={forecastError} />
        </section>
        <section className="panel insight">
          <span className="insight-icon">
            <Icon type="intelligence" size={25} />
          </span>
          <span className="eyebrow">INTELIGÊNCIA QUE AGE</span>
          <h3>
            Antes da cobrança,
            <br />
            uma segunda leitura.
          </h3>
          <p>
            O Isolation Forest analisa energia, duração e potência. Sessões suspeitas aguardam sua
            decisão.
          </p>
          <div className="insight-count">
            <b>{dashboard.pending}</b>
            <span>
              sessões aguardando
              <br />
              revisão do gestor
            </span>
          </div>
          <button className="secondary" onClick={() => onOpenSessions('pending')}>
            Analisar sessões <Icon type="arrow" size={17} />
          </button>
        </section>
      </div>
      <section className="panel">
        <PanelTitle
          title="Últimas sessões"
          caption="Registros rastreáveis, do carregador à unidade."
          action={
            <button className="text-button" onClick={() => onOpenSessions('all')}>
              Ver todas <Icon type="arrow" size={16} />
            </button>
          }
        />
        <SessionsTable sessions={dashboard.recent} small />
      </section>
    </>
  );
}
