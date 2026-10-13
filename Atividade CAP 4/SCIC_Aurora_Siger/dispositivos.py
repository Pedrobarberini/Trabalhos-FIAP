"""Bases numéricas e eletricidade aplicadas aos transmissores simulados."""
import re


def converter_sensor(codigo):
    if not isinstance(codigo, str) or not re.fullmatch(r'SNS-0x[0-9A-Fa-f]{4}', codigo):
        raise ValueError('Use um código como SNS-0x1A01.')
    decimal = int(codigo.split('0x')[1], 16)
    return {'codigo': codigo, 'decimal': decimal, 'binario': format(decimal, '016b'),
            'hexadecimal': f'0x{decimal:04X}'}


def exemplo_eletrico(linha):
    tensao, corrente = float(linha['tensao_v']), float(linha['corrente_a'])
    potencia = tensao * corrente
    return {'modulo': linha['nome_modulo'], 'sensor': converter_sensor(linha['codigo_sensor']),
            'tensao_v': tensao, 'corrente_a': corrente, 'potencia_calculada_w': potencia,
            'potencia_gravada_w': float(linha['potencia_w']),
            'resistencia_equivalente_ohm': tensao / corrente if corrente > 0 else None}
