"""Erros, precisão e interpretação operacional dos registros válidos."""
import math

import numpy as np

from configuracao import LIMITE_ACEITAVEL, LIMITE_ATENCAO, PISO_LATENCIA_MS


def calcular_erros(df):
    resultado = df.copy()
    # Mantém precisão integral nos cálculos. O arredondamento ocorre na apresentação.
    resultado['desvio_ms'] = resultado['latencia_prevista_ms'] - resultado['latencia_observada_ms']
    resultado['erro_absoluto_ms'] = resultado['desvio_ms'].abs()
    denominador = resultado['latencia_observada_ms'].abs().where(
        resultado['latencia_observada_ms'].abs() >= PISO_LATENCIA_MS
    )
    resultado['erro_relativo'] = resultado['erro_absoluto_ms'] / denominador
    resultado['erro_percentual'] = 100 * resultado['erro_relativo']
    resultado['classificacao_erro'] = np.select(
        [resultado['erro_relativo'].isna(),
         resultado['erro_relativo'] <= LIMITE_ACEITAVEL,
         resultado['erro_relativo'] <= LIMITE_ATENCAO],
        ['indefinido', 'aceitavel', 'atencao'], default='critico',
    )
    # Erro de previsão e degradação são diferentes: redução de latência também gera erro.
    resultado['degradacao'] = (
        (resultado['latencia_observada_ms'] > resultado['latencia_prevista_ms'])
        & resultado['classificacao_erro'].eq('critico')
    )
    return resultado


def indicadores(df):
    media_relativa = df['erro_percentual'].mean()
    return {
        'latencia_media_ms': float(df['latencia_observada_ms'].mean()),
        'latencia_p95_ms': float(df['latencia_observada_ms'].quantile(0.95)),
        'erro_absoluto_medio_ms': float(df['erro_absoluto_ms'].mean()),
        'erro_absoluto_mediano_ms': float(df['erro_absoluto_ms'].median()),
        'erro_absoluto_maximo_ms': float(df['erro_absoluto_ms'].max()),
        'erro_relativo_medio_pct': float(media_relativa) if np.isfinite(media_relativa) else None,
        'erros_criticos': int(df['classificacao_erro'].eq('critico').sum()),
        'degradacoes_criticas': int(df['degradacao'].sum()),
        'alertas_informados': int(df['status'].eq('alerta').sum()),
        'manutencoes': int(df['status'].eq('manutencao').sum()),
        'leituras_relativo_indefinido': int(df['classificacao_erro'].eq('indefinido').sum()),
    }


def erros_por_modulo(df):
    return df.groupby('nome_modulo').agg(
        erro_medio_ms=('erro_absoluto_ms', 'mean'),
        erro_percentual_medio=('erro_percentual', 'mean'),
        criticos=('classificacao_erro', lambda serie: int(serie.eq('critico').sum())),
    ).sort_values('erro_percentual_medio', ascending=False)


def verificar_potencia(df):
    calculada = df['tensao_v'] * df['corrente_a']
    diferenca = (calculada - df['potencia_w']).abs()
    # V tem resolução 0,01 V, I 0,001 A e P 0,01 W. Limite propagado de arredondamento.
    tolerancia = 0.005 * df['corrente_a'].abs() + 0.0005 * df['tensao_v'].abs() + 0.005 * 0.0005 + 0.005
    return {
        'registros': len(df), 'coerentes': int((diferenca <= tolerancia + 1e-12).sum()),
        'incoerentes': int((diferenca > tolerancia + 1e-12).sum()),
        'diferenca_media_w': float(diferenca.mean()),
        'diferenca_maxima_w': float(diferenca.max()),
        'tolerancia_maxima_w': float(tolerancia.max()),
    }


def precisao_numerica(df):
    latencias = df['latencia_observada_ms'].tolist()
    relativos = df['erro_percentual'].dropna()
    mediana_relativa = float(relativos.median()) if not relativos.empty else None
    return {
        'soma_decimal': 0.1 + 0.2,
        'igualdade_exata': 0.1 + 0.2 == 0.3,
        'igualdade_com_tolerancia': math.isclose(0.1 + 0.2, 0.3),
        'soma_direta': sum(latencias), 'soma_inversa': sum(reversed(latencias)),
        'soma_compensada': math.fsum(latencias),
        'menor_latencia_ms': min(latencias),
        'erro_resolucao_maximo_pct': 100 * 0.005 / min(latencias),
        'desvio_mediano_pct': mediana_relativa,
    }
