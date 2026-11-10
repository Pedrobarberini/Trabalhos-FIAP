"""Portas lógicas puras do módulo de monitoramento da Aurora Siger."""
from itertools import product


def avaliar_portas(E: bool, C: bool, O: bool, V: bool) -> dict:
    """R = (E AND C) OR O OR (NOT V); recebe somente sinais booleanos."""
    sinais = {'E': E, 'C': C, 'O': O, 'V': V}
    if any(type(valor) is not bool for valor in sinais.values()):
        raise ValueError('As entradas E, C, O e V devem ser booleanas.')
    falha_sensor = not V
    excesso_em_critico = E and C
    risco = excesso_em_critico or O or falha_sensor
    return {**sinais, 'F': falha_sensor, 'EC': excesso_em_critico, 'R': risco}


def tabela_verdade() -> list[dict]:
    """Enumera as 16 combinações possíveis das quatro entradas digitais."""
    return [avaliar_portas(*sinais) for sinais in product((False, True), repeat=4)]
