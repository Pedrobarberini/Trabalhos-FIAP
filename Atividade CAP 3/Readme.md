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

## ✅ Conclusão

O desenvolvimento do Sistema de Gerenciamento da Colônia Aurora Singer proporcionou uma aplicação prática dos conhecimentos adquiridos em programação utilizando a linguagem Python. Durante a criação do projeto, foi possível trabalhar conceitos importantes como estruturas condicionais, funções, organização de dados com dicionários e listas, além da separação de responsabilidades dentro do código para tornar o sistema mais organizado, legível e eficiente.

A proposta do sistema foi simular o gerenciamento de uma colônia espacial localizada em Marte, considerando diferentes fatores que influenciam diretamente o funcionamento da base, como condições climáticas, geração de energia, consumo dos módulos e controle do nível das baterias. Com isso, o projeto permitiu demonstrar como sistemas automatizados podem auxiliar na tomada de decisões em ambientes críticos, garantindo maior segurança e eficiência operacional.

Outro ponto importante foi a implementação dos diferentes modos de operação da colônia, permitindo que o sistema se adapte automaticamente conforme o nível de energia disponível e as condições ambientais. Essa lógica de adaptação torna a simulação mais próxima de situações reais, mostrando a importância do gerenciamento inteligente de recursos em cenários de risco ou emergência.

Além do aprendizado técnico, o projeto também contribuiu para o desenvolvimento da lógica de programação, da análise de problemas e da organização estrutural de sistemas. A utilização de funções específicas para cada tarefa facilitou a manutenção do código e tornou o sistema mais modular e reutilizável.

Por fim, o trabalho demonstrou como a programação pode ser aplicada na criação de soluções capazes de monitorar, analisar e controlar diferentes processos de maneira automatizada. O projeto serviu como uma importante experiência prática no desenvolvimento de sistemas, reforçando conhecimentos fundamentais da área de tecnologia e preparando para desafios mais avançados no desenvolvimento de software.