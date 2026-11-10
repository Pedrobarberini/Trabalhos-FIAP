"""Tabela hash, histórico em lista e fila de prioridade para os alertas."""
from dataclasses import asdict, dataclass
import heapq

from .sensores import Leitura, Resultado, Sensor, avaliar_leitura


@dataclass(frozen=True)
class Alerta:
    id_leitura: str
    codigo_sensor: str
    modulo: str
    ciclo: int
    prioridade: int
    motivos: tuple[str, ...]

    def para_dict(self):
        return asdict(self)


class FilaPrioridade:
    def __init__(self):
        self._heap = []
        self._sequencia = 0

    def __len__(self):
        return len(self._heap)

    def inserir(self, alerta: Alerta):
        if type(alerta.prioridade) is not int or alerta.prioridade not in (1, 2, 3, 4):
            raise ValueError('A prioridade do alerta deve ser um inteiro entre 1 e 4.')
        # O contador impede comparar objetos e mantém ordem de chegada em empates.
        heapq.heappush(self._heap, (alerta.prioridade, self._sequencia, alerta))
        self._sequencia += 1

    def proximo(self):
        return self._heap[0][2] if self._heap else None

    def retirar(self):
        return heapq.heappop(self._heap)[2] if self._heap else None

    def listar(self):
        copia = self._heap.copy()
        return [heapq.heappop(copia)[2] for _ in range(len(copia))]

    def vetor(self):
        return [{'indice': indice, 'pai': (indice - 1) // 2 if indice else None,
                 'prioridade': prioridade, 'ordem_chegada': ordem, 'id_leitura': alerta.id_leitura}
                for indice, (prioridade, ordem, alerta) in enumerate(self._heap)]


class MonitorSensores:
    def __init__(self, sensores: list[Sensor]):
        if not sensores:
            raise ValueError('Cadastre pelo menos um sensor no cenário.')
        self._sensores = {}
        for sensor in sensores:
            if sensor.codigo in self._sensores:
                raise ValueError(f'Sensor duplicado no catálogo: {sensor.codigo}.')
            self._sensores[sensor.codigo] = sensor
        self._por_id = {}
        self._ultimas = {}
        self._historico = []
        self._encaminhados = []
        self.fila = FilaPrioridade()

    def buscar_sensor(self, codigo) -> Sensor:
        try:
            return self._sensores[codigo]
        except KeyError as erro:
            raise ValueError(f'Sensor não cadastrado: {codigo}.') from erro

    def sensores(self):
        return list(self._sensores.values())

    def historico(self) -> list[Resultado]:
        return self._historico.copy()

    def ultimas_leituras(self):
        return list(self._ultimas.values())

    def encaminhados(self):
        return self._encaminhados.copy()

    def registrar(self, leitura: Leitura) -> Resultado:
        anterior = self._por_id.get(leitura.id)
        if anterior is not None:
            if anterior.leitura != leitura:
                raise ValueError(f'ID {leitura.id} repetido com conteúdo diferente.')
            return anterior  # Reenvio idêntico não duplica histórico nem alerta.
        sensor = self.buscar_sensor(leitura.codigo_sensor)
        ultima = self._ultimas.get(leitura.codigo_sensor)
        if ultima and leitura.ciclo <= ultima.leitura.ciclo:
            raise ValueError('A nova leitura deve ter ciclo maior que a última do mesmo sensor.')
        resultado = avaliar_leitura(sensor, leitura)
        self._por_id[leitura.id] = resultado
        self._ultimas[sensor.codigo] = resultado
        self._historico.append(resultado)
        if resultado.prioridade is not None:
            self.fila.inserir(Alerta(leitura.id, sensor.codigo, sensor.modulo, leitura.ciclo,
                                    resultado.prioridade, resultado.motivos))
        return resultado

    def encaminhar_proximo(self):
        alerta = self.fila.retirar()
        if alerta is not None:
            self._encaminhados.append(alerta)
        return alerta
