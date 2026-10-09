import React from 'react';
import { nextDate } from '../../shared/format.mjs';
import { Icon } from '../../shared/components/Icon.jsx';
import { PanelTitle } from '../../shared/components/PanelTitle.jsx';
import { Forecast } from '../intelligence/ForecastChart.jsx';
export function IntelligencePage({ dashboard, forecast, forecastError, month, onReview }) {
  return (
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
            O modelo aprende com energia distribuída por hora. Os últimos 7 dias ficam separados
            para avaliar o erro antes do novo treino.
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
            Resultados com dados sintéticos. A previsão orienta planejamento; o protótipo não envia
            comandos ao carregador.
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
              <button className="secondary" onClick={() => onReview(s)}>
                Revisar
              </button>
            </div>
          ))
        ) : (
          <div className="empty">Nenhuma anomalia pendente neste mês.</div>
        )}
      </section>
    </>
  );
}
