"""Regressão linear simples com validação cronológica e teste reservado."""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ATRIBUTOS = ['latencia_prevista_ms', 'numero_ciclo']
ALVO = 'latencia_observada_ms'


def metricas(observado, previsto):
    observado, previsto = np.asarray(observado), np.asarray(previsto)
    mse = mean_squared_error(observado, previsto)
    # R² não é informativo para um único valor ou alvo constante.
    r2 = float(r2_score(observado, previsto)) if len(observado) >= 2 and np.ptp(observado) > 0 else None
    return {'mae_ms': float(mean_absolute_error(observado, previsto)),
            'mse_ms2': float(mse), 'rmse_ms': float(np.sqrt(mse)), 'r2': r2}


def separar_temporal(df):
    ciclos = sorted(df['numero_ciclo'].unique())
    if len(ciclos) < 5:
        raise ValueError('A avaliação temporal exige pelo menos cinco ciclos diferentes.')
    ordem = df.groupby('numero_ciclo')['data_registro'].agg(['min', 'max']).loc[ciclos]
    if any(ordem.iloc[index]['max'] >= ordem.iloc[index + 1]['min'] for index in range(len(ordem) - 1)):
        raise ValueError('Datas sobrepostas entre ciclos impedem a separação temporal.')
    fim_treino = max(1, int(len(ciclos) * 0.6))
    fim_validacao = max(fim_treino + 1, int(len(ciclos) * 0.8))
    grupos = [ciclos[:fim_treino], ciclos[fim_treino:fim_validacao], ciclos[fim_validacao:]]
    return tuple(df[df['numero_ciclo'].isin(grupo)].copy() for grupo in grupos)


@dataclass
class Avaliacao:
    modelo: LinearRegression
    preferido: str
    resumo: dict
    teste: pd.DataFrame

    def prever(self, entradas):
        if self.preferido == 'referencia':
            return entradas['latencia_prevista_ms'].to_numpy()
        return self.modelo.predict(entradas[ATRIBUTOS])


def avaliar_modelo(df):
    treino, validacao, teste = separar_temporal(df)
    modelo = LinearRegression()
    modelo.fit(treino[ATRIBUTOS], treino[ALVO])
    val_linear = metricas(validacao[ALVO], modelo.predict(validacao[ATRIBUTOS]))
    val_referencia = metricas(validacao[ALVO], validacao['latencia_prevista_ms'])
    preferido = 'regressao_linear' if val_linear['rmse_ms'] < val_referencia['rmse_ms'] else 'referencia'
    # A escolha usa apenas validação. O teste não participa do ajuste nem da seleção.
    ajuste_final = pd.concat([treino, validacao], ignore_index=True)
    modelo.fit(ajuste_final[ATRIBUTOS], ajuste_final[ALVO])
    teste = teste.copy()
    teste['previsao_regressao_ms'] = modelo.predict(teste[ATRIBUTOS])
    resumo = {
        'atributos': ATRIBUTOS, 'alvo': ALVO, 'preferido_na_validacao': preferido,
        'particoes': {nome: {'registros': len(parte), 'ciclos': sorted(parte['ciclo'].unique().tolist())}
                      for nome, parte in [('treino', treino), ('validacao', validacao), ('teste', teste)]},
        'validacao': {'regressao_linear': val_linear, 'referencia': val_referencia},
        'teste': {'regressao_linear': metricas(teste[ALVO], teste['previsao_regressao_ms']),
                  'referencia': metricas(teste[ALVO], teste['latencia_prevista_ms'])},
        'coeficientes': dict(zip(ATRIBUTOS, map(float, modelo.coef_))),
        'intercepto': float(modelo.intercept_),
    }
    return Avaliacao(modelo, preferido, resumo, teste)


def prever_proximo_ciclo(df, avaliacao):
    # Simulação de um único ciclo adiante, mantendo a referência nominal mais recente.
    entradas = df.sort_values('numero_ciclo').groupby('codigo_sensor', as_index=False).tail(1).copy()
    entradas['numero_ciclo'] = int(df['numero_ciclo'].max()) + 1
    entradas['ciclo'] = entradas['numero_ciclo'].map(lambda valor: f'C{valor:03d}')
    entradas['estimativa_proximo_ciclo_ms'] = avaliacao.prever(entradas)
    entradas['metodo'] = avaliacao.preferido
    entradas['previsao_fisicamente_valida'] = entradas['estimativa_proximo_ciclo_ms'] > 0
    return entradas[['nome_modulo', 'codigo_sensor', 'ciclo', 'latencia_prevista_ms',
                     'estimativa_proximo_ciclo_ms', 'metodo', 'previsao_fisicamente_valida']].reset_index(drop=True)
