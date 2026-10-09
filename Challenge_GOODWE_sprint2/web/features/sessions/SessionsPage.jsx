import React, { useState } from 'react';
import { Icon } from '../../shared/components/Icon.jsx';
import { PanelTitle } from '../../shared/components/PanelTitle.jsx';
import { SessionsTable } from './SessionsTable.jsx';
export function SessionsPage({
  sessions,
  dashboard,
  onReview,
  onImport,
  initialFilter = 'all',
  busy,
}) {
  const [filter, setFilter] = useState(initialFilter);
  const [search, setSearch] = useState('');
  const visible = sessions.filter(
    (session) =>
      (filter === 'all' || session.review_status === filter) &&
      (session.id + ' ' + session.unit_id).toLowerCase().includes(search.toLowerCase()),
  );
  return (
    <section className="panel">
      <PanelTitle
        title="Registro e validação"
        caption="Medições acumuladas, consumo calculado e análise de IA em cada importação."
        action={
          <label className="secondary file-button">
            <Icon type="download" size={17} /> Importar JSON
            <input
              type="file"
              disabled={busy}
              accept=".json,application/json"
              onChange={(e) => {
                const file = e.target.files[0];
                if (file) onImport(file);
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
      <SessionsTable sessions={visible} onReview={onReview} />
    </section>
  );
}
