# Contrato HTTP e dados

Base local: `http://localhost:3000/api`. Datas de entrada usam ISO 8601 com fuso obrigatório. Datas persistidas estão em UTC; competência e interface usam Brasília.

| Método | Rota | Finalidade |
| --- | --- | --- |
| GET | `/health` | Estado da API, banco e modo demonstrativo |
| GET | `/catalog` | Unidades, usuários, veículos e carregadores cadastrados |
| GET | `/dashboard?month=2026-09` | Totais, sessões recentes e pendências |
| GET | `/sessions?month=2026-09&unit=302` | Sessões; `unit` opcional |
| POST | `/sessions` | Registrar uma sessão e executar a análise de IA |
| POST | `/import` | Registrar lote `{ "sessions": [...] }`, de 1 a 100 registros |
| POST | `/sessions/ID/review` | Revisar sessão pendente |
| GET | `/sessions/ID/reviews` | Trilha de auditoria das decisões |
| GET | `/forecast?date=2026-10-01` | Previsão de 24 horas e métricas temporais |
| POST | `/invoices` | Fechar competência e gerar faturas imutáveis |
| GET | `/invoices?month=2026-09&unit=302` | Faturas com sessões de origem; `unit` opcional |
| GET | `/invoices.csv?month=2026-09&unit=302` | Exportar valores das faturas em CSV UTF-8 |

## Registrar sessão

```json
{
  "id": "IMPORT-001",
  "source": "sems-import",
  "user_id": "U302",
  "unit_id": "302",
  "vehicle_id": "V302",
  "charger_id": "HCA01",
  "start_at": "2026-09-28T05:00:00-03:00",
  "end_at": "2026-09-28T06:00:00-03:00",
  "status": "completed",
  "start_meter_kwh": 100,
  "end_meter_kwh": 105.2
}
```

Para `interrupted`, envie `last_valid_meter_kwh` em vez de `end_meter_kwh`. A ausência dessa leitura é permitida para registrar a falha, mas exige revisão e impede a aprovação/cobrança. Números podem ser strings com ponto decimal. Leituras aceitam três casas decimais, máximo de 1.000.000 kWh, sem valores negativos. A duração deve estar entre zero (exclusivo) e sete dias. O usuário, veículo e unidade precisam estar associados no catálogo.

`source` representa a origem declarada do arquivo. `sems-import` **não significa conexão verificada com a GoodWe**. O contrato acima é interno ao protótipo. A conversão de um payload real SEMS+ é uma etapa futura.

Resposta 201 inclui `sessions` com `energy_wh`, `energy_kwh`, `average_kw`, `duration_minutes`, `billing_month`, `review_status`, `reasons`, `anomaly_score` e `model_version`; `analysis` informa técnica, versão e tamanho do histórico de treino. Um lote com qualquer conflito é recusado integralmente.

## Revisar e faturar

```json
{ "decision": "rejected", "reason": "Leitura inconsistente conferida e excluída do faturamento." }
```

Decisões: `approved` ou `rejected`; justificativa de 10 a 500 caracteres. Somente `pending` pode ser revisada. Ausência de energia válida impede aprovação. Histórico de revisão e dados originais são mantidos.

```json
{ "month": "2026-09", "tariff": "1.05", "fixed_fee": "20.00" }
```

Tarifa aceita até três casas decimais, entre R$ 0 e R$ 100/kWh. Taxa fixa aceita duas casas decimais, entre R$ 0 e R$ 10.000. A omissão usa R$ 1,05 e R$ 20,00, parâmetros apenas demonstrativos. Para cobrança exclusivamente por consumo, informe `fixed_fee: "0.00"`.

Faturas retornam `energy_wh`, `tariff_millis`, `fixed_cents`, `consumption_cents`, `total_cents` e `session_ids`. A taxa é aplicada uma vez por unidade, incluindo as sem consumo. Depois do fechamento, novas sessões da competência não são aceitas.

## Erros e limites

Erros têm formato `{ "error": "mensagem" }`. Códigos: 400 (JSON inválido), 403 (origem de mutação externa), 404 (recurso/rota inexistente), 409 (duplicidade, sobreposição, pendências ou competência fechada), 413 (payload acima de 1 MB), 422 (regra ou dados inválidos), 503 (IA indisponível). IDs usam letras, números, `_` e `-`, até 80 caracteres.

O filtro `unit` é uma ferramenta de demonstração, **não uma autorização de acesso**. Nenhuma autenticação está habilitada neste protótipo local.

## Serviço Python interno

`GET /health`, `POST /analyze` e `POST /forecast` em `127.0.0.1:8001`. A API Node envia histórico, candidatos e data ao serviço. Este endpoint não precisa ser acessado pelo navegador. A versão lógica é `chargeops-1.0-seed42`; as dependências estão fixadas em `ai/requirements.txt`.
