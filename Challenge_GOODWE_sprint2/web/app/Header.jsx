import React from 'react';
import { titles } from './navigation.mjs';
export function Header({ page }) {
  return (
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
  );
}
