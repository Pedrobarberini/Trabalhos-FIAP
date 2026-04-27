# 🚀 MGPEB - Módulo Gerenciador de Pouso e Estabilização de Base

## 📌 Sobre o Projeto

O **MGPEB (Módulo Gerenciador de Pouso e Estabilização de Base)** é um sistema desenvolvido em Python com o objetivo de simular o processo de decisão de pouso de módulos em uma missão espacial.

O sistema utiliza **lógica booleana, estruturas de dados lineares e algoritmos básicos** para determinar se um módulo pode pousar com segurança em Marte.

---

## 🎯 Objetivos

* Simular a tomada de decisão de pouso de módulos espaciais
* Aplicar **portas lógicas (AND, OR, NOT)**
* Utilizar **estruturas de dados (listas, filas e pilhas)**
* Implementar **algoritmos de busca e ordenação**
* Desenvolver um sistema simples e eficiente, inspirado em sistemas embarcados

---

## 🧠 Regras de Decisão (Lógica Booleana)

O pouso de um módulo é autorizado com base na seguinte expressão:

```
POUSO_AUTORIZADO = combustível_ok AND clima_estavel AND area_livre AND sensores_ok
```

### 🔍 Interpretação:

* O módulo **só pode pousar** se TODAS as condições forem verdadeiras
* Caso contrário, o sistema:

  * Gera alertas
  * Ou adia o pouso

---

## 🏗️ Estruturas de Dados Utilizadas

* **Fila (Queue)** → Armazena os módulos aguardando pouso
* **Lista (List)** → Registra os módulos que já pousaram
* **Pilha (Stack)** → Armazena alertas e erros do sistema

---

## 🔎 Funcionalidades

### ✔ Cadastro de módulos

Permite adicionar módulos com atributos como:

* Nome
* Prioridade
* Combustível
* Criticidade
* Condições de sensores, clima e área

---

### ✔ Algoritmos de Busca

* Módulo com **menor combustível**
* Módulo com **maior prioridade**

---

### ✔ Ordenação

* Ordena a fila de pouso por **prioridade (decrescente)**

---

### ✔ Simulação de Pouso

O sistema analisa cada módulo e decide:

* ✅ Pouso autorizado
* ⚠️ Alerta (ex: combustível baixo)
* ⛔ Pouso adiado

---

## ▶️ Como Executar

1. Certifique-se de ter o Python instalado
2. Copie o código para um arquivo `.py`
3. Execute no terminal:

```
python nome_do_arquivo.py
```

---

## 🧪 Exemplo de Saída

```
=== BUSCAS ===
Menor combustível: Suporte Médico
Maior prioridade: Habitação

=== SIMULAÇÃO DE POUSO ===
Analisando módulo: Habitação
>>> POUSO AUTORIZADO

Analisando módulo: Suporte Médico
>>> ERRO: Falha nos sensores

=== MÓDULOS POUSADOS ===
Habitação

=== PILHA DE ALERTAS ===
Suporte Médico - falha sensores
```

---

## ⚙️ Tecnologias Utilizadas

* Python
* Lógica Booleana
* Estruturas de Dados
* Algoritmos básicos

---

## 🌍 Contexto do Projeto

Este projeto foi desenvolvido com base em um cenário de missão espacial, onde decisões precisam ser:

* Rápidas
* Confiáveis
* Autônomas

Refletindo limitações reais como:

* Baixo consumo de energia
* Processamento limitado
* Alta criticidade das operações

---

## 📚 Aprendizados

* Aplicação prática de lógica computacional
* Uso de estruturas lineares
* Modelagem de problemas reais
* Tomada de decisão baseada em dados
