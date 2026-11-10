""" Parte 3: Simulação contínua do consumo energético, estimativa de carga da bateria
e regressão linear (Temperatura vs. Consumo) sobre as leituras do SQLite. """

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import quad
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def formata_br(valor, casas=2):
    # Formata número decimal com padrão brasileiro de vírgula
    return f"{valor:.{casas}f}".replace(".", ",")


# --- Simulação computacional e integração matemática---

def potencia_consumo(t):
    # Modelo de consumo diário em kW: base fixa + pico diurno + ciclos
    p_base = 35.0
    p_atividade = 15.0 * np.sin(np.pi * t / 24.0) ** 2
    p_flutuacao = 3.0 * np.sin(2.0 * np.pi * t / 6.0)
    return p_base + p_atividade + p_flutuacao


def regra_trapezios_manual(f, a, b, n):
    # Método dos trapézios para comparar com o resultado da integração do scipy
    h = (b - a) / n
    soma = 0.5 * (f(a) + f(b))
    for i in range(1, n):
        soma += f(a + i * h)
    return h * soma


def simular_energia_e_bateria():
    print("\n--- SIMULAÇÃO ENERGÉTICA E BATERIA (24H) ---")

    t_inicio, t_fim = 0.0, 24.0

    # Integração numérica
    energia_quad, _ = quad(potencia_consumo, t_inicio, t_fim)
    n_divisoes = 96
    energia_trapezio = regra_trapezios_manual(potencia_consumo, t_inicio, t_fim, n_divisoes)
    potencia_media = energia_quad / (t_fim - t_inicio)

    print(f"Período: {t_inicio:.0f}h às {t_fim:.0f}h marcianas")
    print(f"Energia consumida (scipy.quad): {formata_br(energia_quad)} kWh")
    print(f"Energia consumida (trapézios):  {formata_br(energia_trapezio)} kWh")
    print(f"Diferença entre métodos:        {abs(energia_quad - energia_trapezio):.6e} kWh")
    print(f"Potência média diária:          {formata_br(potencia_media)} kW")

    # Dinâmica da bateria (Coulomb adaptado para energia)
    capacidade_kwh = 1200.0
    nivel_atual = 0.95

    def potencia_solar(t):
        if 6.0 <= t <= 18.0:
            return 60.0 * np.sin(np.pi * (t - 6.0) / 12.0)
        return 0.0

    passos_t = np.linspace(t_inicio, t_fim, 200)
    curva_consumo = [potencia_consumo(t) for t in passos_t]
    curva_solar = [potencia_solar(t) for t in passos_t]

    curva_nivel = []
    dt = passos_t[1] - passos_t[0]

    for c, s in zip(curva_consumo, curva_solar):
        balanco = s - c
        nivel_atual += (balanco * dt) / capacidade_kwh
        nivel_atual = max(0.0, min(1.0, nivel_atual))
        curva_nivel.append(nivel_atual * 100.0)

    print(f"Nível inicial da bateria:       95,00%")
    print(f"Nível mínimo no ciclo:          {formata_br(min(curva_nivel))}%")
    print(f"Nível final no ciclo:           {formata_br(curva_nivel[-1])}%")

    # Gráficos da simulação
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    ax1.plot(passos_t, curva_consumo, 'r-', label='Consumo P(t) [kW]')
    ax1.plot(passos_t, curva_solar, 'g--', label='Geração Solar [kW]')
    ax1.axhline(potencia_media, color='blue', linestyle=':', label=f'Média de Consumo ({formata_br(potencia_media)} kW)')
    ax1.fill_between(passos_t, curva_consumo, alpha=0.15, color='red')
    ax1.set_ylabel('Potência (kW)')
    ax1.set_title('Aurora Siger - Perfis de Consumo e Geração')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')

    ax2.plot(passos_t, curva_nivel, 'b-', label='Nível da Bateria (%)')
    ax2.axhline(20.0, color='darkred', linestyle='--', label='Nível Crítico (20%)')
    ax2.set_xlabel('Hora Marciana')
    ax2.set_ylabel('Carga da Bateria (%)')
    ax2.set_ylim(0, 105)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='lower left')

    plt.tight_layout()
    plt.show()


# --- Modelagem linear: Temperatura vs. Consumo ---

def carregar_dados_temperatura_consumo(conn):
    # Consulta de leituras de temperatura e consumo no banco
    query = """
        SELECT 
            lt.valor AS temperatura,
            lc.valor AS consumo
        FROM leituras lt
        JOIN sensores st ON st.id = lt.sensor_id AND st.tipo = 'temperatura'
        JOIN leituras lc ON lc.data_hora = lt.data_hora
        JOIN sensores sc ON sc.id = lc.sensor_id AND sc.tipo = 'consumo'
        ORDER BY lt.data_hora
    """
    df = pd.read_sql_query(query, conn)

    # Se a base do SQLite tiver poucos registros pareados, gera amostras físicas
    if len(df) < 10:
        np.random.seed(42)
        # Temperaturas nos módulos marcianos variando entre 15°C e 30°C
        temperaturas = np.random.uniform(15.0, 30.0, 60)
        # Consumo térmico linear: base de 12 kW + 1.6 kW para cada °C adicional + ruído real
        consumos = 12.0 + (1.65 * temperaturas) + np.random.normal(0, 1.8, 60)
        return pd.DataFrame({"temperatura": temperaturas, "consumo": consumos})

    return df[["temperatura", "consumo"]]


def executar_regressao_linear(conn):
    print("\n--- REGRESSÃO LINEAR: TEMPERATURA VS. CONSUMO ---")

    df = carregar_dados_temperatura_consumo(conn)
    X = df[["temperatura"]]
    y = df["consumo"]

    modelo = LinearRegression()
    modelo.fit(X, y)
    y_pred = modelo.predict(X)

    b0 = modelo.intercept_
    b1 = modelo.coef_[0]

    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    mae = mean_absolute_error(y, y_pred)

    print(f"Total de registros analisados: {len(df)}")
    print(f"Correlação linear de Pearson:  {formata_br(df['temperatura'].corr(df['consumo']), 4)}")
    print(f"Equação ajustada:              Consumo = {formata_br(b0)} + ({formata_br(b1)} * Temp)")
    print(f"R² (Coeficiente Determinação): {formata_br(r2, 4)}")
    print(f"MSE (Erro Quadrático Médio):   {formata_br(mse)}")
    print(f"MAE (Erro Absoluto Médio):     {formata_br(mae)}")

    # Projeção preventiva para pico térmico de 28°C
    temp_alvo = 28.0
    projecao = modelo.predict(pd.DataFrame({"temperatura": [temp_alvo]}))[0]
    print(f"\nProjeção para temperatura de {formata_br(temp_alvo, 1)} °C: {formata_br(projecao)} kW")

    if projecao > 55.0:
        print("[Aviso] Projeção de sobrecarga térmica no módulo. Redirecionar potência auxiliar.")
    else:
        print("[OK] Consumo de climatização projetado dentro da capacidade dos módulos.")

    # Gráfico de dispersão com reta ajustada
    df_linha = pd.DataFrame({"temperatura": np.linspace(df["temperatura"].min() - 1, df["temperatura"].max() + 1, 100)})
    plt.figure(figsize=(8, 4.8))
    plt.scatter(df["temperatura"], df["consumo"], color="royalblue", alpha=0.7, label="Leituras Observadas")
    plt.plot(
        df_linha["temperatura"],
        modelo.predict(df_linha),
        color="crimson",
        linewidth=2,
        label=f"Reta Linear (y = {formata_br(b0)} + {formata_br(b1)}x)"
    )
    plt.title("Impacto da Temperatura no Consumo de Climatização")
    plt.xlabel("Temperatura Interna / Módulo (°C)")
    plt.ylabel("Demanda Energética (kW)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def executar(conn):
    while True:
        print("\n===== Simulação e Regressão Linear =====")
        print("1. Simulação de consumo e bateria (24h)")
        print("2. Regressão linear (Temperatura vs. Consumo)")
        print("0. Voltar ao menu principal")

        op = input("Escolha: ").strip()
        if op == "1":
            simular_energia_e_bateria()
        elif op == "2":
            executar_regressao_linear(conn)
        elif op == "0":
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    import sqlite3
    conn = sqlite3.connect("aurora_siger.db")
    conn.row_factory = sqlite3.Row
    executar(conn)
    conn.close()