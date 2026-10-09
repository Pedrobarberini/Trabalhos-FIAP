import React from 'react';
import { titles } from './navigation.mjs';
import { Icon } from '../shared/components/Icon.jsx';
export function PageHeading({ page, month, setMonth, onRegister, ready }) {
  return (
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
        <button className="primary" onClick={onRegister} disabled={!ready}>
          <Icon type="plus" size={17} /> Nova sessão
        </button>
      </div>
    </div>
  );
}
