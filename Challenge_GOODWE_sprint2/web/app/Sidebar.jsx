import React from 'react';
import { titles } from './navigation.mjs';
import { Icon } from '../shared/components/Icon.jsx';
export function Sidebar({ page, pending, onNavigate }) {
  return (
    <aside className="sidebar">
      <a
        className="brand"
        href="#"
        onClick={(e) => {
          e.preventDefault();
          onNavigate('overview');
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
              onNavigate(key);
            }}
          >
            <Icon type={key} />
            <span>{title}</span>
            {key === 'sessions' && pending > 0 && <b>{pending}</b>}
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
  );
}
