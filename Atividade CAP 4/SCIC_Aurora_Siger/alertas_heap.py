"""Min-heap explícito: inserção com heapify-up e retirada com heapify-down."""
from dataclasses import asdict, dataclass
import math

import pandas as pd


@dataclass(frozen=True)
class Alerta:
    id_registro: int | str
    modulo: str
    ciclo: str
    nivel: int
    prioridade_modulo: int
    idade_ciclos: int
    erro_relativo: float
    motivo: str

    def __post_init__(self):
        if self.nivel not in (1, 2) or self.prioridade_modulo not in range(1, 6):
            raise ValueError('Nível de alerta ou prioridade inválida.')
        if self.idade_ciclos < 0 or not math.isfinite(self.erro_relativo) or self.erro_relativo < 0:
            raise ValueError('Idade e erro devem ser finitos e não negativos.')

    @property
    def chave(self):
        # Menor chave sai primeiro. Depois da severidade, protege módulos essenciais.
        return (self.nivel, self.prioridade_modulo, -self.idade_ciclos, -self.erro_relativo)


class FilaAlertas:
    def __init__(self, alertas=()):
        self._itens = []
        self._sequencia = 0
        for alerta in alertas:
            self.inserir(alerta)

    def __len__(self):
        return len(self._itens)

    def inserir(self, alerta):
        # O contador mantém FIFO em empates e dispensa comparar objetos Alerta.
        self._itens.append((alerta.chave, self._sequencia, alerta))
        self._sequencia += 1
        self._subir(len(self._itens) - 1)

    def _subir(self, indice):
        while indice > 0:
            pai = (indice - 1) // 2
            if self._itens[pai][:2] <= self._itens[indice][:2]:
                break
            self._itens[pai], self._itens[indice] = self._itens[indice], self._itens[pai]
            indice = pai

    def _descer(self, indice):
        while 2 * indice + 1 < len(self._itens):
            menor = 2 * indice + 1
            direita = menor + 1
            if direita < len(self._itens) and self._itens[direita][:2] < self._itens[menor][:2]:
                menor = direita
            if self._itens[indice][:2] <= self._itens[menor][:2]:
                break
            self._itens[indice], self._itens[menor] = self._itens[menor], self._itens[indice]
            indice = menor

    def primeiro(self):
        return self._itens[0][2] if self._itens else None

    def retirar(self):
        if not self._itens:
            return None
        primeiro = self._itens[0][2]
        ultimo = self._itens.pop()
        if self._itens:
            self._itens[0] = ultimo
            self._descer(0)
        return primeiro

    def em_ordem(self):
        # A listagem não consome a fila usada pelo operador.
        copia = FilaAlertas()
        copia._itens = self._itens.copy()
        copia._sequencia = self._sequencia
        resultado = []
        while len(copia):
            resultado.append(copia.retirar())
        return resultado

    def estrutura(self):
        return [{'indice': indice, 'pai': (indice - 1) // 2 if indice else None,
                 'id_registro': item[2].id_registro, 'chave': list(item[0])}
                for indice, item in enumerate(self._itens)]


def construir_fila(df, rejeitados):
    alertas = []
    ultimo_ciclo = int(df['numero_ciclo'].max())
    for linha in df.to_dict('records'):
        if linha['status'] == 'manutencao':
            continue
        if linha['degradacao']:
            nivel, motivo = 1, 'Latência maior que a referência com erro relativo acima de 15%.'
        elif linha['status'] == 'alerta' or linha['classificacao_erro'] in ('atencao', 'critico', 'indefinido'):
            nivel, motivo = 2, 'Revisar desvio da previsão ou alerta informado: ' + linha['mensagem_alerta']
        else:
            continue
        relativo = linha['erro_relativo'] if pd.notna(linha['erro_relativo']) else 0.0
        alertas.append(Alerta(int(linha['id_registro']), linha['nome_modulo'], linha['ciclo'],
                             nivel, int(linha['prioridade']), ultimo_ciclo - int(linha['numero_ciclo']),
                             float(relativo), motivo))
    # A leitura ausente sai das métricas, mas permanece como falha de telemetria na fila.
    for indice, linha in enumerate(rejeitados.to_dict('records')):
        identificador = linha['id_registro']
        identificador = int(identificador) if pd.notna(identificador) and math.isfinite(identificador) else f'INVALIDO-{indice + 1}'
        prioridade = linha['prioridade']
        prioridade = int(prioridade) if pd.notna(prioridade) and prioridade in range(1, 6) else 1
        ciclo = str(linha['ciclo'])
        numero = int(ciclo[1:]) if len(ciclo) == 4 and ciclo[1:].isdigit() else ultimo_ciclo
        alertas.append(Alerta(identificador, linha['nome_modulo'], ciclo, 1, prioridade,
                             max(0, ultimo_ciclo - numero), 0.0,
                             'Falha de qualidade da telemetria: ' + linha['motivo_rejeicao']))
    return FilaAlertas(alertas)


def exportar_alertas(fila):
    return [asdict(alerta) for alerta in fila.em_ordem()]
