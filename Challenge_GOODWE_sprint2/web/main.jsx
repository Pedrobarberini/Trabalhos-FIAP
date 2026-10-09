import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const brl = (cents) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100);
const number = (n) => new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format(n);
const energyNumber = (n) => new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 3 }).format(n);
const date = (value) =>
  new Intl.DateTimeFormat('pt-BR', {
    timeZone: 'America/Sao_Paulo',
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
const nextDate = (month) => {
  const dt = new Date(`${month}-01T12:00:00Z`);
  dt.setUTCMonth(dt.getUTCMonth() + 1);
  return dt.toISOString().slice(0, 10);
};
const titles = {
  overview: 'Visão geral',
  sessions: 'Sessões de recarga',
  invoices: 'Rateio e faturas',
  intelligence: 'Inteligência operacional',
  resident: 'Portal do morador',
};
async function api(path, body) {
  const response = await fetch(
    `/api${path}`,
    body
      ? {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        }
      : {},
  );
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Falha ao carregar dados.');
  return result;
}
function Icon({ type = 'bolt', size = 20 }) {
  const paths = {
    bolt: 'm13 2-9 12h7l-1 8 10-12h-7l1-8Z',
    overview: 'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z',
    sessions: 'M7 3v4m10-4v4M4 10h16M5 5h14a1 1 0 0 1 1 1v14H4V6a1 1 0 0 1 1-1Zm3 9h3m3 0h2m-8 3h3',
    invoices: 'M6 3h12v19l-3-2-3 2-3-2-3 2V3Zm3 5h6m-6 4h6m-6 4h3',
    intelligence: 'm12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z',
    resident: 'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Zm-13 14v-2a9 9 0 0 1 18 0v2',
    arrow: 'M5 12h14m-5-5 5 5-5 5',
    plus: 'M12 5v14M5 12h14',
    check: 'm5 12 4 4L19 6',
    close: 'm6 6 12 12M6 18 18 6',
    download: 'M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4',
    clock: 'M12 8v4l3 2M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z',
    alert: 'm12 3 10 18H2L12 3Zm0 6v5m0 3v1',
    charger:
      'M5 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16M3 21h14M8 6h4v5H8zM15 10h3v7a2 2 0 0 0 4 0V7l-3-3',
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[type] || paths.bolt} />
    </svg>
  );
}
function Badge({ status }) {
  return (
    <span className={`badge ${status}`}>
      {{ clear: 'Liberada', approved: 'Revisada', pending: 'Em revisão', rejected: 'Excluída' }[
        status
      ] || status}
    </span>
  );
}
function Forecast({ value, error }) {
  if (!value)
    return <div className="empty">{error || 'Calculando previsão com o histórico validado…'}</div>;
  const max = Math.max(value.capacity_kw, ...value.hours.map((h) => h.expected_kw), 1);
  const points = value.hours
    .map((h, i) => `${35 + i * 24},${170 - (h.expected_kw / max) * 135}`)
    .join(' ');
  return (
    <>
      <div className="chart-meta">
        <span>
          <i className="dot green" /> Demanda prevista
        </span>
        <span>
          <i className="dot pale" /> Capacidade: {number(value.capacity_kw)} kW
        </span>
        <span className="peak">
          Pico às {value.peak_hour}h · {number(value.peak_kw)} kW
        </span>
      </div>
      <svg
        className="chart"
        viewBox="0 0 622 208"
        role="img"
        aria-label={`Previsão para ${value.date}. Pico de ${value.peak_kw} kW às ${value.peak_hour} horas.`}
      >
        <defs>
          <linearGradient id="area" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#bedc74" stopOpacity=".55" />
            <stop offset="100%" stopColor="#bedc74" stopOpacity=".04" />
          </linearGradient>
        </defs>
        {[0, 0.5, 1].map((f) => (
          <g key={f}>
            <line
              x1="32"
              x2="602"
              y1={170 - f * 135}
              y2={170 - f * 135}
              stroke="#e8ebe2"
              strokeDasharray={f === 1 ? '5 5' : ''}
            />
            <text x="0" y={174 - f * 135}>
              {number(max * f)}
            </text>
          </g>
        ))}
        <polygon points={`35,170 ${points} 587,170`} fill="url(#area)" />
        <polyline
          points={points}
          fill="none"
          stroke="#49774a"
          strokeWidth="3"
          strokeLinejoin="round"
        />
        {value.hours.map((h, i) => (
          <circle
            key={i}
            cx={35 + i * 24}
            cy={170 - (h.expected_kw / max) * 135}
            r="3"
            fill="#49774a"
          >
            <title>
              {h.hour}h: {number(h.expected_kw)} kW
            </title>
          </circle>
        ))}
        {[0, 6, 12, 18, 23].map((h) => (
          <text key={h} x={35 + h * 24} y="198" textAnchor="middle">
            {String(h).padStart(2, '0')}:00
          </text>
        ))}
      </svg>
      <div className="chart-note">
        <Icon type="intelligence" size={17} />
        <span>{value.recommendation}</span>
      </div>
    </>
  );
}
function SessionsTable({ sessions, onReview, small = false }) {
  if (!sessions.length) return <div className="empty">Nenhuma sessão neste filtro.</div>;
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Sessão / unidade</th>
            <th>Encerramento</th>
            <th>Consumo</th>
            {!small && <th>Duração</th>}
            <th>Validação</th>
            {!small && <th>Ação</th>}
          </tr>
        </thead>
        <tbody>
          {sessions.map((s) => (
            <tr key={s.id}>
              <td>
                <strong>{s.id}</strong>
                <span className="sub">
                  Apto {s.unit_id} · {s.charger_id}
                  {s.status === 'interrupted' ? ' · Interrompida' : ''}
                </span>
              </td>
              <td>{date(s.end_at)}</td>
              <td>
                <strong>
                  {s.energy_kwh == null ? 'Sem leitura' : `${energyNumber(s.energy_kwh)} kWh`}
                </strong>
              </td>
              {!small && <td>{number(s.duration_minutes)} min</td>}
              <td>
                <Badge status={s.review_status} />
              </td>
              {!small && (
                <td>
                  {s.review_status === 'pending' ? (
                    <button className="text-button" onClick={() => onReview(s)}>
                      Revisar <Icon type="arrow" size={15} />
                    </button>
                  ) : (
                    <span className="muted">—</span>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
function App() {
  const [page, setPage] = useState('overview');
  const [month, setMonth] = useState('2026-09');
  const [catalog, setCatalog] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [forecastError, setForecastError] = useState('');
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [unit, setUnit] = useState('302');
  const [modal, setModal] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const [tariff, setTariff] = useState('1.05');
  const [fee, setFee] = useState('20.00');
  function showModal(value) {
    setError('');
    setNotice('');
    setModal(value);
  }
  async function load() {
    const [c, d, s, i] = await Promise.all([
      api('/catalog'),
      api(`/dashboard?month=${month}`),
      api(`/sessions?month=${month}`),
      api(`/invoices?month=${month}`),
    ]);
    setCatalog(c);
    setDashboard(d);
    setSessions(s);
    setInvoices(i);
  }
  useEffect(() => {
    load().catch((e) => setError(e.message));
  }, [month]);
  useEffect(() => {
    let active = true;
    setForecast(null);
    setForecastError('');
    api(`/forecast?date=${nextDate(month)}`)
      .then((f) => {
        if (active) setForecast(f);
      })
      .catch((e) => {
        if (active) setForecastError(e.message);
      });
    return () => {
      active = false;
    };
  }, [month, sessions]);
  async function action(task, message) {
    setBusy(true);
    setError('');
    setNotice('');
    try {
      await task();
      await load();
      setModal(null);
      setNotice(message);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  const visible = sessions.filter(
    (s) =>
      (filter === 'all' || s.review_status === filter) &&
      `${s.id} ${s.unit_id}`.toLowerCase().includes(search.toLowerCase()),
  );
  const own = sessions.filter((s) => s.unit_id === unit);
  const ownInvoice = invoices.find((i) => i.unit_id === unit);
  const ownEnergy = own
    .filter((s) => ['clear', 'approved'].includes(s.review_status))
    .reduce((sum, s) => sum + (s.energy_kwh || 0), 0);
  return (
    <div className="app">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setPage('overview');
          }}
        >
          <span className="brand-mark">
            <Icon size={25} />
          </span>
          <span>
            ChargeOps<small>ENERGIA EM EQUILÍBRIO</small>
          </span>
        </a>
        <div className="workspace">
          <span className="workspace-icon">A</span>
          <div>
            Condomínio Aurora<small>Ambiente de demonstração</small>
          </div>
          <span className="workspace-arrow">⌄</span>
        </div>
        <span className="nav-label">OPERAÇÃO</span>
        <nav>
          {Object.entries(titles).map(([key, title]) => (
            <button
              key={key}
              aria-label={title}
              title={title}
              className={page === key ? 'active' : ''}
              onClick={() => {
                setPage(key);
                setError('');
              }}
            >
              <Icon type={key} />
              <span>{title}</span>
              {key === 'sessions' && dashboard?.pending > 0 && <b>{dashboard.pending}</b>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="lab-label">FIAP × GoodWe</div>
          <p>De sessões de recarga a decisões mais inteligentes.</p>
          <span className="sprint-tag">SPRINT 02 · PROTÓTIPO</span>
        </div>
        <div className="profile">
          <span>GC</span>
          <div>
            Gestor do condomínio<small>Acesso demonstrativo</small>
          </div>
        </div>
      </aside>
      <main>
        <header>
          <div className="breadcrumb">
            Operação <span>/</span> <strong>{titles[page]}</strong>
          </div>
          <div className="header-right">
            <span className="live">
              <i /> IA no fluxo de validação
            </span>
            <span className="avatar">GC</span>
          </div>
        </header>
        <div className="content">
          <div className="page-title">
            <div>
              <div className="eyebrow">EV CHARGEOPS / GOODWE HCA G2</div>
              <h1>{titles[page]}</h1>
              <p>
                {page === 'resident'
                  ? 'Cada recarga, cada kWh e cada valor em um só lugar.'
                  : 'Acompanhe a energia. Entenda o consumo. Feche a conta com clareza.'}
              </p>
            </div>
            <div className="page-actions">
              <label className="month-label">
                Período
                <input
                  aria-label="Mês de referência"
                  type="month"
                  value={month}
                  onChange={(e) => e.target.value && setMonth(e.target.value)}
                />
              </label>
              <button className="primary" onClick={() => showModal({ type: 'register' })}>
                <Icon type="plus" size={17} /> Nova sessão
              </button>
            </div>
          </div>
          <div className="demo-bar">
            <span>
              <i className="dot amber" /> Dados sintéticos · sem conexão com carregador físico ou
              SEMS+
            </span>
            <span>
              {catalog?.database === 'postgresql' ? 'PostgreSQL' : 'SQLite local'} · horário de
              Brasília
            </span>
          </div>
          {error && (
            <div className="message error" role="alert">
              <Icon type="alert" />
              <span>{error}</span>
              <button aria-label="Fechar erro" onClick={() => setError('')}>
                <Icon type="close" size={16} />
              </button>
            </div>
          )}
          {notice && (
            <div className="message success" role="status">
              <Icon type="check" />
              <span>{notice}</span>
              <button aria-label="Fechar mensagem" onClick={() => setNotice('')}>
                <Icon type="close" size={16} />
              </button>
            </div>
          )}
          {!dashboard ? (
            <div className="panel empty">Carregando a operação…</div>
          ) : (
            <>
              {page === 'overview' && (
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
                      <button onClick={() => setPage('invoices')}>
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
                        O Isolation Forest analisa energia, duração e potência. Sessões suspeitas
                        aguardam sua decisão.
                      </p>
                      <div className="insight-count">
                        <b>{dashboard.pending}</b>
                        <span>
                          sessões aguardando
                          <br />
                          revisão do gestor
                        </span>
                      </div>
                      <button
                        className="secondary"
                        onClick={() => {
                          setFilter('pending');
                          setPage('sessions');
                        }}
                      >
                        Analisar sessões <Icon type="arrow" size={17} />
                      </button>
                    </section>
                  </div>
                  <section className="panel">
                    <PanelTitle
                      title="Últimas sessões"
                      caption="Registros rastreáveis, do carregador à unidade."
                      action={
                        <button
                          className="text-button"
                          onClick={() => {
                            setFilter('all');
                            setPage('sessions');
                          }}
                        >
                          Ver todas <Icon type="arrow" size={16} />
                        </button>
                      }
                    />
                    <SessionsTable sessions={dashboard.recent} small />
                  </section>
                </>
              )}
              {page === 'sessions' && (
                <section className="panel">
                  <PanelTitle
                    title="Registro e validação"
                    caption="Medições acumuladas, consumo calculado e análise de IA em cada importação."
                    action={
                      <label className="secondary file-button">
                        <Icon type="download" size={17} /> Importar JSON
                        <input
                          type="file"
                          accept=".json,application/json"
                          onChange={(e) => {
                            const file = e.target.files[0];
                            if (file)
                              action(
                                async () => api('/import', JSON.parse(await file.text())),
                                'Lote importado e analisado pela IA.',
                              );
                            e.target.value = '';
                          }}
                        />
                      </label>
                    }
                  />
                  <div className="toolbar">
                    <div className="filters">
                      {[
                        ['all', 'Todas'],
                        ['pending', `Em revisão (${dashboard.pending})`],
                        ['clear', 'Liberadas'],
                        ['approved', 'Revisadas'],
                        ['rejected', 'Excluídas'],
                      ].map(([key, title]) => (
                        <button
                          key={key}
                          className={filter === key ? 'selected' : ''}
                          onClick={() => setFilter(key)}
                        >
                          {title}
                        </button>
                      ))}
                    </div>
                    <input
                      className="search"
                      aria-label="Buscar sessão ou unidade"
                      placeholder="Buscar sessão ou unidade"
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </div>
                  <SessionsTable
                    sessions={visible}
                    onReview={(s) => showModal({ type: 'review', session: s })}
                  />
                </section>
              )}
              {page === 'invoices' && (
                <>
                  <section className="panel billing-config">
                    <div>
                      <span className="eyebrow">RATEIO POR CONSUMO EFETIVO</span>
                      <h3>Uma regra simples. Uma conta justa.</h3>
                      <p>Consumo da unidade × tarifa por kWh + taxa fixa.</p>
                      <small>
                        O fechamento preserva as faturas e encerra a ingestão deste mês.
                      </small>
                    </div>
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        action(
                          () => api('/invoices', { month, tariff, fixed_fee: fee }),
                          'Mês fechado. Faturas individuais geradas e preservadas.',
                        );
                      }}
                    >
                      <label>
                        Tarifa (R$/kWh)
                        <input
                          aria-label="Tarifa por kWh"
                          type="number"
                          min="0"
                          max="100"
                          step="0.001"
                          required
                          value={tariff}
                          onChange={(e) => setTariff(e.target.value)}
                        />
                      </label>
                      <label>
                        Taxa fixa (R$)
                        <input
                          aria-label="Taxa fixa"
                          type="number"
                          min="0"
                          max="10000"
                          step="0.01"
                          required
                          value={fee}
                          onChange={(e) => setFee(e.target.value)}
                        />
                      </label>
                      <button className="primary" disabled={busy}>
                        <Icon type="invoices" size={17} />
                        {busy ? 'Processando…' : 'Gerar faturas'}
                      </button>
                    </form>
                  </section>
                  {dashboard.pending > 0 && (
                    <div className="message warning">
                      <Icon type="alert" />
                      <span>
                        <strong>{dashboard.pending} sessões impedem o fechamento.</strong> Revise ou
                        exclua os registros suspeitos antes de gerar as faturas.
                      </span>
                      <button
                        className="text-button"
                        onClick={() => {
                          setFilter('pending');
                          setPage('sessions');
                        }}
                      >
                        Revisar <Icon type="arrow" size={16} />
                      </button>
                    </div>
                  )}
                  <section className="panel">
                    <PanelTitle
                      title="Faturas por unidade"
                      caption="Valores em reais, arredondados uma vez sobre o consumo mensal."
                      action={
                        <a className="secondary" href={`/api/invoices.csv?month=${month}`}>
                          <Icon type="download" size={17} /> Exportar CSV
                        </a>
                      }
                    />
                    {!invoices.length ? (
                      <div className="empty">
                        <Icon type="invoices" size={32} />
                        <h3>Pronto para fechar o mês?</h3>
                        <p>Resolva as pendências e gere as faturas para conferir o rateio.</p>
                      </div>
                    ) : (
                      <div className="table-scroll">
                        <table>
                          <thead>
                            <tr>
                              <th>Unidade</th>
                              <th>Sessões</th>
                              <th>Consumo</th>
                              <th>Energia</th>
                              <th>Taxa fixa</th>
                              <th>Total</th>
                            </tr>
                          </thead>
                          <tbody>
                            {invoices.map((i) => (
                              <tr key={i.id}>
                                <td>
                                  <strong>Apto {i.unit_id}</strong>
                                  <span className="sub">{i.id}</span>
                                </td>
                                <td>{i.session_ids.length}</td>
                                <td>{energyNumber(i.energy_wh / 1000)} kWh</td>
                                <td>{brl(i.consumption_cents)}</td>
                                <td>{brl(i.fixed_cents)}</td>
                                <td>
                                  <strong className="green-text">{brl(i.total_cents)}</strong>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </section>
                  <div className="footnote">
                    A taxa fixa é opcional e deve ser aprovada pelo condomínio. Unidade sem recarga
                    não paga consumo variável; a taxa configurada se aplica a todas as unidades.
                  </div>
                </>
              )}
              {page === 'intelligence' && (
                <>
                  <div className="two-col">
                    <section className="panel">
                      <PanelTitle
                        title="Previsão de demanda"
                        caption={`Dia previsto: ${nextDate(month).split('-').reverse().join('/')}`}
                        tag="RANDOM FOREST"
                      />
                      <Forecast value={forecast} error={forecastError} />
                    </section>
                    <section className="panel model-card">
                      <span className="eyebrow">AVALIAÇÃO CRONOLÓGICA</span>
                      <h3>Prever com transparência.</h3>
                      <p>
                        O modelo aprende com energia distribuída por hora. Os últimos 7 dias ficam
                        separados para avaliar o erro antes do novo treino.
                      </p>
                      <dl>
                        <div>
                          <dt>Histórico utilizado</dt>
                          <dd>{forecast?.training_days ?? '—'} dias</dd>
                        </div>
                        <div>
                          <dt>Erro médio do modelo</dt>
                          <dd>{forecast?.validation_mae_kw ?? '—'} kW</dd>
                        </div>
                        <div>
                          <dt>Erro da média histórica</dt>
                          <dd>{forecast?.baseline_mae_kw ?? '—'} kW</dd>
                        </div>
                      </dl>
                      <small>
                        Resultados com dados sintéticos. A previsão orienta planejamento; o
                        protótipo não envia comandos ao carregador.
                      </small>
                    </section>
                  </div>
                  <section className="panel">
                    <PanelTitle
                      title="Anomalias que exigem decisão"
                      caption="Isolation Forest + validação física de potência e integridade das leituras."
                    />
                    {dashboard.alerts.length ? (
                      dashboard.alerts.map((s) => (
                        <div className="alert-row" key={s.id}>
                          <span className="alert-symbol">
                            <Icon type="alert" />
                          </span>
                          <div>
                            <strong>
                              {s.id} · Apto {s.unit_id}
                            </strong>
                            <p>{s.reasons.join(' ')}</p>
                            <small>
                              Modelo: {s.model_version} · Score:{' '}
                              {s.anomaly_score == null ? 'sem leitura' : s.anomaly_score.toFixed(3)}
                            </small>
                          </div>
                          <button
                            className="secondary"
                            onClick={() => showModal({ type: 'review', session: s })}
                          >
                            Revisar
                          </button>
                        </div>
                      ))
                    ) : (
                      <div className="empty">Nenhuma anomalia pendente neste mês.</div>
                    )}
                  </section>
                </>
              )}
              {page === 'resident' && (
                <>
                  <div className="resident-intro">
                    <div>
                      <span className="eyebrow">SEU CONSUMO, COM CLAREZA</span>
                      <h2>
                        Olá, {catalog?.users.find((u) => u.unit_id === unit)?.name.split(' ')[0]}.
                      </h2>
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
                    Este seletor demonstra a visão do morador. Login e controle de acesso por perfil
                    são evoluções para produção.
                  </div>
                </>
              )}
            </>
          )}
          <footer>
            <span>
              EV ChargeOps <b>·</b> FIAP Enterprise Challenge 2026
            </span>
            <span>Consumo medido. Rateio justo. Decisões informadas.</span>
          </footer>
        </div>
      </main>
      {modal && (
        <div
          className="modal-backdrop"
          onClick={(e) => {
            if (e.target === e.currentTarget && !busy) setModal(null);
          }}
        >
          <section
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label={modal.type === 'review' ? 'Revisar sessão' : 'Registrar sessão'}
          >
            <button
              className="modal-close"
              aria-label="Fechar janela"
              disabled={busy}
              onClick={() => setModal(null)}
            >
              <Icon type="close" />
            </button>
            {modal.type === 'review' ? (
              <ReviewForm
                session={modal.session}
                busy={busy}
                onSubmit={(data) =>
                  action(
                    () => api(`/sessions/${modal.session.id}/review`, data),
                    'Revisão registrada com justificativa.',
                  )
                }
                error={error}
              />
            ) : (
              <RegisterForm
                catalog={catalog}
                month={month}
                busy={busy}
                onSubmit={(data) =>
                  action(
                    () => api('/sessions', data),
                    'Sessão registrada, normalizada e analisada pela IA.',
                  )
                }
                error={error}
              />
            )}
          </section>
        </div>
      )}
    </div>
  );
}
function Stat({ label, value, suffix, icon, note, alert }) {
  return (
    <div className={`stat ${alert ? 'stat-alert' : ''}`}>
      <div className="stat-top">
        <span>{label}</span>
        <Icon type={icon} size={19} />
      </div>
      <div className="stat-value">
        {value} <small>{suffix}</small>
      </div>
      <div className="stat-note">{note}</div>
    </div>
  );
}
function PanelTitle({ title, caption, action, tag }) {
  return (
    <div className="panel-title">
      <div>
        <h3>{title}</h3>
        {caption && <p>{caption}</p>}
      </div>
      {action}
      {tag && <span className="model-tag">{tag}</span>}
    </div>
  );
}
function ReviewForm({ session, busy, onSubmit, error }) {
  const [decision, setDecision] = useState('rejected');
  const [reason, setReason] = useState('');
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ decision, reason });
      }}
    >
      <span className="eyebrow">REVISÃO DO GESTOR</span>
      <h2>Conferir antes de cobrar.</h2>
      <p>
        {session.id} · Apto {session.unit_id}
      </p>
      <div className="review-reasons">
        {session.reasons.map((r, i) => (
          <p key={i}>{r}</p>
        ))}
      </div>
      <label>
        Decisão
        <select value={decision} onChange={(e) => setDecision(e.target.value)}>
          <option value="rejected">Excluir do faturamento</option>
          <option value="approved" disabled={session.energy_wh == null}>
            Aprovar medição após conferência
          </option>
        </select>
      </label>
      <label>
        Justificativa
        <textarea
          autoFocus
          required
          minLength="10"
          maxLength="500"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Descreva a conferência realizada (mínimo 10 caracteres)"
        />
      </label>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      <button className="primary full" disabled={busy}>
        {busy ? 'Salvando…' : 'Registrar decisão'}
      </button>
    </form>
  );
}
function RegisterForm({ catalog, month, busy, onSubmit, error }) {
  const [unit, setUnit] = useState('302');
  const [status, setStatus] = useState('completed');
  const user = catalog?.users.find((u) => u.unit_id === unit);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const form = Object.fromEntries(new FormData(e.currentTarget));
        const end = form.end_meter_kwh;
        delete form.end_meter_kwh;
        onSubmit({
          ...form,
          unit_id: unit,
          user_id: user.id,
          status,
          start_at: `${form.start_at}:00-03:00`,
          end_at: `${form.end_at}:00-03:00`,
          ...(end === ''
            ? {}
            : status === 'interrupted'
              ? { last_valid_meter_kwh: end }
              : { end_meter_kwh: end }),
        });
      }}
    >
      <span className="eyebrow">NOVA RECARGA · DADOS SIMULADOS</span>
      <h2>Da sessão ao dado.</h2>
      <p>Informe leituras acumuladas em kWh. A IA analisa o registro antes da cobrança.</p>
      <div className="form-grid">
        <label>
          Identificador
          <input
            name="id"
            required
            defaultValue={`MANUAL-${Date.now()}`}
            pattern="[A-Za-z0-9_-]{1,80}"
          />
        </label>
        <label>
          Unidade
          <select value={unit} onChange={(e) => setUnit(e.target.value)}>
            {catalog?.units.map((u) => (
              <option key={u.id} value={u.id}>
                {u.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Veículo
          <select name="vehicle_id" key={unit}>
            {catalog?.vehicles
              .filter((v) => v.user_id === user?.id)
              .map((v) => (
                <option key={v.id} value={v.id}>
                  {v.label}
                </option>
              ))}
          </select>
        </label>
        <label>
          Carregador
          <select name="charger_id">
            {catalog?.chargers.map((c) => (
              <option key={c.id} value={c.id}>
                {c.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Início (Brasília)
          <input
            name="start_at"
            type="datetime-local"
            required
            defaultValue={`${month}-28T05:00`}
          />
        </label>
        <label>
          Fim (Brasília)
          <input name="end_at" type="datetime-local" required defaultValue={`${month}-28T06:00`} />
        </label>
        <label>
          Medidor inicial (kWh)
          <input
            name="start_meter_kwh"
            type="number"
            min="0"
            max="1000000"
            step="0.001"
            required
            defaultValue="100"
          />
        </label>
        <label>
          {status === 'interrupted' ? 'Última leitura válida (kWh)' : 'Medidor final (kWh)'}
          <input
            name="end_meter_kwh"
            type="number"
            min="0"
            max="1000000"
            step="0.001"
            defaultValue="105.2"
          />
        </label>
      </div>
      <label>
        Status
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="completed">Concluída</option>
          <option value="interrupted">Interrompida</option>
        </select>
      </label>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      <button className="primary full" disabled={busy}>
        {busy ? 'Analisando com IA…' : 'Registrar e analisar com IA'}
      </button>
    </form>
  );
}

createRoot(document.getElementById('root')).render(<App />);
