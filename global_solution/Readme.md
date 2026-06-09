# 🚀 Global Solution - Sistema Inteligente de Monitoramento Espacial

## 📌 Sobre o Projeto

Este projeto foi desenvolvido para o desafio **Global Solution** da FIAP, no curso de **Ciência da Computação**.

A proposta consiste em um **Sistema Inteligente de Monitoramento para Missões Espaciais Experimentais**, capaz de analisar dados de telemetria, identificar situações críticas, gerar alertas automáticos e recomendar ações operacionais para garantir a segurança da missão.

O sistema simula o painel de controle da estação espacial **ARES-1**, monitorando indicadores essenciais como geração de energia, consumo, reserva energética, temperatura externa, radiação e qualidade da comunicação.

---

## 🎯 Objetivo

O principal objetivo do projeto é transformar dados operacionais em informações estratégicas para tomada de decisão em uma missão espacial.

A solução busca:

* Monitorar dados de telemetria da missão;
* Classificar módulos operacionais como `NORMAL`, `ALERTA` ou `CRÍTICO`;
* Detectar inconsistências entre os dados;
* Priorizar alertas conforme a severidade;
* Registrar eventos críticos em estrutura de pilha;
* Aplicar regressão linear para previsão de reserva energética;
* Gerar recomendações automáticas para mitigação de riscos.

---

## 🛰️ Contexto da Solução

Missões espaciais dependem de sistemas capazes de interpretar dados em tempo real e responder rapidamente a cenários adversos.

Falhas em comunicação, energia, suporte à vida ou exposição à radiação podem comprometer a segurança da tripulação e a continuidade da missão.

Pensando nisso, o sistema desenvolvido simula um ambiente de monitoramento inteligente, aplicando conceitos fundamentais de lógica computacional, estruturas de dados e análise preditiva.

---

## 🧠 Conceitos Aplicados

Durante o desenvolvimento foram aplicados conceitos estudados ao longo do curso:

### Lógica Computacional

Utilização de operadores booleanos como:

* `AND`
* `OR`
* `NOT`

Esses operadores são utilizados para diagnosticar situações críticas da missão.

### Estruturas de Dados

Foram utilizadas diferentes estruturas para organizar as informações:

* **Listas:** armazenamento dos dados de telemetria;
* **Matriz:** organização dos dados lidos do CSV;
* **Fila de alertas:** priorização dos eventos ativos;
* **Pilha:** armazenamento dos últimos eventos críticos.

### Análise Preditiva

Foi implementada uma regressão linear simples para prever a próxima reserva energética da missão com base nos dados históricos.

---

## 🛠️ Tecnologias Utilizadas

* Python 3
* CSV
* Git
* GitHub

---

## 📁 Estrutura do Projeto

```bash
global_solution/
│
├── dados.csv        # Arquivo com os dados simulados de telemetria
├── sistema.py       # Código principal do sistema de monitoramento
└── README.md        # Documentação do projeto
```

---

## 📊 Dados Monitorados

O arquivo `dados.csv` contém os dados de telemetria utilizados pelo sistema.

As informações monitoradas são:

| Campo            | Descrição                       |
| ---------------- | ------------------------------- |
| `horario`        | Horário da leitura              |
| `geracao_solar`  | Energia gerada por fonte solar  |
| `geracao_eolica` | Energia gerada por fonte eólica |
| `consumo`        | Consumo energético da estação   |
| `reserva_pct`    | Percentual de energia restante  |
| `temp_externa`   | Temperatura externa             |
| `radiacao`       | Nível de radiação               |
| `qualidade_com`  | Qualidade da comunicação        |

---

## ⚙️ Funcionalidades

### 1. Leitura de Telemetria

O sistema realiza a leitura dos dados a partir de um arquivo CSV e organiza as informações em listas e matrizes.

### 2. Status dos Módulos

Os módulos principais da missão são avaliados individualmente.

Exemplos de módulos:

* Suporte à vida;
* Energia;
* Comunicação;
* Habitat;
* Laboratório;
* Armazenamento.

Cada módulo recebe uma classificação:

* `NORMAL`
* `ALERTA`
* `CRÍTICO`

### 3. Verificação de Inconsistências

O sistema identifica inconsistências operacionais.

Exemplo:

> O módulo de comunicação pode estar marcado como ativo, mas apresentar qualidade de sinal abaixo do mínimo seguro.

### 4. Diagnóstico Geral da Missão

Com base nos dados de energia, radiação, comunicação e suporte à vida, o sistema define a situação geral da missão.

Possíveis diagnósticos:

* `NORMAL`
* `ALERTA`
* `CRÍTICO`

### 5. Alertas Priorizados

Os alertas são organizados conforme sua severidade.

A prioridade utilizada é:

```python
PRIORIDADE = {
    "CRITICO": 0,
    "ALERTA": 1,
    "NORMAL": 2
}
```

Assim, eventos críticos aparecem antes dos alertas de menor impacto.

### 6. Histórico de Eventos Críticos

O sistema utiliza uma pilha para armazenar os últimos eventos críticos.

Com isso, é possível consultar rapidamente os acontecimentos mais recentes da missão.

### 7. Previsão de Energia

Foi implementada uma regressão linear simples para prever a reserva de energia no próximo ciclo.

Essa previsão permite antecipar possíveis quedas críticas e auxiliar na tomada de decisão.

### 8. Recomendações Automáticas

Com base no diagnóstico geral e nos dados previstos, o sistema gera recomendações automáticas.

Exemplos:

* Manter suporte à vida ativo;
* Desligar sistemas não essenciais;
* Ativar canal de comunicação redundante;
* Redirecionar energia para o habitat;
* Cortar consumo não essencial.

---

## ▶️ Como Executar o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/Pedrobarberini/Trabalhos-FIAP.git
```

### 2. Acesse a branch do projeto

```bash
git checkout global_solution
```

### 3. Entre na pasta do projeto

```bash
cd global_solution
```

### 4. Execute o sistema

```bash
python sistema.py
```

---

## ⚠️ Observação Importante

No arquivo `sistema.py`, o caminho do arquivo CSV pode estar configurado com um caminho absoluto do computador utilizado no desenvolvimento.

Caso necessário, altere a linha de leitura do arquivo para:

```python
with open("dados.csv", "r", encoding="utf-8") as arquivo:
```

Isso permite que o projeto funcione corretamente em qualquer computador, desde que o arquivo `dados.csv` esteja na mesma pasta do `sistema.py`.

---

## 🧪 Exemplo de Saída Esperada

Ao executar o sistema, o terminal exibirá informações como:

```bash
============================================================
 ESTACAO ARES-1 - PAINEL DE MONITORAMENTO
============================================================

[ LEITURAS POR HORARIO ]
Horario | Solar Eolica Consumo Reserva Temp Radiacao QualCom

[ STATUS DOS MODULOS ]
MODULO | BINARIO | STATUS

[ VERIFICACAO DE INCONSISTENCIAS ]

[ DIAGNOSTICO GERAL ]
Situacao da missao: CRITICO

[ ALERTAS ATIVOS (priorizados) ]

[ HISTORICO (pilha de eventos criticos) ]

[ PREVISAO DE ENERGIA (regressao linear) ]

[ RECOMENDACOES ]
```

---

## 🎥 Vídeo Pitch

Além do desenvolvimento do sistema, também foi produzido um **vídeo pitch** apresentando a proposta, o funcionamento da solução e os principais conceitos aplicados.

No vídeo são demonstrados:

* O problema abordado;
* A importância do monitoramento espacial;
* A leitura dos dados de telemetria;
* A classificação dos módulos;
* A geração de alertas;
* O uso de pilhas e filas;
* A previsão da reserva energética;
* As recomendações automáticas geradas pelo sistema.

---

## 👥 Integrantes

* Laura Oliveira
* Alexandre Ribeiro
* Igor Costa
* Pedro Barberini Rodrigues Carvalho
* Yan Victer

---

## 📚 Aprendizados

Este projeto permitiu aplicar, de forma prática, diversos conceitos fundamentais da Ciência da Computação, como lógica booleana, estruturas de dados, manipulação de arquivos, organização de dados, tomada de decisão automatizada e análise preditiva.

A solução demonstra como sistemas computacionais podem apoiar decisões críticas em cenários complexos, como missões espaciais experimentais.

---

## ✅ Conclusão

O Sistema Inteligente de Monitoramento Espacial desenvolvido para a Global Solution apresenta uma solução funcional, acadêmica e alinhada aos desafios tecnológicos atuais.

Por meio da análise de telemetria, priorização de alertas, histórico de eventos críticos e previsão matemática, o projeto mostra como a tecnologia pode ser utilizada para aumentar a segurança, a eficiência e a autonomia de operações em ambientes extremos.

Mais do que um sistema em Python, este projeto representa a aplicação prática dos conhecimentos adquiridos ao longo do curso, demonstrando raciocínio lógico, organização de dados e capacidade de resolver problemas reais com programação.

---

## 📌 Status do Projeto

✅ Projeto acadêmico concluído
✅ Código funcional em Python
✅ Base de dados em CSV
✅ Vídeo pitch produzido
✅ Documentação desenvolvida para apresentação no Global Solution
