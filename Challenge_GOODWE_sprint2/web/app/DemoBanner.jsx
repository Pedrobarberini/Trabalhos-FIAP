import React from 'react';
export function DemoBanner({ catalog }) {
  return (
    <div className="demo-bar">
      <span>
        <i className="dot amber" /> Dados sintéticos · sem conexão com carregador físico ou SEMS+
      </span>
      <span>
        {catalog?.database === 'postgresql' ? 'PostgreSQL' : 'SQLite local'} · horário de Brasília
      </span>
    </div>
  );
}
