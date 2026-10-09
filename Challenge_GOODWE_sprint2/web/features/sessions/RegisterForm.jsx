import React, { useState } from 'react';
import { sessionInput } from './session-input.mjs';

export function RegisterForm({ catalog, month, busy, onSubmit, error }) {
  const [unit, setUnit] = useState('302');
  const [status, setStatus] = useState('completed');
  const [sessionId] = useState(() => `MANUAL-${Date.now()}`);
  const user = catalog?.users.find((u) => u.unit_id === unit);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const form = Object.fromEntries(new FormData(e.currentTarget));
        onSubmit(sessionInput(form, { unitId: unit, userId: user.id, status }));
      }}
    >
      <span className="eyebrow">NOVA RECARGA · DADOS SIMULADOS</span>
      <h2>Da sessão ao dado.</h2>
      <p>Informe leituras acumuladas em kWh. A IA analisa o registro antes da cobrança.</p>
      <div className="form-grid">
        <label>
          Identificador
          <input name="id" required defaultValue={sessionId} pattern="[A-Za-z0-9_-]{1,80}" />
        </label>
        <label>
          Unidade
          <select value={unit} onChange={(e) => setUnit(e.target.value)}>
            {catalog?.units.map((u) => (
              <option key={u.id} value={u.id}>
                {u.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Veículo
          <select name="vehicle_id" key={unit}>
            {catalog?.vehicles
              .filter((v) => v.user_id === user?.id)
              .map((v) => (
                <option key={v.id} value={v.id}>
                  {v.label}
                </option>
              ))}
          </select>
        </label>
        <label>
          Carregador
          <select name="charger_id">
            {catalog?.chargers.map((c) => (
              <option key={c.id} value={c.id}>
                {c.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Início (Brasília)
          <input
            name="start_at"
            type="datetime-local"
            required
            defaultValue={`${month}-28T05:00`}
          />
        </label>
        <label>
          Fim (Brasília)
          <input name="end_at" type="datetime-local" required defaultValue={`${month}-28T06:00`} />
        </label>
        <label>
          Medidor inicial (kWh)
          <input
            name="start_meter_kwh"
            type="number"
            min="0"
            max="1000000"
            step="0.001"
            required
            defaultValue="100"
          />
        </label>
        <label>
          {status === 'interrupted' ? 'Última leitura válida (kWh)' : 'Medidor final (kWh)'}
          <input
            name="end_meter_kwh"
            type="number"
            min="0"
            max="1000000"
            step="0.001"
            defaultValue="105.2"
          />
        </label>
      </div>
      <label>
        Status
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="completed">Concluída</option>
          <option value="interrupted">Interrompida</option>
        </select>
      </label>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      <button className="primary full" disabled={busy}>
        {busy ? 'Analisando com IA…' : 'Registrar e analisar com IA'}
      </button>
    </form>
  );
}
