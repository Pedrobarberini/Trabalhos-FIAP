import React from 'react';
import { Icon } from './Icon.jsx';

export function Notification({ message, type = 'error', onClose }) {
  if (!message) return null;
  return (
    <div className={`message ${type}`} role={type === 'error' ? 'alert' : 'status'}>
      <Icon type={type === 'error' ? 'alert' : 'check'} />
      <span>{message}</span>
      {onClose && (
        <button aria-label={type === 'error' ? 'Fechar erro' : 'Fechar mensagem'} onClick={onClose}>
          <Icon type="close" size={16} />
        </button>
      )}
    </div>
  );
}
