import React, { useState } from 'react';
import { brl, number, energyNumber } from '../../shared/format.mjs';
import { Icon } from '../../shared/components/Icon.jsx';
import { PanelTitle } from '../../shared/components/PanelTitle.jsx';
import { chargeOpsApi } from '../../shared/api/client.mjs';
export function InvoicesPage({ invoices, dashboard, month, busy, onGenerate, onOpenSessions }) {
  const [tariff, setTariff] = useState('1.05');
  const [fee, setFee] = useState('20.00');
  return (
    <>
      <section className="panel billing-config">
        <div>
          <span className="eyebrow">RATEIO POR CONSUMO EFETIVO</span>
          <h3>Uma regra simples. Uma conta justa.</h3>
          <p>Consumo da unidade × tarifa por kWh + taxa fixa.</p>
          <small>O fechamento preserva as faturas e encerra a ingestão deste mês.</small>
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onGenerate({ month, tariff, fixed_fee: fee });
          }}
        >
          <label>
            Tarifa (R$/kWh)
            <input
              aria-label="Tarifa por kWh"
              type="number"
              min="0"
              max="100"
              step="0.001"
              required
              value={tariff}
              onChange={(e) => setTariff(e.target.value)}
            />
          </label>
          <label>
            Taxa fixa (R$)
            <input
              aria-label="Taxa fixa"
              type="number"
              min="0"
              max="10000"
              step="0.01"
              required
              value={fee}
              onChange={(e) => setFee(e.target.value)}
            />
          </label>
          <button className="primary" disabled={busy}>
            <Icon type="invoices" size={17} />
            {busy ? 'Processando…' : 'Gerar faturas'}
          </button>
        </form>
      </section>
      {dashboard.pending > 0 && (
        <div className="message warning">
          <Icon type="alert" />
          <span>
            <strong>{dashboard.pending} sessões impedem o fechamento.</strong> Revise ou exclua os
            registros suspeitos antes de gerar as faturas.
          </span>
          <button className="text-button" onClick={() => onOpenSessions('pending')}>
            Revisar <Icon type="arrow" size={16} />
          </button>
        </div>
      )}
      <section className="panel">
        <PanelTitle
          title="Faturas por unidade"
          caption="Valores em reais, arredondados uma vez sobre o consumo mensal."
          action={
            <a className="secondary" href={chargeOpsApi.invoiceExport(month)}>
              <Icon type="download" size={17} /> Exportar CSV
            </a>
          }
        />
        {!invoices.length ? (
          <div className="empty">
            <Icon type="invoices" size={32} />
            <h3>Pronto para fechar o mês?</h3>
            <p>Resolva as pendências e gere as faturas para conferir o rateio.</p>
          </div>
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Unidade</th>
                  <th>Sessões</th>
                  <th>Consumo</th>
                  <th>Energia</th>
                  <th>Taxa fixa</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((i) => (
                  <tr key={i.id}>
                    <td>
                      <strong>Apto {i.unit_id}</strong>
                      <span className="sub">{i.id}</span>
                    </td>
                    <td>{i.session_ids.length}</td>
                    <td>{energyNumber(i.energy_wh / 1000)} kWh</td>
                    <td>{brl(i.consumption_cents)}</td>
                    <td>{brl(i.fixed_cents)}</td>
                    <td>
                      <strong className="green-text">{brl(i.total_cents)}</strong>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <div className="footnote">
        A taxa fixa é opcional e deve ser aprovada pelo condomínio. Unidade sem recarga não paga
        consumo variável; a taxa configurada se aplica a todas as unidades.
      </div>
    </>
  );
}
