import React from 'react';

export function Badge({ status }) {
  return (
    <span className={`badge ${status}`}>
      {{ clear: 'Liberada', approved: 'Revisada', pending: 'Em revisão', rejected: 'Excluída' }[
        status
      ] || status}
    </span>
  );
}
