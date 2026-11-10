# Parte 3: Simulação Computacional e Modelagem Linear

Parte desenvolvida referente à  **Simulação Computacional e ModelagemIntegração Matemática**. O código está integrado ao menu principal (`main.py`) via opção 7 e ao banco SQLite (`aurora_siger.db`).

---

## 1. Visão Geral do Módulo

O arquivo `parte3_simulacao.py` implementa duas frentes analíticas para a sustentabilidade e resiliência da colônia:
1. **Simulação Computacional e Integração Matemática:** Modelagem temporal de 24h marcianas para consumo energético, geração solar, cálculo de energia acumulada por integração/trapézios, potência média e dinâmica do nível de carga da bateria.
2. **Modelagem Linear para Tomada de Decisão:** Regressão linear supervisionada correlacionando temperatura dos módulos e demanda de energia para climatização/suporte à vida, com avaliação por $R^2$, MSE, MAE e regra de apoio à decisão operacional.

---

## 2. Simulação Computacional e Integração Matemática

### Fenômeno Representado
A colônia opera em ciclos diários de 24 horas marcianas (sol). O sistema elétrico precisa equilibrar:
* Carga contínua ininterrupta de suporte à vida (oxigênio, pressurização, controle térmico);
* Pico de demanda diurna com a tripulação ativa em laboratórios e agricultura;
* Geração solar restrita ao período diurno (janela de 6h às 18h);
* Ciclos de carga e descarga do banco de baterias central.

### Formulação Matemática

1. **Curva Contínua de Consumo Instantâneo $P(t)$:**
   $$P(t) = P_{\text{base}} + P_{\text{atividade}} \cdot \sin^2\left(\frac{\pi t}{24}\right) + P_{\text{flutuação}} \cdot \sin\left(\frac{2\pi t}{6}\right)$$
   * $P_{\text{base}} = 35{,}0\text{ kW}$ (demanda mínima vital);
   * $P_{\text{atividade}} = 15{,}0\text{ kW}$ (acréscimo operacional no expediente diurno);
   * $P_{\text{flutuação}} = 3{,}0\text{ kW}$ (acionamento ocasional de bombas e outros equipamentos).

2. **Cálculo da Energia Total Consumida ($E$):**
   A energia acumulada ao longo de 24 horas corresponde à área sob a curva de potência:
   $$E = \int_{0}^{24} P(t)\,dt$$
   * **Método 1 (SciPy):** integração adaptativa por integração numérica com `scipy.integrate.quad`.
   * **Método 2 (Trapézios):** implementação manual da regra dos trapézios com $n = 96$ intervalos ($\Delta t = 15\text{ min}$):
     $$E \approx \frac{h}{2} \left[ P(t_0) + 2 \sum_{i=1}^{n-1} P(t_i) + P(t_n) \right]$$
   * **Comparação:** o erro entre os dois métodos é inferior a $10^{-5}\text{ kWh}$, validando a precisão da discretização.

3. **Potência Média Diária ($P_{\text{médio}}$):**
   $$P_{\text{médio}} = \frac{1}{24 - 0} \int_{0}^{24} P(t)\,dt \approx 42{,}50\text{ kW}$$

4. **Nível da Bateria:**
   Capacidade nominal do banco de baterias: $C_{\text{bat}} = 1.200\text{ kWh}$. Nível inicial: $95{,}00\%$.
   $$\text{Nível}(t) = \text{Nível}(t_0) + \frac{1}{C_{\text{bat}}} \int_{t_0}^{t} \left( P_{\text{solar}}(\tau) - P_{\text{consumo}}(\tau) \right) d\tau$$
   O código monitora a reserva e plota uma linha crítica em $20{,}00\%$ (nível crítico de segurança).

### Variáveis Utilizadas
* `t`: tempo contínuo no ciclo de 24h marcianas (horas).
* `P(t)`: potência instantânea de consumo total da base (kW).
* `P_solar(t)`: potência gerada pelo campo fotovoltaico (kW).
* `energia_quad` / `energia_trapezio`: energia total integrada (kWh).
* `potencia_media`: taxa média contínua de consumo (kW).
* `curva_nivel`: evolução percentual da carga da bateria ao longo do dia (%).

### Limitações da Simulação
* A insolação marciana assume céu limpo sem tempestades de poeira sazonais, que poderiam reduzir drasticamente a radiação solar.

---

## 3. Modelagem Linear para Tomada de Decisão

### Justificativa da Relação Escolhida
A modelagem linear simples relaciona a **Temperatura Interna dos Módulos (°C)** com a **Demanda Energética de Climatização (kW)**. 
Em Marte, o ambiente externo extremamente hostil exige que os sistemas de controle térmico (HVAC) aumentem linearmente o consumo para cada grau de dissipação térmica interna e externa, tornando a relação linear física e estatisticamente válida.

### Origem dos Dados e Integração com SQLite
* O script executa uma query SQL cruzando as tabelas `leituras` e `sensores` do banco `aurora_siger.db`:
  * Sensor do tipo `temperatura` (`SEN-LAB-TP`);
  * Sensor do tipo `consumo` (`SEN-ENE-01`).
* **Tratamento de contingência:** se a base de dados contiver poucas amostras, o código gera $N = 60$ observações amostrais realistas baseadas na faixa operacional dos módulos ($15^\circ\text{C}$ a $30^\circ\text{C}$), garantindo a execução do modelo sem interrupções.

### Equação do Modelo e Interpretação dos Coeficientes
O ajuste foi realizado com a classe `LinearRegression` da biblioteca `scikit-learn`:
$$\text{Consumo (kW)} = \beta_0 + \beta_1 \cdot \text{Temperatura (°C)}$$
* **Intercepto ($\beta_0 \approx 12{,}00\text{ kW}$):** consumo elétrico basal dos sistemas de bombeamento e sensores de controle térmico, mesmo quando a temperatura se aproxima de zero.
* **Coeficiente Angular ($\beta_1 \approx 1{,}65\text{ kW/°C}$):** para cada $1^\circ\text{C}$ de aumento térmico no módulo, o sistema de refrigeração/climatização demanda em média mais $1{,}65\text{ kW}$ de potência da rede elétrica da colônia.

### Métricas de Avaliação
* **$R^2$ (Coeficiente de Determinação $\approx 0{,}85$):** indica que cerca de $85\%$ da variabilidade do consumo elétrico é explicada diretamente pela temperatura ambiente dos módulos.
* **MSE (Erro Quadrático Médio $\approx 3{,}20$):** penaliza desvios maiores, confirmando ausência de dispersões extremas.
* **MAE (Erro Absoluto Médio $\approx 1{,}45\text{ kW}$):** erro médio da projeção para mais ou para menos.

### Apoio à Tomada de Decisão
O modelo projeta a demanda esperada para cenários de estresse térmico (ex.: $28{,}0^\circ\text{C}$):
* Projeção calculada: $\approx 58{,}20\text{ kW}$.
* Regra implementada: se a demanda ultrapassar o teto operacional ($55{,}0\text{ kW}$), o sistema emite no terminal:
  ```text
  [Aviso] Projeção de sobrecarga térmica no módulo. Redirecionar potência auxiliar.
  ```
Isso permite aos operadores remanejar fontes ou acionar geradores auxiliares antes que ocorra algum dano aos módulos habitacionais.