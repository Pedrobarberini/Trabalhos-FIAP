"""Sensores virtuais, validação de entradas e comparadores do circuito."""
from dataclasses import asdict, dataclass
import math
import re

from .logica_risco import avaliar_portas


def texto_identificador(valor, campo):
    if not isinstance(valor, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', valor):
        raise ValueError(f'{campo}: use de 1 a 64 letras, números, _ ou hífen.')
    return valor


def numero_finito(valor):
    return type(valor) in (int, float) and math.isfinite(valor)


@dataclass(frozen=True)
class Sensor:
    codigo: str
    modulo: str
    critico: bool
    limite_consumo_kwh: float
    minimo_oxigenio_pct: float
    monitorar_consumo: bool = True
    monitorar_oxigenio: bool = True

    def __post_init__(self):
        texto_identificador(self.codigo, 'Código do sensor')
        if not isinstance(self.modulo, str) or not self.modulo.strip():
            raise ValueError('O nome do módulo deve estar preenchido.')
        if type(self.critico) is not bool:
            raise ValueError('A criticidade do módulo deve ser booleana.')
        if type(self.monitorar_consumo) is not bool or type(self.monitorar_oxigenio) is not bool:
            raise ValueError('A seleção dos canais deve ser booleana.')
        if not self.monitorar_consumo and not self.monitorar_oxigenio:
            raise ValueError('O sensor precisa monitorar consumo ou oxigênio.')
        if not numero_finito(self.limite_consumo_kwh) or self.limite_consumo_kwh <= 0:
            raise ValueError('O limite de consumo deve ser positivo e finito.')
        if not numero_finito(self.minimo_oxigenio_pct) or not 0 < self.minimo_oxigenio_pct <= 100:
            raise ValueError('O limite mínimo de oxigênio deve estar entre 0 e 100, excluindo zero.')

    @classmethod
    def de_dict(cls, dados):
        if not isinstance(dados, dict):
            raise ValueError('Cada sensor deve ser um objeto JSON.')
        try:
            obrigatorios = ('codigo', 'modulo', 'critico', 'limite_consumo_kwh', 'minimo_oxigenio_pct')
            argumentos = {campo: dados[campo] for campo in obrigatorios}
            for canal in ('monitorar_consumo', 'monitorar_oxigenio'):
                if canal in dados:
                    argumentos[canal] = dados[canal]
            return cls(**argumentos)
        except KeyError as erro:
            raise ValueError(f'Campo do sensor ausente: {erro.args[0]}.') from erro


@dataclass(frozen=True)
class Leitura:
    id: str
    codigo_sensor: str
    ciclo: int
    consumo_kwh: float | None
    oxigenio_pct: float | None
    sensor_valido: bool

    def __post_init__(self):
        texto_identificador(self.id, 'ID da leitura')
        texto_identificador(self.codigo_sensor, 'Código do sensor')
        if type(self.ciclo) is not int or self.ciclo < 1:
            raise ValueError('O ciclo deve ser um inteiro positivo.')
        if type(self.sensor_valido) is not bool:
            raise ValueError('sensor_valido deve ser true ou false.')
        for campo in ('consumo_kwh', 'oxigenio_pct'):
            valor = getattr(self, campo)
            if valor is not None and not numero_finito(valor):
                raise ValueError(f'{campo}: informe um número finito ou null para ausência de medição.')

    @classmethod
    def de_dict(cls, dados):
        if not isinstance(dados, dict):
            raise ValueError('Cada leitura deve ser um objeto JSON.')
        try:
            return cls(**{campo: dados[campo] for campo in cls.__dataclass_fields__})
        except KeyError as erro:
            raise ValueError(f'Campo da leitura ausente: {erro.args[0]}.') from erro


@dataclass(frozen=True)
class Resultado:
    leitura: Leitura
    modulo: str
    sinais: tuple[tuple[str, bool], ...]
    classificacao: str
    prioridade: int | None
    motivos: tuple[str, ...]
    led_alarme: bool
    buzzer: bool
    indicador_atencao: bool

    def para_dict(self):
        resultado = asdict(self)
        resultado['sinais'] = dict(self.sinais)
        return resultado


def avaliar_leitura(sensor: Sensor, leitura: Leitura) -> Resultado:
    if sensor.codigo != leitura.codigo_sensor:
        raise ValueError('A leitura não corresponde ao sensor informado.')
    consumo_valido = leitura.consumo_kwh is not None and leitura.consumo_kwh >= 0
    oxigenio_valido = leitura.oxigenio_pct is not None and 0 <= leitura.oxigenio_pct <= 100
    valido = (leitura.sensor_valido
              and (not sensor.monitorar_consumo or consumo_valido)
              and (not sensor.monitorar_oxigenio or oxigenio_valido))
    # Um canal ausente não recebe zero. Um sensor declarado inválido não valida seus valores.
    energia_alta = bool(sensor.monitorar_consumo and leitura.sensor_valido and consumo_valido
                        and leitura.consumo_kwh > sensor.limite_consumo_kwh)
    oxigenio_critico = bool(sensor.monitorar_oxigenio and leitura.sensor_valido and oxigenio_valido
                            and leitura.oxigenio_pct < sensor.minimo_oxigenio_pct)
    sinais = avaliar_portas(energia_alta, sensor.critico, oxigenio_critico, valido)
    motivos = []
    if not leitura.sensor_valido:
        motivos.append('Sensor informou estado inválido; valores não utilizados pelos comparadores.')
    if sensor.monitorar_consumo and not consumo_valido:
        motivos.append('Medição de consumo ausente ou negativa.')
    if sensor.monitorar_oxigenio and not oxigenio_valido:
        motivos.append('Medição de oxigênio ausente ou fora do intervalo de 0 a 100%.')
    if oxigenio_critico:
        motivos.append(f'Oxigênio de {leitura.oxigenio_pct:g}% abaixo de {sensor.minimo_oxigenio_pct:g}%.')
    if energia_alta:
        motivos.append(f'Consumo de {leitura.consumo_kwh:g} kWh acima de '
                       f'{sensor.limite_consumo_kwh:g} kWh por ciclo; módulo '
                       + ('crítico.' if sensor.critico else 'não crítico.'))

    # A ordem de urgência é separada da avaliação booleana do circuito.
    if oxigenio_critico:
        prioridade = 1
    elif not valido:
        prioridade = 2
    elif energia_alta and sensor.critico:
        prioridade = 3
    elif energia_alta:
        prioridade = 4
    else:
        prioridade = None
    atencao = prioridade == 4
    classificacao = 'critico' if sinais['R'] else 'atencao' if atencao else 'normal'
    return Resultado(leitura, sensor.modulo, tuple(sinais.items()), classificacao, prioridade,
                     tuple(motivos or ['Medições dentro dos limites da simulação.']),
                     sinais['R'], sinais['R'], atencao)
