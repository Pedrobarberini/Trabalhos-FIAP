# 🚀 Sistema de Gerenciamento da Colônia Aurora Singer

Sistema desenvolvido em Python para monitoramento e gerenciamento energético da colônia fictícia **Aurora Singer**, localizada em Marte.  
O projeto simula controle de energia, clima, modos de operação e verificações automáticas de segurança dos módulos da colônia.

---

## 📌 Objetivo

O sistema foi criado para simular o funcionamento de uma colônia espacial, realizando:

- Monitoramento climático
- Controle de bateria e energia
- Definição automática do modo operacional
- Verificação de sistemas essenciais
- Emissão de alertas preventivos

---

## 🛠️ Tecnologias Utilizadas

- **Python**
  - Estruturação do sistema
  - Lógica de programação
  - Funções e condicionais
  - Organização de dados com dicionários e listas

---

## 📂 Estrutura do Projeto

```bash
📁 Atividade CAP 3
 ┣ 📄 Primeiros_Sistemas_da_Colônia.py
 ┗ 📄 README.md
```

---

## ⚙️ Funcionalidades:

### 🌡️ Monitoramento Climático

Exibe:

- Temperatura externa
- Temperatura interna
- Velocidade do vento
- Umidade
- Status de tempestade de areia

---

### 🔋 Controle de Energia

O sistema calcula:

- Capacidade total das baterias
- Carga atual
- Percentual de energia disponível

---

### 🚨 Modos de Operação

O sistema define automaticamente o modo da colônia:

| Modo | Condição |
|---|---|
| NORMAL | Bateria acima de 60% e sem tempestade |
| ECONOMIA | Bateria entre 30% e 60% |
| CRÍTICO | Bateria abaixo de 30% |

---

### 🛰️ Verificação dos Sistemas

Realiza verificações automáticas em:

- Umidade
- Sistema solar
- Sistema eólico

---

## ▶️ Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
```

### 2. Acesse a pasta do projeto

```bash
cd Atividade CAP 3
```

### 3. Execute o sistema

```bash
python Primeiros_Sistemas_da_Colônia.py
```

---

## 📋 Exemplo de Saída

```bash
SISTEMA DE GERENCIAMENTO DA COLÔNIA AURORA SINGER

CONDIÇÕES CLIMÁTICAS
Temperatura Externa: -25°C
Temperatura Interna: 22°C

STATUS DE ENERGIA
Bateria Atual: 4400 kWh
Percentual: 100.0%

MODO DE OPERAÇÃO: NORMAL
```

---

## 📖 Conceitos Aplicados

- Estruturas condicionais
- Funções
- Dicionários aninhados
- Organização hierárquica de dados
- Simulação de cenários
- Boas práticas de programação
