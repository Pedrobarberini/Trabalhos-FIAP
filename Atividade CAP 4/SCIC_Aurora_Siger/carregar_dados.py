"""Leitura validada, limpeza auditável e consultas dos dados da colônia."""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from configuracao import ARQUIVO_DADOS, COLUNAS, TIPOS_MODULO


@dataclass
class Carga:
    dados: pd.DataFrame
    rejeitados: pd.DataFrame
    linhas_originais: int
    duplicatas: int

    def resumo(self):
        return {
            'linhas_originais': self.linhas_originais,
            'duplicatas_removidas': self.duplicatas,
            'registros_rejeitados': len(self.rejeitados),
            'registros_validos': len(self.dados),
            'modulos': self.dados['nome_modulo'].nunique(),
            'ciclos': self.dados['ciclo'].nunique(),
        }


def carregar_base(caminho=ARQUIVO_DADOS):
    caminho = Path(caminho)
    df = pd.read_csv(caminho, encoding='utf-8-sig')
    ausentes = sorted(set(COLUNAS) - set(df.columns))
    if ausentes:
        raise ValueError('Colunas ausentes: ' + ', '.join(ausentes))
    if df.empty:
        raise ValueError('A base está vazia.')
    df = df[COLUNAS].copy()
    total = len(df)
    textos = ['nome_modulo', 'tipo_modulo', 'codigo_sensor', 'status', 'ciclo', 'mensagem_alerta']
    for coluna in textos:
        df[coluna] = df[coluna].fillna('').astype(str).str.strip()
    df['status'] = df['status'].str.lower()
    df['tipo_modulo'] = df['tipo_modulo'].str.lower()
    df['codigo_sensor'] = df['codigo_sensor'].str.upper().str.replace('0X', '0x', regex=False)
    df['ciclo'] = df['ciclo'].str.upper()
    numericas = ['id_registro', 'latencia_prevista_ms', 'latencia_observada_ms',
                 'tensao_v', 'corrente_a', 'potencia_w', 'prioridade']
    for coluna in numericas:
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce')
    df['data_registro'] = pd.to_datetime(df['data_registro'], format='%Y-%m-%d', errors='coerce')

    # Reenvios idênticos são removidos; um ID com conteúdos conflitantes é ambíguo.
    for identificador, grupo in df.groupby('id_registro'):
        if len(grupo.drop_duplicates()) > 1:
            raise ValueError(f'ID {identificador:g} repetido com dados conflitantes.')
    repetidos = df['id_registro'].notna() & df.duplicated('id_registro')
    duplicatas = int(repetidos.sum())
    df = df.loc[~repetidos].copy()
    motivos = pd.Series('', index=df.index, dtype=str)

    def invalidar(mascara, motivo):
        motivos.loc[mascara] += motivo + '; '

    for coluna in numericas:
        invalidar(~np.isfinite(df[coluna]), f'{coluna}: ausente ou não finito')
    invalidar((df['id_registro'] <= 0) | (df['id_registro'] % 1 != 0), 'ID deve ser inteiro positivo')
    invalidar(~df['prioridade'].between(1, 5) | (df['prioridade'] % 1 != 0), 'Prioridade deve ser inteira entre 1 e 5')
    for coluna in ['latencia_prevista_ms', 'latencia_observada_ms', 'tensao_v']:
        invalidar(df[coluna] <= 0, f'{coluna}: deve ser positivo')
    for coluna in ['corrente_a', 'potencia_w']:
        invalidar(df[coluna] < 0, f'{coluna}: não pode ser negativo')
    invalidar(~df['status'].isin(['ativo', 'manutencao', 'alerta']), 'Status desconhecido')
    invalidar(~df['tipo_modulo'].isin(TIPOS_MODULO), 'Tipo de módulo desconhecido')
    invalidar(df['nome_modulo'].eq(''), 'Nome do módulo vazio')
    invalidar(df['mensagem_alerta'].eq(''), 'Mensagem vazia')
    invalidar(df['data_registro'].isna(), 'Data inválida')
    invalidar(~df['codigo_sensor'].str.fullmatch(r'SNS-0x[0-9A-F]{4}'), 'Código de sensor inválido')
    invalidar(~df['ciclo'].str.fullmatch(r'C\d{3}') | df['ciclo'].eq('C000'), 'Ciclo inválido')

    rejeitados = df.loc[motivos.ne('')].copy()
    rejeitados['motivo_rejeicao'] = motivos.loc[rejeitados.index].str.rstrip('; ')
    validos = df.loc[motivos.eq('')].copy()
    if validos.empty:
        raise ValueError('Nenhuma leitura válida após a limpeza.')
    validos['id_registro'] = validos['id_registro'].astype(int)
    validos['prioridade'] = validos['prioridade'].astype(int)
    validos['numero_ciclo'] = validos['ciclo'].str[1:].astype(int)
    # Um sensor representa um único módulo; isso evita atribuições contraditórias.
    if (validos.groupby('codigo_sensor')['nome_modulo'].nunique() > 1).any():
        raise ValueError('O mesmo sensor está associado a módulos diferentes.')
    if validos.duplicated(['codigo_sensor', 'ciclo']).any():
        raise ValueError('Mais de uma leitura para o mesmo sensor e ciclo.')
    validos = validos.sort_values(['numero_ciclo', 'nome_modulo']).reset_index(drop=True)
    return Carga(validos, rejeitados.reset_index(drop=True), total, duplicatas)


def consultar_registros(df, modulo='', status='', prioridade_maxima=None):
    resultado = df
    if modulo:
        # Busca textual literal: caracteres como '[' não são expressões regulares.
        resultado = resultado[resultado['nome_modulo'].str.contains(modulo, case=False, regex=False)]
    if status:
        if status not in ('ativo', 'alerta', 'manutencao'):
            raise ValueError('Status deve ser ativo, alerta ou manutencao.')
        resultado = resultado[resultado['status'].eq(status)]
    if prioridade_maxima is not None:
        if prioridade_maxima not in range(1, 6):
            raise ValueError('Prioridade deve estar entre 1 e 5.')
        resultado = resultado[resultado['prioridade'] <= prioridade_maxima]
    return resultado.copy()


def resumo_por_tipo(df):
    return df.groupby('tipo_modulo').agg(
        registros=('id_registro', 'size'), modulos=('nome_modulo', 'nunique'),
        latencia_media_ms=('latencia_observada_ms', 'mean'),
        potencia_media_w=('potencia_w', 'mean'),
        taxa_alerta_pct=('status', lambda serie: 100 * serie.eq('alerta').mean()),
    ).sort_values('latencia_media_ms', ascending=False)
