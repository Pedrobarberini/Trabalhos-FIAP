# SIFSM - Sistema Integrado de Futuro Sustentável em Marte

Projeto da Aurora Siger com **Parte 1 (Python e CRUD)** e **Parte 2 (circuito lógico, sensores e estruturas de dados)** integradas no mesmo menu e banco SQLite.

## Executar

O menu, o CRUD, as regras e os testes usam somente a biblioteca padrão do Python. Ambiente validado: Python 3.12.

```bash
python main.py
```

A entrada padronizada da atividade também está disponível:

```bash
python codigo_fonte.py
```

O banco `aurora_siger.db` é criado e preenchido automaticamente pela Parte 1. A **opção 6** chama `parte2_regras.executar(conn)`, passando a mesma conexão do menu.

## Funcionalidades integradas

- Cadastro, consulta, alteração e exclusão de módulos, sensores, leituras, alertas e manutenções.
- Exportação de leituras para CSV.
- Regra booleana `R = (E AND C) OR O OR (NOT V)`, com LED e buzzer virtuais.
- Análise da última leitura de cada sensor de consumo ou oxigênio.
- Fila de prioridade, consultas por dicionário e histórico.
- Registro dos alertas calculados na tabela `alertas`, com auditoria em `parte2_eventos` e prevenção de duplicação.

As opções de simulação/regressão e agentes/arquitetura continuam como pontos de integração para as Partes 3 e 4. O menu informa quando esses módulos ainda não estão presentes.

## Validar sem modificar o banco de uso

```bash
python parte2_regras.py --demo
python -m unittest discover -s testes -v
```

O primeiro comando usa o schema e os dados de exemplo da Parte 1 em SQLite **em memória**, mostra as decisões e testa o registro idempotente de alertas. Os resultados estão em [evidencias/parte2_sqlite](evidencias/parte2_sqlite/execucao_sqlite.json). A validação integrada contém **44 testes aprovados**, com o registro em [evidencias/testes.txt](evidencias/testes.txt).

Há também um cenário didático de 13 leituras, útil para demonstrar todas as causas da regra e os limites:

```bash
python parte2_regras.py --cenario-json --demo
```

Essa demonstração fica separada do banco da Parte 1 e não é importada automaticamente para ele.

## Documentação e arquivos

| Arquivo | Responsabilidade |
| --- | --- |
| [README_PARTE1.md](README_PARTE1.md) | Implementação original do banco e CRUD |
| [README_PARTE2.md](README_PARTE2.md) | Execução, regras, prioridades e contrato da integração |
| [RELATORIO_PARTE2.md](RELATORIO_PARTE2.md) | Análise técnica da compatibilidade e dos resultados |
| `main.py` / `codigo_fonte.py` | Entradas do menu integrado |
| `banco.py` / `crud.py` | Schema, dados de exemplo, conexão e operações da Parte 1 |
| `integracao.py` | Contratos `executar(conn)` e exportação CSV |
| `parte2_regras.py` | Adaptador entre SQLite, circuito e fila de alertas |
| `parte2/` | Modelos de sensores, portas lógicas, estruturas e demonstração JSON |
| [script_banco.sql](script_banco.sql) | Estrutura das tabelas originais e da auditoria da Parte 2 |
| [circuito_logico.png](circuito_logico.png) | Representação das portas AND, OR e NOT |
| `testes/` | Testes da lógica e da integração com banco, CRUD e menu |
| `evidencias/` | Execução real no schema do projeto e saída dos testes |

## Parâmetros e limites

A integração começa com limite de **50 kWh por leitura de consumo** e mínimo de **19,5% de oxigênio**. São parâmetros didáticos configuráveis da função `analisar`; não são limites certificados. A leitura de consumo deve representar energia em uma janela comparável. Medidores acumulados precisam ser convertidos em consumo do intervalo pela aquisição de dados.

Um sensor de consumo não é obrigado a fornecer oxigênio, e um sensor de oxigênio não é obrigado a fornecer energia. Unidades incompatíveis, leitura ausente, sensor inativo ou valor inválido acionam o sinal de falha. Não há conversão automática de kW para kWh.

As ações são simuladas, sem hardware ou desligamento de sistemas essenciais. Os dados de exemplo são históricos; analisar a última leitura não constitui monitoramento em tempo real. O registro de um alerta não confirma sua resolução física.
