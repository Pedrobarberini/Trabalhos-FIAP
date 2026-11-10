"""Gera a representação do circuito principal com Matplotlib, sem editar imagens."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, PathPatch, Polygon
from matplotlib.path import Path as Caminho

VERDE = '#173F36'
LINHA = '#315E51'
FUNDO = '#F5F7F1'


def gerar_circuito(destino=None):
    destino = Path(destino) if destino else Path(__file__).resolve().parents[1] / 'circuito_logico.png'
    fig = plt.figure(figsize=(16, 9), facecolor=FUNDO)
    fig.text(0.055, 0.93, 'SIFSM | Aurora Siger', fontsize=16, color=VERDE, weight='bold')
    fig.text(0.055, 0.875, 'Circuito lógico de identificação de risco', fontsize=25, color=VERDE, weight='bold')
    fig.text(0.055, 0.815, r'$R = (E \wedge C)\;\vee\; O\;\vee\; \neg V$', fontsize=24, color=VERDE)
    ax = fig.add_axes([0.04, 0.29, 0.92, 0.48])
    ax.set(xlim=(0, 15.6), ylim=(0.3, 6.2), aspect='equal')
    ax.axis('off')

    def fio(pontos):
        ax.plot([p[0] for p in pontos], [p[1] for p in pontos], color=LINHA, lw=2, solid_capstyle='round')

    def entrada(simbolo, descricao, y, fim):
        ax.text(0.25, y + 0.18, simbolo, fontsize=17, color=VERDE, weight='bold')
        ax.text(0.85, y + 0.18, descricao, fontsize=10.5, color=VERDE)
        fio([(0.4, y), (fim, y)])

    def porta_and(x, y):
        vertices = [(x, y - .7), (x, y + .7), (x + .7, y + .7),
                    (x + 1.7, y + .7), (x + 1.7, y - .7), (x + .7, y - .7), (x, y - .7)]
        codigos = [Caminho.MOVETO, Caminho.LINETO, Caminho.LINETO,
                   Caminho.CURVE4, Caminho.CURVE4, Caminho.CURVE4, Caminho.CLOSEPOLY]
        ax.add_patch(PathPatch(Caminho(vertices, codigos), fc='white', ec=VERDE, lw=2))
        ax.text(x + .7, y, 'AND', ha='center', va='center', fontsize=13, color=VERDE, weight='bold')

    def porta_or(x, y):
        vertices = [(x, y - .7), (x + .8, y - .7), (x + 1.35, y - .4), (x + 1.7, y),
                    (x + 1.35, y + .4), (x + .8, y + .7), (x, y + .7),
                    (x + .45, y + .2), (x + .45, y - .2), (x, y - .7)]
        codigos = [Caminho.MOVETO] + [Caminho.CURVE4] * 9
        ax.add_patch(PathPatch(Caminho(vertices, codigos), fc='white', ec=VERDE, lw=2))
        ax.text(x + .85, y, 'OR', ha='center', va='center', fontsize=13, color=VERDE, weight='bold')

    entrada('E', 'consumo alto', 5.15, 3.4)
    entrada('C', 'módulo crítico', 4.45, 3.4)
    porta_and(3.4, 4.8)
    fio([(4.85, 4.8), (8.1, 4.8), (8.1, 3.9), (9.33, 3.9)])
    ax.text(5.4, 5.02, 'E AND C', fontsize=11, color=VERDE)

    entrada('O', 'oxigênio crítico', 2.85, 4.8)
    fio([(4.8, 2.85), (4.8, 2.65), (5.63, 2.65)])
    entrada('V', 'medições válidas', 1.5, 3.1)
    ax.add_patch(Polygon([(3.1, 1.0), (3.1, 2.0), (4.05, 1.5)], closed=True, fc='white', ec=VERDE, lw=2))
    ax.add_patch(Circle((4.16, 1.5), .11, fc='white', ec=VERDE, lw=2))
    ax.text(3.35, 1.5, 'NOT', ha='center', va='center', fontsize=9.5, color=VERDE, weight='bold')
    fio([(4.27, 1.5), (4.8, 1.5), (4.8, 1.95), (5.63, 1.95)])
    ax.text(4.0, 1.05, 'F = NOT V', fontsize=11, color=VERDE)
    porta_or(5.3, 2.3)
    fio([(7.0, 2.3), (8.1, 2.3), (8.1, 3.2), (9.33, 3.2)])

    porta_or(9.0, 3.55)
    fio([(10.7, 3.55), (11.8, 3.55)])
    ax.text(11.0, 3.78, 'R', fontsize=18, color=VERDE, weight='bold')
    ax.add_patch(Circle((11.8, 3.55), .06, fc=VERDE, ec=VERDE))
    fio([(11.8, 3.55), (11.8, 4.5), (12.4, 4.5)])
    fio([(11.8, 3.55), (11.8, 2.6), (12.4, 2.6)])
    for y, titulo, detalhe in [(4.5, 'LED de alarme', 'aceso quando R = 1'), (2.6, 'Buzzer virtual', 'ligado quando R = 1')]:
        ax.add_patch(FancyBboxPatch((12.4, y - .45), 2.8, .9, boxstyle='round,pad=0.08', fc='#E4EBCD', ec=VERDE, lw=1.5))
        ax.text(13.8, y + .10, titulo, ha='center', va='center', fontsize=12, color=VERDE, weight='bold')
        ax.text(13.8, y - .18, detalhe, ha='center', va='center', fontsize=10, color=VERDE)

    fig.text(0.055, 0.245, 'Conversão das medições em sinais digitais', fontsize=13, color=VERDE, weight='bold')
    fig.text(0.055, 0.205, 'E = 1 quando consumo > limite do módulo; O = 1 quando oxigênio < mínimo configurado.', fontsize=12, color=VERDE)
    fig.text(0.055, 0.17, 'V combina o estado informado pelo sensor e a validade dos canais; F = 1 quando V = 0.', fontsize=12, color=VERDE)
    fig.text(0.055, 0.135, 'C é definido no catálogo. AND exige E e C; OR reúne as causas; NOT inverte a validade.', fontsize=12, color=VERDE)
    fig.text(0.055, 0.087, 'Aviso auxiliar: consumo alto em módulo não crítico, sem falha ou oxigênio baixo, acende atenção.', fontsize=11, color=VERDE)
    fig.text(0.055, 0.05, 'Representação de software. Limiares didáticos; os atuadores são simulados e não desligam cargas essenciais.', fontsize=10.5, color='#5A6C60')
    fig.savefig(destino, dpi=170, facecolor=FUNDO)
    plt.close(fig)
    return destino


if __name__ == '__main__':
    print('Circuito gerado:', gerar_circuito())
