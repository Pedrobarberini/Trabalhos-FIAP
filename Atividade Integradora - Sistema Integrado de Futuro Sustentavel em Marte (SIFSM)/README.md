#  Sistema Integrado de Futuro Sustentável em Marte (SIFSM)

## Aurora Siger - Gestão Inteligente de Recursos para uma Colônia Marciana

### Integrantes

- Alexandre - Rm572374
- Igor - Rm573995 
- Kaua - Rm573734 
- Laura - Rm573954 
- Pedro - Rm573405 

---

#  Visão Geral

O Sistema Integrado de Futuro Sustentável em Marte (SIFSM) foi desenvolvido para auxiliar a operação da colônia marciana Aurora Siger por meio da integração de banco de dados, sensores simulados, lógica computacional, estruturas de dados, simulação matemática, modelagem preditiva e inteligência artificial conceitual.

A solução centraliza informações operacionais da colônia, monitora recursos essenciais, detecta riscos ambientais, simula cenários futuros e apoia a tomada de decisões sustentáveis.

O projeto integra os conteúdos estudados ao longo da fase acadêmica, demonstrando a aplicação prática de programação em Python, banco de dados, estruturas de dados, lógica digital, simulação computacional, regressão linear, arquiteturas computacionais modernas e sistemas inteligentes.

---

#  Objetivos

O sistema possui os seguintes objetivos:

- Monitorar recursos críticos da colônia;
- Centralizar dados operacionais;
- Automatizar a identificação de riscos;
- Organizar alertas por prioridade;
- Simular cenários energéticos;
- Prever comportamentos futuros;
- Apoiar a tomada de decisões sustentáveis;
- Demonstrar integração entre software, matemática e inteligência artificial.

---

#  Arquitetura Geral do Sistema

```text
Sensores
   ↓
Banco SQLite
   ↓
CRUD
   ↓
Regras Lógicas
   ↓
Estruturas de Dados
   ↓
Simulação Computacional
   ↓
Regressão Linear
   ↓
Sistema Multiagente
   ↓
Tomada de Decisão
```

---

#  Estrutura do Projeto

```text
SIFSM
│
├── main.py
├── crud.py
├── banco.py
├── integracao.py
├── parte2_regras.py
├── parte3_simulacao.py
├── aurora_siger.db
├── script_banco.sql
├── circuito_logico.png
├── README.md
├── relatorio_tecnico.pdf
├── link_video.txt
└── evidencias/
```

---

#  Banco de Dados

O sistema utiliza SQLite como mecanismo de armazenamento local.

## Tabelas

### Modulos

Armazena os módulos operacionais da colônia:

- Central de Energia
- Habitação Principal
- Estufa Agrícola
- Laboratório
- Comunicação
- Armazenamento
- Suporte Médico

### Sensores

Armazena os sensores instalados nos módulos.

Tipos disponíveis:

- Consumo energético
- Temperatura
- Umidade
- Oxigênio
- Luminosidade
- Presença
- Carga de baterias

### Leituras

Registra os valores coletados pelos sensores.

### Alertas

Armazena ocorrências críticas identificadas pelo sistema.

### Manutenções

Controla atividades preventivas e corretivas.

### Parte2_Eventos

Tabela auxiliar responsável pelo registro e auditoria dos alertas calculados automaticamente.

---

#  Operações CRUD

O sistema implementa integralmente as operações CRUD:

## CREATE

Cadastro de:

- Módulos
- Sensores
- Leituras
- Alertas
- Manutenções

## READ

Consulta de registros armazenados.

## UPDATE

Atualização das informações cadastradas.

## DELETE

Remoção de registros utilizando:

```sql
ON DELETE CASCADE
```

garantindo integridade referencial.

---

#  Tratamento de Erros

O sistema utiliza estruturas completas de tratamento de exceções:

```python
try
except
else
finally
```

Situações tratadas:

- Entradas inválidas;
- Conversões incorretas;
- Registros inexistentes;
- Chaves estrangeiras inválidas;
- Violações de integridade;
- Erros de banco de dados;
- Encerramento inesperado.

---

# 🔌 Circuitos Lógicos e Automação

## Regra Booleana Principal

```text
R = (E AND C) OR O OR (NOT V)
```

Onde:

| Variável | Significado |
|-----------|-------------|
| E | Consumo acima do limite |
| C | Módulo crítico |
| O | Oxigênio abaixo do mínimo |
| V | Sensor válido |
| R | Situação de risco |

---

## Interpretação

O sistema gera alertas quando:

- O consumo ultrapassa o limite permitido em módulos críticos.
- O nível de oxigênio fica abaixo do valor mínimo.
- Um sensor gera medições inválidas.
- O equipamento encontra-se inativo ou inconsistente.

---

## Atuadores Simulados

Quando a condição de risco é verdadeira:

```text
R = 1
```

são ativados:

- LED virtual de alarme;
- Buzzer virtual.

O circuito lógico foi representado graficamente em:

```text
circuito_logico.png
```

---

#  Estruturas de Dados

## Listas

Utilizadas para:

- Leituras;
- Resultados;
- Histórico de análises.

---

## Dicionários (Hash)

Utilizados para:

- Catálogo de sensores;
- Busca rápida de códigos;
- Metadados dos módulos.

Complexidade média:

```text
O(1)
```

---

## Heap de Prioridade

Implementa a fila de alertas.

Prioridades:

| Prioridade | Situação |
|------------|-----------|
| 1 | Oxigênio crítico |
| 2 | Sensor inválido |
| 3 | Consumo alto em módulo crítico |
| 4 | Consumo alto em módulo não crítico |

Complexidade:

```text
Inserção: O(log n)
Remoção: O(log n)
Consulta: O(1)
```

---

#  Simulação Computacional

A simulação representa o funcionamento energético da colônia durante um ciclo de 24 horas marcianas.

## Objetivos

Simular:

- Consumo energético;
- Geração solar;
- Estado de carga da bateria;
- Potência média;
- Energia acumulada.

---

## Variáveis Utilizadas

### Entrada

- Tempo (horas)
- Consumo
- Geração solar

### Saída

- Energia consumida
- Potência média
- Nível da bateria

---

## Integração Matemática

A energia total é determinada pela área sob a curva de potência.

### Método SciPy

```python
scipy.integrate.quad()
```

### Regra dos Trapézios

Implementação numérica manual para validação dos resultados.

---

## Indicadores Calculados

- Energia acumulada (kWh)
- Potência média (kW)
- Nível mínimo da bateria (%)
- Nível final da bateria (%)

---

#  Modelagem Linear

Foi desenvolvido um modelo de regressão linear simples.

## Variável Independente

```text
Temperatura
```

## Variável Dependente

```text
Consumo Energético
```

---

## Equação

```text
Consumo = b0 + b1 × Temperatura
```

---

## Métricas Utilizadas

- Correlação de Pearson;
- Coeficiente de Determinação (R²);
- Erro Quadrático Médio (MSE);
- Erro Absoluto Médio (MAE).

---

## Aplicação

O modelo permite:

- Estimar demanda energética futura;
- Detectar sobrecarga térmica;
- Apoiar decisões preventivas;
- Planejar a distribuição energética.

---

#  Inteligência Artificial Multiagente

O projeto propõe uma arquitetura composta por agentes especialistas.

## Agente Orquestrador

Coordena o fluxo de informações entre os demais agentes.

## Agente de Energia

Monitora consumo e geração energética.

## Agente Ambiental

Analisa temperatura, umidade e oxigênio.

## Agente de Dados

Valida a qualidade dos dados.

## Agente de Manutenção

Prioriza intervenções técnicas.

## Agente de Simulação

Avalia cenários futuros.

## Agente de Histórico

Mantém contexto operacional e registros de decisões.

---

#  Guardrails

A operação dos agentes é protegida por mecanismos de segurança.

Exemplos:

- Impedir desligamento de módulos críticos;
- Validar leituras antes das análises;
- Restringir acesso aos dados;
- Exigir aprovação humana para ações críticas.

---

#  Arquitetura Computacional

O projeto relaciona a solução com conceitos modernos de hardware.

## CPU

Responsável por:

- Banco de dados;
- CRUD;
- Regras lógicas;
- Menu interativo.

---

## GPU

Aplicável para:

- Simulações em larga escala;
- Processamento paralelo.

---

## NPU

Aplicável para:

- Inferência local de inteligência artificial;
- Detecção de padrões.

---

## TPU

Utilização conceitual para treinamento de modelos em data centers terrestres.

---

#  Computação Heterogênea

Proposta para expansão futura:

- Sensores → Microcontroladores;
- Servidor Local → CPU;
- IA Local → NPU;
- Processamento Pesado → GPU/TPU na Terra.

---

#  Hierarquia de Memória

```text
Registradores
↓
Cache
↓
RAM
↓
SSD
↓
Rede
```

O objetivo é minimizar movimentações desnecessárias de dados e reduzir o consumo energético.

---

#  Sustentabilidade

O sistema contribui para:

## Uso Responsável dos Recursos

Monitoramento contínuo de consumo.

## Simulação Preventiva

Redução de desperdícios.

## Redes Inteligentes

Maior autonomia da colônia.

## Resiliência Operacional

Funcionamento mesmo diante de falhas locais.

---

#  Cidadania Digital

O projeto considera:

- Privacidade dos dados;
- Transparência das decisões;
- Controle de acesso;
- Minimização de coleta de informações pessoais;
- Responsabilidade no uso da inteligência artificial.

---

#  Impacto Socioambiental

O sistema reconhece que:

- Data centers possuem impacto ambiental;
- Processamento intensivo consome energia;
- Modelos de IA devem ser utilizados com responsabilidade;
- A inovação deve sempre considerar seus impactos sociais e ambientais.

---

#  Como Executar

## Instalar Dependências

```bash
pip install numpy pandas matplotlib scipy scikit-learn
```

---

## Executar o Sistema

```bash
python main.py
```

---

#  Limitações

- Sensores simulados;
- Banco local SQLite;
- IA conceitual;
- Ambiente marciano simplificado;
- Ausência de hardware físico.

---

#  Trabalhos Futuros

- Integração com Arduino;
- Sensores IoT reais;
- Dashboard Web;
- Monitoramento em tempo real;
- Modelos de IA conectados ao banco;
- Computação distribuída;
- Redes inteligentes autônomas.

---

#  Conclusão

O Sistema Integrado de Futuro Sustentável em Marte (SIFSM) demonstra de forma integrada a aplicação de conceitos de programação, banco de dados, estruturas de dados, lógica computacional, circuitos digitais, modelagem matemática, simulação computacional, inteligência artificial e arquitetura de computadores.

A solução oferece suporte à operação da colônia Aurora Siger por meio do monitoramento inteligente de recursos, contribuindo para um futuro mais sustentável, resiliente e tecnologicamente eficiente em ambientes extraterrestres.