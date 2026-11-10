"""Circuito lógico e estruturas reutilizáveis da Parte 2 do SIFSM."""
from .estruturas import Alerta, FilaPrioridade, MonitorSensores
from .logica_risco import avaliar_portas, tabela_verdade
from .sensores import Leitura, Resultado, Sensor, avaliar_leitura

__all__ = [
    'Alerta', 'FilaPrioridade', 'MonitorSensores', 'Leitura', 'Resultado',
    'Sensor', 'avaliar_leitura', 'avaliar_portas', 'tabela_verdade',
]
