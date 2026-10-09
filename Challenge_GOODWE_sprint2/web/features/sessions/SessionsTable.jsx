import React from 'react';
import { date, number, energyNumber } from '../../shared/format.mjs';
import { Icon } from '../../shared/components/Icon.jsx';
import { Badge } from './SessionBadge.jsx';
export function SessionsTable({ sessions, onReview, small = false }) {
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
