import React, { useState } from 'react';

export function ReviewForm({ session, busy, onSubmit, error }) {
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
