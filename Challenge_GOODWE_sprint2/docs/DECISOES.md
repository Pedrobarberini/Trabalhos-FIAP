# Decisões técnicas — Sprint 02

## Continuidade com a Sprint 01

| Plano anterior | Decisão implementada | Justificativa |
| --- | --- | --- |
| Back-end Spring Boot ou Node.js | Node.js 24 com API HTTP nativa | Uma das alternativas previstas; poucas dependências e regras de negócio separadas do transporte HTTP. |
| Banco PostgreSQL | PostgreSQL via `pg`, schema e Docker Compose; SQLite como modo local padrão | Mantém a opção original e permite demonstração sem instalar um servidor de banco. SQLite é um desvio explícito para portabilidade. |
| React e interface responsiva | React 19 e Vite | Painéis funcionais para gestor e morador, usando a mesma API. |
| Python, Pandas e scikit-learn | Python, NumPy e scikit-learn | As transformações cabem em arrays e listas; Pandas não foi necessário para este volume. |
| Previsão de demanda | Random Forest Regressor | Aprende padrões horários e semanais; fornece erro temporal e comparação com baseline. |
| Detecção de anomalias | Isolation Forest + regras de integridade | Modelo implementado conforme a técnica prevista, integrado à importação e ao bloqueio do rateio. |
| Dados SEMS+ e/ou simulados | Histórico sintético determinístico e importador canônico | Não foram fornecidas credenciais nem um contrato oficial de integração. Nenhum acesso real foi inventado. |
| Dataset Kaggle como alternativa | Gerador próprio com seed 42 | Evita dependência de download/login e permite conhecer os casos normais e anômalos. Não houve uso de dados Kaggle nesta entrega. |
| Cadastro de entidades | Entidades e relações persistidas; catálogo inicial de demonstração | CRUD administrativo completo foi adiado para concentrar o protótipo no registro, IA, rateio e evidências obrigatórias. |
| Alertas técnicos/regulatórios e APIs externas | Alertas de integridade/IA implementados; conformidade automática e APIs externas adiadas | O escopo obrigatório prioriza a lógica central e a IA. Não há certificação regulatória automática, comparação nacional ou validação física da instalação. |

## Consumo e dinheiro

O banco armazena energia em **Wh inteiros** e dinheiro em **centavos**. A API aceita leituras com até três casas decimais em kWh. Tarifa é armazenada em milésimos de real por kWh; taxa fixa em centavos. O valor variável é arredondado pelo método half-up **uma única vez após a soma mensal por unidade**. Assim, dois veículos de uma unidade não recebem duas taxas fixas.

Sessão concluída: `energia = medidor_final − medidor_inicial`. Sessão interrompida: `energia = última_leitura_válida − medidor_inicial`, mesmo que seja recebido outro valor final. Leitura ausente ou regressiva gera consumo indefinido e revisão; não é imputada por IA para cobrança. Correções exigem rejeitar o registro inconsistente e importar um registro com novo ID.

## Competência, sobreposição e fechamento

O fuso é `America/Sao_Paulo`. A competência corresponde ao mês do **encerramento**. Uma sessão que cruza a virada do mês pertence integralmente ao mês em que termina: o protótipo não dispõe da curva de medição para ratear fisicamente a energia entre competências. A previsão usa uma distribuição uniforme por hora, hipótese separada do cálculo da fatura.

Identificadores duplicados e intervalos sobrepostos no mesmo carregador são recusados. Intervalos adjacentes são aceitos. Lotes de até 100 sessões são atômicos. As mutações são serializadas com fila/transação SQLite e advisory lock transacional no PostgreSQL.

Qualquer pendência impede o fechamento do mês inteiro. O gestor pode aprovar uma medição válida ou excluir um registro, sempre com justificativa. A versão do modelo, score, motivos originais e decisões ficam persistidos. Fechamento cria uma fatura por unidade e vínculos com as sessões; chamadas repetidas com os mesmos parâmetros devolvem as faturas existentes. Outra tarifa/taxa, alteração de decisão ou ingestão no mês encerrado são recusadas. Não há reabertura automática ou recálculo destrutivo.

## Histórico e avaliação de IA

O gerador cria 366 sessões históricas (61 dias × 2 carregadores × 3 janelas), fisicamente coerentes e marcadas como histórico sintético validado. As quatro sessões demonstrativas usam a mesma normalização e análise de IA da ingestão, em uma transação atômica: duas da unidade 302, uma anomalia e uma sessão sem medição. Caso as duas sessões de referência sejam sinalizadas, o seed registra uma aprovação com justificativa baseada no ground truth sintético. Isso fica visível na auditoria.

Novas sessões são classificadas por um modelo treinado com os registros validados disponíveis, sem usar os próprios candidatos como treino. A detecção não é uma prova de fraude ou defeito: ela solicita conferência humana. O histórico inicialmente validado tem origem conhecida; em produção essa confiança precisará ser estabelecida por medições e revisão independentes.

A previsão usa exclusivamente registros aprovados/limpos encerrados antes da data solicitada. Dados futuros, rejeitados e pendentes ficam fora. A separação de treino e validação respeita o tempo. O MAE e a comparação com a média histórica são expostos mesmo quando o modelo não supera essa média. A distribuição sintética não sustenta uma alegação de precisão operacional real.

## Limites da entrega

Não foram implementados login, permissões de produção, integração elétrica, comando OCPP, leitor RFID, pagamentos, alarmes externos, previsão de geração solar nem verificação legal automatizada. O protótipo não deve ser exposto publicamente com dados pessoais. A configuração local usa loopback e o Compose publica somente a porta da aplicação em loopback.

O caminho PostgreSQL está disponível no código e Compose, mas requer validação adicional em ambiente com Docker/PostgreSQL. Os testes e evidências deste trabalho foram produzidos com SQLite e serviço scikit-learn real. Nenhum vídeo pitch foi produzido, conforme o escopo solicitado.
