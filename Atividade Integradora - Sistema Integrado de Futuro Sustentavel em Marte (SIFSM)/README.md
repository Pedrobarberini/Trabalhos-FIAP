#  SIFSM — Sistema Integrado de Futuro Sustentável em Marte
**Projeto de Base de Aprendagem (PBL) — Atividade Integradora Fase 7 (2026)**  
**Colônia Marciana:** Aurora Siger  

---

##  Sumário
1. [Visão Geral do Projeto](#-visão-geral-do-projeto)
2. [Estrutura de Arquivos da Entrega (.zip)](#-estrutura-de-arquivos-da-entrega-zip)
3. [Detalhamento Técnico por Parte (Consolidado)](#-detalhamento-técnico-por-parte-consolidado)
   * [Parte 1: Sistema em Python, CRUD e Banco de Dados](#parte-1-sistema-em-python-crud-e-banco-de-dados)
   * [Parte 2: Lógica Booleana, Circuitos, Sensores e Estruturas de Dados](#parte-2-lógica-booleana-circuitos-sensores-e-estruturas-de-dados)
   * [Parte 3: Simulação Computacional e Modelagem Matemática](#parte-3-simulação-computacional-e-modelagem-matemática)
   * [Parte 4: Inteligência Artificial, Arquitetura Computacional e Sustentabilidade](#parte-4-inteligência-artificial-arquitetura-computacional-e-sustentabilidade)
   * [Parte 5: Integração, Relatório Técnico e Apresentação](#parte-5-integração-relatório-técnico-e-apresentação)
4. [Pré-requisitos e Dependências](#-pré-requisitos-e-dependências)
5. [Instruções de Execução](#-instruções-de-execução)
6. [Vídeo de Apresentação](#-vídeo-de-apresentação)

---

##  1. Visão Geral do Projeto
O **SIFSM (Sistema Integrado de Futuro Sustentável em Marte)** foi desenvolvido como o protótipo central de governança, monitoramento e tomada de decisão autônoma para a colônia marciana **Aurora Siger**. O sistema integra camadas físicas, lógicas, analíticas e de inteligência artificial para otimizar o uso de recursos críticos (energia, água, oxigênio), mitigar riscos operacionais e garantir a sustentabilidade de longo prazo em habitações extraterrestres.

---

##  2. Estrutura de Arquivos da Entrega (.zip)
A pasta compactada contém rigorosamente os seguintes arquivos e diretórios padronizados:
* `main.py` — Ponto de entrada principal do sistema contendo o menu interativo no terminal.
* `banco.py` — Gerenciamento e conexão com o banco de dados (SQLite/Estruturado).
* `crud.py` — Implementação das operações de cadastro, listagem, alteração e exclusão de registros.
* `parte2/` — Módulos contendo as regras de risco booleanas, simulação de sensores e estruturas de dados (filas, pilhas, tabelas hash).
* `parte3_simulacao.py` — Script responsável pela simulação computacional dinâmica e modelagem matemática (regressão linear).
* `script_banco.sql` — Script SQL contendo a criação da estrutura relacional das tabelas.
* `relatorio_tecnico.md` — Relatório técnico completo e detalhado de toda a solução.
* `link_video.txt` — Arquivo de texto contendo o link de acesso ao vídeo de apresentação no YouTube.

---

##  3. Detalhamento Técnico por Parte (Consolidado)

### Parte 1: Sistema em Python, CRUD e Banco de Dados
* **Objetivo:** Estabelecer a infraestrutura de software e persistência de dados da colônia.
* **Funcionalidades:**
  * Conexão estruturada com banco de dados e arquivos auxiliares em formato JSON.
  * Implementação completa das operações **CRUD**: **C**adastrar (novos módulos/sensores), **R**esolver/Listar (consulta em tempo real), **U**pdate/Alterar (status operacionais) e **D**elete/Excluir (registros inconsistentes).
  * **Tratamento de Erros:** Uso rigoroso de blocos `try`, `except`, `else` e `finally` para tratar entradas inválidas de usuário e falhas de conexão ou leitura.

### Parte 2: Lógica Booleana, Circuitos, Sensores e Estruturas de Dados
* **Objetivo:** Automatizar a tomada de decisões de segurança e organizar o fluxo informacional.
* **Funcionalidades:**
  * **Regra Booleana de Risco:** Expressões lógicas para disparo automático de alertas (ex: cruzamento de consumo energético elevado em módulos críticos com estados de falha de sensores).
  * **Automação e Circuitos:** Representação lógica de decisões de hardware simulado (Tinkercad/Arduino/Python) para acionamento de atuadores, como liberação de irrigação agrícola e sinalização de manutenção.
  * **Estruturas de Dados Aplicadas:**
    * *Filas (Queues):* Organização de solicitações da tripulação e chamados de manutenção por ordem de chegada (FIFO).
    * *Pilhas (Stacks):* Registro do histórico de ações com suporte à função de desfazer etapas (*undo*).
    * *Tabelas Hash:* Busca rápida e indexada por códigos de sensores e módulos.

### Parte 3: Simulação Computacional e Modelagem Matemática
* **Objetivo:** Projetar cenários futuros, prever demandas e validar critérios de sustentabilidade.
* **Funcionalidades:**
  * **Simulação Dinâmica:** Scripts desenvolvidos em Python (com apoio de `NumPy` e `Matplotlib`) para simular a variação do estado de carga de baterias, consumo energético e oscilação de temperatura em ciclos marcianos.
  * **Modelagem Linear:** Aplicação de regressão linear simples e múltipla para prever o consumo de recursos com base no histórico operacional, acompanhada de análises exploratórias, correlações e avaliação de métricas do modelo.

### Parte 4: Inteligência Artificial, Arquitetura Computacional e Sustentabilidade
* **Objetivo:** Alinhar a proposta a conceitos modernos de IA, arquitetura de hardware e cidadania digital.
* **Funcionalidades:**
  * **Sistemas Multiagentes:** Proposta conceitual de agentes especializados (Agente de Energia, Agente Ambiental e Agente de Manutenção) coordenados por um agente triador, utilizando *handoffs* (transferência de tarefas) e *guardrails* (regras de segurança).
  * **Arquitetura Computacional:** Discussão sobre computação heterogênea (distribuição de cargas entre CPUs, GPUs e aceleradores), hierarquia de memória e eficiência energética no data center da colônia.
  * **Sustentabilidade e Cidadania Digital:** Análise rigorosa sobre privacidade de dados da tripulação, mitigação de impactos socioambientais de processamento intensivo e inovação tecnológica ética.

### Parte 5: Integração, Relatório Técnico e Apresentação
* **Objetivo:** Consolidar todas as entregas em um pacote coeso, documentado e demonstrável.
* **Funcionalidades:**
  * Elaboração do **Relatório Técnico (`relatorio_tecnico.md`)** completo.
  * Organização estruturada do pacote de arquivos em formato `.zip`.
  * Coordenação e gravação do vídeo oficial de apresentação da equipe.

---

##  4. Pré-requisitos e Dependências
O projeto foi desenvolvido inteiramente em linguagem **Python (versão 3.10 ou superior)**. 

Para o correto funcionamento das simulações numéricas e geração de gráficos, certifique-se de instalar as bibliotecas necessárias executando o comando abaixo no terminal:
```bash
pip install numpy pandas matplotlib