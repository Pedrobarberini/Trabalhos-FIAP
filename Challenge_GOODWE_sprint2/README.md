# EV ChargeOps - Challenge GoodWe | Sprint 2

Protótipo funcional para organizar sessões de recarga compartilhadas, calcular consumo individual, aplicar rateio por unidade e apoiar a gestão com inteligência artificial.

A aplicação oferece cadastro e importação de sessões, validação de medições, revisão de anomalias, fechamento mensal, exportação CSV, previsão horária de demanda e portal demonstrativo do morador. **Os dados são sintéticos; a aplicação não está conectada ao carregador físico ou ao SEMS+.**

## Evidências da aplicação funcionando

Validação realizada em **20/10/2026**, com **Node.js v24.19.0**, serviço Python executado localmente e **SQLite em memória**. O cenário utiliza o mesmo servidor HTTP, as regras de negócio e os modelos da aplicação. O banco de uso local é preservado.

| Verificação executada           | Resultado observado                                                                            | Registro                                                                                                              |
| ------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Compilação da interface React   | Vite concluiu o build, com 51 módulos transformados                                            | [Saída do build](docs/evidencias/build.txt)                                                                           |
| Testes automatizados            | **35 testes Node.js + 5 testes Python aprovados**, sem falhas                                  | [Saída dos testes](docs/evidencias/testes.txt)                                                                        |
| Estado inicial de setembro/2026 | **184 sessões**, 2 pendências e 2.398,832 kWh liberados                                        | [Execução HTTP](docs/evidencias/execucao.json), campo `initial_dashboard`                                             |
| Cadastro de recarga             | HTTP **201**; medidor de 100 para 105,2 kWh gerou **5.200 Wh / 5,2 kWh**, com versão do modelo | [Execução HTTP](docs/evidencias/execucao.json), requisição `POST /api/sessions`                                       |
| Reenvio do mesmo registro       | HTTP **409**, sem duplicação da sessão                                                         | [Execução HTTP](docs/evidencias/execucao.json), segunda requisição `POST /api/sessions`                               |
| Fechamento com pendências       | HTTP **409**, exigindo revisão antes da cobrança                                               | [Execução HTTP](docs/evidencias/execucao.json), primeira requisição `POST /api/invoices`                              |
| Revisão do gestor               | Decisões com justificativa registradas; auditoria consultada pela API                          | [Execução HTTP](docs/evidencias/execucao.json), rotas `/review` e `/reviews`                                          |
| Fatura da unidade 302           | Dois veículos, **60 kWh**, R$ 63,00 de energia + R$ 20,00 de taxa = **R$ 83,00**               | [Faturas exportadas](docs/evidencias/faturas.csv) e campo `unit_302_invoice` do [JSON](docs/evidencias/execucao.json) |
| Unidade 999 sem recarga         | Consumo variável zero e taxa configurada de R$ 20,00                                           | [Faturas exportadas](docs/evidencias/faturas.csv)                                                                     |
| Repetição do fechamento         | As mesmas faturas foram retornadas, sem nova cobrança                                          | [Execução HTTP](docs/evidencias/execucao.json), segunda requisição de fechamento bem-sucedida                         |
| Consulta do morador             | Filtro da unidade 302 retornou apenas suas duas sessões                                        | [Execução HTTP](docs/evidencias/execucao.json), `GET /api/sessions?month=2026-09&unit=302`                            |
| Estado final                    | **185 sessões**, nenhuma pendência e **6 faturas**; total de R$ 2.644,23                       | [Execução HTTP](docs/evidencias/execucao.json), campo `final_dashboard`                                               |

### Evidência da inteligência artificial

O serviço Python executou **Isolation Forest** na ingestão de sessões e **Random Forest Regressor** na previsão de demanda. No cenário de validação, a previsão de 01/10/2026 retornou:

| Indicador                                 | Resultado                |
| ----------------------------------------- | ------------------------ |
| Histórico utilizado                       | 61 dias                  |
| Horas previstas                           | 24                       |
| Pico previsto                             | **18h**, com **11,1 kW** |
| Capacidade cadastrada                     | 14,4 kW                  |
| MAE do modelo na validação temporal       | 1,249 kW                 |
| MAE da média histórica na mesma validação | 1,243 kW                 |

A média histórica teve erro ligeiramente menor nessa amostra. Os valores são apresentados para comparação, sem afirmar que o modelo supera a referência. A previsão orienta o planejamento; o faturamento utiliza medições válidas.

As respostas completas, os corpos das requisições, os códigos HTTP esperados e observados e as verificações realizadas estão em [execucao.json](docs/evidencias/execucao.json). O arquivo foi gerado pelo [script de evidências](scripts/evidence.mjs), que interrompe a execução se uma verificação falhar.

### Reproduzir as evidências

Depois de instalar as dependências conforme as instruções abaixo:

```bash
npx --yes pnpm@11.25.0 run evidence
```

Esse comando compila a interface, executa os 40 testes e inicia temporariamente a API e a IA em portas locais disponíveis. Em seguida, cria o cenário com banco em memória, executa o fluxo HTTP e gera:

- `docs/evidencias/build.txt`: saída real da compilação e código de saída.
- `docs/evidencias/testes.txt`: saída real dos testes Node.js e Python.
- `docs/evidencias/execucao.json`: respostas da API, previsão, fatura e verificações do fluxo.
- `docs/evidencias/faturas.csv`: exportação das seis faturas desse cenário.

Ao terminar, os serviços temporários e o banco em memória são encerrados. A nova sessão de 5,2 kWh pertence à unidade 501; por isso, o exemplo de 60 kWh da unidade 302 permanece inalterado. Se a IA sinalizar essa sessão sintética, o script registra uma aprovação justificada após conferir suas leituras. Os exemplos inconsistentes `DEMO-ANOMALIA` e `DEMO-SEM-LEITURA` são rejeitados com justificativa para demonstrar o fechamento.

## Tecnologias e arquitetura

| Parte                    | Implementação                                   |
| ------------------------ | ----------------------------------------------- |
| Interface                | React 19, JavaScript/JSX, HTML e CSS responsivo |
| Compilação               | Vite 7                                          |
| API e coordenação        | Node.js 24+, HTTP e JSON                        |
| Inteligência artificial  | Python 3.12, scikit-learn e NumPy               |
| Persistência local       | SQLite, com `node:sqlite`                       |
| Persistência alternativa | PostgreSQL, configurado por `DATABASE_URL`      |
| Infraestrutura opcional  | Docker e Docker Compose                         |
| Testes                   | `node:test` e `unittest`                        |

O backend separa **domínio**, **aplicação**, **infraestrutura** e **apresentação HTTP**. O frontend está organizado por funcionalidades, componentes compartilhados e hooks. Os adaptadores de banco e IA são fornecidos aos serviços na inicialização.

```text
Interface React
    | HTTP / JSON
API Node.js
    |-- Regras de sessões, revisão e faturamento
    |-- Repositórios -> SQLite ou PostgreSQL
    `-- Serviço Python -> análise de anomalias e previsão
```

## Executar localmente

Pré-requisitos: **Node.js 24 ou superior**, npm/npx e **Python 3.12**. Os comandos usam a versão de pnpm definida no projeto, sem exigir uma instalação global desse gerenciador.

### Windows PowerShell

Execute a partir da raiz deste repositório:

```powershell
cd Challenge_GOODWE_sprint2
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ai/requirements.txt
npx --yes pnpm@11.25.0 install --frozen-lockfile
npx --yes pnpm@11.25.0 run build
npx --yes pnpm@11.25.0 start
```

### Linux/macOS

```bash
cd Challenge_GOODWE_sprint2
python3 -m venv .venv
.venv/bin/python -m pip install -r ai/requirements.txt
npx --yes pnpm@11.25.0 install --frozen-lockfile
npx --yes pnpm@11.25.0 run build
npx --yes pnpm@11.25.0 start
```

Acesse **http://localhost:3000**. O script inicia o serviço Python em `127.0.0.1:8001` e a aplicação Node.js em `127.0.0.1:3000`. O Python do ambiente `.venv` é identificado automaticamente. Use `Ctrl+C` para encerrar os serviços.

O banco local é criado em `data/chargeops.sqlite` na primeira execução. A aplicação o preenche apenas quando o catálogo está vazio. Alterações posteriores ficam salvas nesse banco; por isso, os totais da sua tela podem diferir do cenário isolado das evidências. Após editar o frontend, execute novamente `run build` antes de iniciar a aplicação.

### Configuração opcional

O arquivo `.env` é opcional. Para personalizar a execução, copie [.env.example](.env.example) para `.env` e ajuste as variáveis necessárias:

| Variável       | Uso e padrão                                                                   |
| -------------- | ------------------------------------------------------------------------------ |
| `PORT`         | Porta da aplicação; padrão `3000`                                              |
| `AI_PORT`      | Porta do serviço Python local; padrão `8001`                                   |
| `DB_PATH`      | Arquivo SQLite; padrão `data/chargeops.sqlite`                                 |
| `DATABASE_URL` | Quando preenchida, seleciona PostgreSQL                                        |
| `AI_URL`       | Endereço de um serviço Python já iniciado; evita iniciar outro automaticamente |
| `PYTHON`       | Caminho de um interpretador Python específico, caso necessário                 |

Para usar as duas portas padrão, mantenha-as disponíveis ou escolha outros valores. Dados e configurações particulares não devem ser versionados.

### Docker Compose

Existe uma configuração que reúne PostgreSQL, IA e aplicação:

```bash
docker compose up --build
```

Ela usa credenciais de demonstração e disponibiliza a aplicação em `http://localhost:3000`. A validação registrada neste README foi realizada com **SQLite e processos locais**; a execução em Docker/PostgreSQL não foi verificada nesta evidência.

## Utilizar a aplicação

Selecione **setembro de 2026** para explorar o cenário inicial:

1. **Visão geral:** consumo liberado, faturas, pontos de recarga, pendências e previsão.
2. **Sessões de recarga:** consulte registros, filtre status e importe lotes JSON pelo botão de importação.
3. **Nova sessão:** informe unidade, veículo, carregador, horários e leituras acumuladas do medidor.
4. **Inteligência operacional:** examine a previsão horária, as métricas e os motivos das anomalias.
5. **Revisar:** aprove uma medição conferida ou exclua o registro do faturamento, com justificativa de 10 a 500 caracteres.
6. **Rateio e faturas:** configure tarifa e taxa fixa; resolva as pendências antes de gerar as faturas. A tela permite exportar CSV.
7. **Portal do morador:** escolha uma unidade demonstrativa para consultar seu histórico e a fatura consolidada.

O cenário contém 366 sessões históricas sintéticas de agosto e setembro e quatro registros demonstrativos. Na competência de setembro há 184 sessões e, inicialmente, duas pendências. Os registros de referência da unidade 302 podem receber aprovação justificada na inicialização, baseada nas leituras conhecidas do cenário sintético; a revisão fica registrada na auditoria.

## Regras de consumo e rateio

```text
Consumo da sessão = medidor final válido - medidor inicial
Consumo mensal da unidade = soma das sessões liberadas ou aprovadas
Fatura = consumo mensal em kWh x tarifa por kWh + taxa fixa

Exemplo da unidade 302:
35 kWh + 25 kWh = 60 kWh
60 x R$ 1,05 + R$ 20,00 = R$ 83,00
```

Sessões interrompidas usam a última leitura válida. Leituras ausentes ou regressivas não se tornam consumo cobrável. A potência média é conferida em relação ao limite nominal do carregador, com tolerância de 10%.

A energia é armazenada em Wh inteiros. A tarifa usa milésimos de real e as parcelas financeiras usam centavos; o consumo é somado antes do arredondamento mensal. Todos os veículos da mesma unidade participam da sua fatura. Unidade sem recarga tem parcela variável zero e recebe a taxa fixa configurada.

IDs duplicados, associação incorreta entre veículo e unidade e sessões simultâneas no mesmo carregador são recusados. A importação de um lote é atômica. Pendências bloqueiam o fechamento. Depois de faturado, o mês fica fechado para novas sessões e as faturas são preservadas; repetir o fechamento com a mesma tarifa e taxa devolve o resultado existente.

## Papel da IA

- **Isolation Forest:** analisa energia, duração e potência média usando histórico validado. São necessárias pelo menos 30 sessões para treinamento; histórico insuficiente exige revisão. Regras físicas e motivos de integridade são mantidos mesmo se o modelo não sinalizar o registro. Indisponibilidade da IA interrompe a ingestão, evitando liberação automática sem análise.
- **Random Forest Regressor:** estima demanda horária com padrões de horário, dia da semana e fim de semana. Utiliza até 90 dias de histórico, exige pelo menos 14 e reserva os últimos sete dias para avaliação temporal antes do ajuste final. A energia total da sessão é distribuída pelo intervalo conforme sua potência média; o protótipo não possui amostragem elétrica minuto a minuto.

## Testar

```bash
npx --yes pnpm@11.25.0 test
```

O comando executa os testes Python, inicia temporariamente a IA em uma porta livre e executa os testes Node.js. A cobertura inclui consumo, sessão interrompida, calendário e fuso de competência, arredondamento, respostas inválidas da IA, rollback, concorrência, auditoria, faturamento, filtros por unidade e exportação CSV. A [saída registrada](docs/evidencias/testes.txt) contém os **40 testes aprovados**.

## Organização dos arquivos

```text
ai/                       Modelos e serviço HTTP Python
db/schema.sql             Estrutura relacional
server/domain/            Validações e cálculos
server/application/       Sessões, revisão, faturas, painel e previsão
server/infrastructure/    Bancos, repositórios, cliente de IA e cenário sintético
server/presentation/http/ Rotas, respostas e arquivos estáticos
web/app/                  Navegação e composição das telas
web/features/             Sessões, faturas, visão geral, IA e morador
web/shared/               Componentes, hooks, formatação e cliente da API
scripts/                  Inicialização, testes e geração de evidências
tests/                    Testes Node.js
docs/evidencias/           Registros reais da validação
```

## Limites do protótipo

A integração com o carregador e o SEMS+, autenticação, autorização por perfil e avaliação com medições reais são evoluções futuras. O seletor do morador demonstra a experiência da unidade, sem implementar controle de acesso. A aplicação recomenda ações de planejamento, mas não envia comandos ao carregador. As métricas de IA e os exemplos de faturamento apresentados são resultados de dados sintéticos.
