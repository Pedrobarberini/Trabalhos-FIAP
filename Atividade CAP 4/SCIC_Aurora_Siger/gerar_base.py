"""Base original de 15 módulos, encapsulada para geração reproduzível sem efeito ao importar."""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from configuracao import ARQUIVO_DADOS, SEMENTE

MODULOS = [
    ("Antena Central Aurora",  "comunicacao",           120.0,   4.0,   48.0,    2.40,   1,   1.80),
    ("Relay Orbital Siger-1",  "comunicacao",           185.0,   9.0,   48.0,    3.10,   1,   0.00),
    ("Relay Orbital Siger-2",  "comunicacao",           190.0,   8.5,   48.0,    3.05,   2,   0.35),
    ("Nucleo de Dados Alfa",   "armazenamento_dados",    45.0,   3.0,   12.0,    5.20,   1,   0.00),
    ("Nucleo de Dados Beta",   "armazenamento_dados",    48.0,   3.2,   12.0,    5.05,   3,   0.90),
    ("Habitacao Norte",        "habitacao",              60.0,   5.0,   24.0,    1.80,   2,   0.00),
    ("Habitacao Sul",          "habitacao",              63.0,   5.5,   24.0,    1.75,   2,   0.00),
    ("Estufa Hidroponica 1",   "agricultura",            75.0,   6.0,   24.0,    2.20,   3,   0.00),
    ("Estufa Hidroponica 2",   "agricultura",            78.0,   6.5,   24.0,    2.15,   3,   0.55),
    ("Laboratorio Geologico",  "laboratorio",            95.0,   7.0,   24.0,    2.60,   4,   0.00),
    ("Laboratorio Biologico",  "laboratorio",            92.0,   6.8,   24.0,    2.55,   3,   0.00),
    ("Enfermaria Central",     "suporte_medico",         55.0,   4.0,   24.0,    3.40,   1,   0.00),
    ("Bloco Cirurgico",        "suporte_medico",         52.0,   3.8,   24.0,    3.60,   1,   0.00),
    ("Deposito Criogenico",    "armazenamento_dados",    70.0,   5.0,   12.0,    4.10,   4,   0.00),
    ("Oficina de Manutencao",  "laboratorio",           110.0,   8.0,   24.0,    2.90,   5,   0.00),
]

BASE_ID = 0x1A00


def codigo_sensor(indice_modulo):
    return "SNS-0x" + format(BASE_ID + indice_modulo + 1, "04X")


def classificar(latencia_obs, latencia_prev, prioridade, em_manutencao):
    """
    Define o status e a mensagem de alerta a partir do desvio de latencia.
    Regra do status de origem: ate 10% e nominal, acima de 10% e alerta,
    acima de 25% a mensagem indica desvio elevado. A analise usa outros limites.
    """
    if em_manutencao:
        return "manutencao", "Manutencao programada do enlace em andamento"

    desvio = abs(latencia_obs - latencia_prev) / latencia_prev

    if desvio > 0.25:
        return "alerta", "Desvio elevado da referencia - verificar enlace"
    if desvio > 0.10:
        return "alerta", "Desvio de latencia acima do limite operacional"
    if prioridade == 1 and latencia_obs > latencia_prev:
        return "ativo", "Enlace essencial com leve atraso - monitorar"
    return "ativo", "Operacao nominal"


def gerar_base(caminho=ARQUIVO_DADOS, ciclos=10):
    if not isinstance(ciclos, int) or not 5 <= ciclos <= 999:
        raise ValueError('Use entre cinco e 999 ciclos inteiros para manter o formato Cnnn.')
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEMENTE)
    registros = []
    id_registro = 1

    for indice, (nome, tipo, lat_base, ruido, tensao_nom, corrente_nom, prioridade, deriva) in enumerate(MODULOS):
        for ciclo in range(1, ciclos + 1):

            # Referencia nominal simulada, sem deriva ou interferencia conhecidas.
            latencia_prevista = lat_base + rng.normal(0, ruido * 0.30)

            # Latencia medida pelo sensor: base + deriva acumulada + ruido
            latencia_observada = lat_base + deriva * (ciclo - 1) + rng.normal(0, ruido)

            # Em ~4% dos registros ocorre um evento raro de interferencia, que
            # multiplica a latencia (tempestade solar, alinhamento orbital ruim)
            if rng.random() < 0.04:
                latencia_observada = latencia_observada * rng.uniform(1.6, 2.4)

            # Grandezas eletricas, usadas tambem na etapa 1.6
            tensao = tensao_nom + rng.normal(0, 0.4)
            corrente = corrente_nom + rng.normal(0, 0.08)
            potencia = tensao * corrente  # P = V x I

            em_manutencao = rng.random() < 0.06
            status, mensagem = classificar(latencia_observada, latencia_prevista, prioridade, em_manutencao)

            data = pd.Timestamp("2026-03-01") + pd.Timedelta(days=7 * (ciclo - 1))

            registros.append({
                "id_registro": id_registro,
                "ciclo": "C" + format(ciclo, "03d"),
                "data_registro": data.strftime("%Y-%m-%d"),
                "nome_modulo": nome,
                "tipo_modulo": tipo,
                "codigo_sensor": codigo_sensor(indice),
                "latencia_prevista_ms": round(latencia_prevista, 2),
                "latencia_observada_ms": round(latencia_observada, 2),
                "tensao_v": round(tensao, 2),
                "corrente_a": round(corrente, 3),
                "potencia_w": round(potencia, 2),
                "status": status,
                "prioridade": prioridade,
                "mensagem_alerta": mensagem,
            })
            id_registro += 1

    df = pd.DataFrame(registros)

    # Insere de proposito 3 problemas comuns em telemetria, para depois praticar
    # limpeza de dados com Pandas em carregar_dados.py:
    #   (a) leituras faltantes de sensor
    #   (b) status com espacos e maiusculas
    #   (c) registros duplicados (reenvio do mesmo pacote)

    indices_faltantes = rng.choice(df.index, size=6, replace=False)
    df.loc[indices_faltantes, "latencia_observada_ms"] = np.nan

    indices_sujos = rng.choice(df.index, size=10, replace=False)
    df.loc[indices_sujos, "status"] = df.loc[indices_sujos, "status"].str.upper() + " "

    duplicados = df.sample(4, random_state=SEMENTE)
    df = pd.concat([df, duplicados], ignore_index=True)

    # Embaralha as linhas para os duplicados nao ficarem todos no final do arquivo
    df = df.sample(frac=1, random_state=SEMENTE).reset_index(drop=True)

    df.to_csv(caminho, index=False, encoding='utf-8')
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gera a base simulada da Aurora Siger.')
    parser.add_argument('--saida', type=Path, required=True, help='CSV de destino; o caminho é obrigatório para evitar sobrescrita acidental.')
    parser.add_argument('--ciclos', type=int, default=10)
    args = parser.parse_args()
    base = gerar_base(args.saida, args.ciclos)
    print(f'Base gravada: {args.saida} | {len(base)} linhas | {base.nome_modulo.nunique()} módulos')
