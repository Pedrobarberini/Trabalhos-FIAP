# RELATÓRIO TÉCNICO

# Sistema Integrado de Futuro Sustentável em Marte (SIFSM)

## Aurora Siger

### Integrantes

- Nome: Alexandre - Rm572374 

- Nome: Igor - Rm573995 

- Nome: Kaua - Rm573734 

- Nome: Laura - Rm573954 

- Nome: Pedro - Rm573405

---

# 1. Introdução

A exploração e colonização de Marte exigem sistemas capazes de monitorar recursos limitados de forma eficiente, sustentável e segura.

A colônia Aurora Siger foi utilizada como cenário para o desenvolvimento do Sistema Integrado de Futuro Sustentável em Marte (SIFSM), um protótipo computacional capaz de armazenar dados operacionais, monitorar sensores, identificar riscos, executar simulações, realizar previsões e apoiar tomadas de decisão.

O projeto integra conceitos de programação, banco de dados, lógica computacional, estruturas de dados, modelagem matemática, simulação computacional, inteligência artificial e arquitetura de computadores.

---

# 2. Objetivos

O sistema foi desenvolvido com os seguintes objetivos:

- Centralizar informações da colônia;
- Monitorar recursos críticos;
- Organizar dados em banco de dados;
- Aplicar regras lógicas para identificação de riscos;
- Simular cenários energéticos;
- Criar previsões baseadas em regressão linear;
- Apoiar decisões sustentáveis;
- Demonstrar integração multidisciplinar.

---

# 3. Descrição Geral da Solução

O SIFSM funciona como uma central de monitoramento da colônia Aurora Siger.

A solução armazena informações relacionadas a:

- módulos da colônia;
- sensores;
- leituras;
- ocorrências;
- manutenção.

Os dados são analisados por regras de decisão e podem ser utilizados por simulações matemáticas e modelos preditivos.

---

# 4. Banco de Dados

## Tecnologia Utilizada

O sistema utiliza SQLite.

A escolha foi realizada por ser um banco leve, embarcado e que dispensa servidor dedicado.

## Estrutura do Banco

### Tabela Modulos

Armazena:

- código;
- nome;
- tipo;
- criticidade;
- status.

### Tabela Sensores

Armazena:

- código;
- tipo;
- unidade;
- módulo associado;
- situação operacional.

### Tabela Leituras

Armazena as medições realizadas pelos sensores.

### Tabela Alertas

Registra situações de risco detectadas pelo sistema.

### Tabela Manutencoes

Controla operações preventivas e corretivas.

### Tabela Parte2_Eventos

Responsável pela auditoria das decisões automáticas dos alertas.

---

# 5. Operações CRUD

O sistema implementa integralmente o CRUD.

## Create

Cadastro de novos registros.

## Read

Consulta de informações.

## Update

Atualização de dados.

## Delete

Remoção de registros.

As exclusões utilizam o mecanismo:

ON DELETE CASCADE

preservando a consistência do banco.

---

# 6. Tratamento de Erros

O sistema utiliza estruturas de tratamento de exceções.

Exemplo:

```python
try:
except:
else:
finally:

Principais situações tratadas:

- entrada inválida;
- valor inconsistente;
- violação de integridade;
- falha de conexão;
- erro inesperado.

---

# 7. Circuitos Lógicos e Decisão Computacional

Foi desenvolvida uma regra booleana para identificação automática de situações de risco.

## Expressão Booleana

R = (E AND C) OR O OR (NOT V)

Onde:

| Variável | Significado |
|-----------|-------------|
| E | Consumo elevado |
| C | Módulo crítico |
| O | Oxigênio crítico |
| V | Sensor válido |
| R | Situação de risco |

---

# 8. Circuito Lógico

Foram utilizadas portas lógicas:

- AND
- OR
- NOT

A saída aciona:

- LED virtual;
- buzzer virtual.

O circuito foi representado graficamente em circuito_logico.png.

---

# 9. Estruturas de Dados

## Listas

Utilizadas para armazenamento de leituras e histórico de resultados.

## Dicionários (Tabela Hash)

Utilizados para busca rápida de sensores.

Complexidade média:

O(1)

## Heap de Prioridade

Implementa a fila de alertas do sistema.

Prioridades:

1. Oxigênio crítico
2. Falha de sensor
3. Consumo crítico
4. Consumo elevado não crítico

Complexidade:

- Inserção: O(log n)
- Remoção: O(log n)
- Consulta: O(1)

---

# 10. Simulação Computacional

A simulação representa um ciclo de 24 horas marcianas.

Variáveis analisadas:

- consumo energético;
- geração solar;
- energia acumulada;
- estado da bateria.

A modelagem permite avaliar o comportamento energético da colônia ao longo do tempo.

---

# 11. Integração Matemática

A energia consumida foi calculada por integração numérica.

Métodos utilizados:

## SciPy

quad()

## Regra dos Trapézios

Implementação manual para validação dos resultados.

A energia total corresponde à área sob a curva de potência ao longo do tempo.

---

# 12. Simulação da Bateria

A simulação calcula:

- carga inicial;
- carga mínima;
- carga final.

Esses indicadores permitem verificar a autonomia energética da colônia.

---

# 13. Modelagem Linear

Foi implementada uma regressão linear simples.

Variável independente:

Temperatura.

Variável dependente:

Consumo energético.

Equação geral:

Consumo = b0 + b1 × Temperatura

---

# 14. Avaliação do Modelo

Foram utilizadas métricas clássicas:

- Correlação de Pearson;
- Coeficiente de Determinação (R²);
- Erro Quadrático Médio (MSE);
- Erro Absoluto Médio (MAE).

Essas métricas permitem avaliar a capacidade preditiva do modelo.

---

# 15. Aplicação Prática

O modelo é utilizado para:

- prever demanda futura;
- identificar sobrecarga térmica;
- apoiar decisões energéticas;
- emitir recomendações preventivas.

---

# 16. Proposta de Inteligência Artificial

O projeto apresenta uma proposta conceitual de arquitetura multiagente.

Agentes propostos:

- Agente Orquestrador;
- Agente de Energia;
- Agente Ambiental;
- Agente de Dados;
- Agente de Manutenção;
- Agente de Simulação;
- Agente de Histórico.

A implementação foi mantida em nível conceitual, conforme permitido pelo enunciado da atividade.

---

# 17. Guardrails e Segurança

Foram definidos mecanismos de proteção para impedir decisões inadequadas.

Exemplos:

- validação humana obrigatória;
- proteção de módulos críticos;
- validação dos dados recebidos;
- restrição de acesso às informações.

---

# 18. Arquitetura Computacional

O projeto relaciona-se aos conceitos de:

- CPU;
- GPU;
- NPU;
- TPU;
- Computação Heterogênea;
- Lei de Amdahl;
- Hierarquia de Memória;
- Gargalo de Von Neumann.

---

# 19. Sustentabilidade

O projeto contribui para:

- uso eficiente de recursos;
- redução de desperdícios;
- planejamento preventivo;
- autonomia operacional.

---

# 20. Cidadania Digital

Foram considerados:

- privacidade dos dados;
- transparência;
- responsabilidade digital;
- uso ético da inteligência artificial.

---

# 21. Impacto Socioambiental

O sistema reconhece os impactos energéticos da computação e da inteligência artificial.

A proposta incentiva o uso responsável da tecnologia e a busca por soluções sustentáveis.

---

# 22. Limitações

- dados simulados;
- sensores virtuais;
- IA não implementada;
- ambiente simplificado;
- ausência de hardware físico.

---

# 23. Trabalhos Futuros

- integração com Arduino;
- sensores IoT;
- dashboard web;
- monitoramento em tempo real;
- sistemas inteligentes conectados ao banco.

---

# 24. Conclusão

O Sistema Integrado de Futuro Sustentável em Marte integra banco de dados, lógica computacional, estruturas de dados, matemática aplicada, simulação computacional, modelagem preditiva e inteligência artificial conceitual.

A solução atende aos requisitos da atividade integradora e demonstra como diferentes áreas da computação podem atuar de forma conjunta para apoiar uma colônia sustentável, resiliente e autônoma em Marte.