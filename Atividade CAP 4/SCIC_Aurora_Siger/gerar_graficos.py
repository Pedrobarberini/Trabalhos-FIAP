"""Gráficos produzidos a partir da execução, sem janela gráfica obrigatória."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def gerar_graficos(df, avaliacao, pasta):
    pasta.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    cores = ['#245748', '#9AAB49']
    medias = df.groupby('tipo_modulo')['latencia_observada_ms'].mean().sort_values()
    fig, ax = plt.subplots(figsize=(9, 5), layout='constrained')
    ax.barh([tipo.replace('_', ' ') for tipo in medias.index], medias, color=cores[0])
    ax.set(title='Aurora Siger: latência média por tipo de módulo', xlabel='Latência observada (ms)')
    fig.savefig(pasta / 'latencia_por_tipo.png', dpi=160)
    plt.close(fig)

    medias = df.groupby('ciclo')[['latencia_prevista_ms', 'latencia_observada_ms']].mean()
    fig, ax = plt.subplots(figsize=(9, 5), layout='constrained')
    for coluna, nome, cor in zip(medias.columns, ['Referência simulada', 'Observada'], cores):
        ax.plot(medias.index, medias[coluna], marker='o', color=cor, label=nome)
    ax.set(title='Latência média da colônia por ciclo', xlabel='Ciclo', ylabel='Latência (ms)')
    ax.legend()
    fig.savefig(pasta / 'latencia_por_ciclo.png', dpi=160)
    plt.close(fig)

    teste = avaliacao.teste
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), layout='constrained')
    limite = teste[['latencia_observada_ms', 'latencia_prevista_ms', 'previsao_regressao_ms']].max().max() * 1.05
    for ax, coluna, titulo, cor in zip(
        axes, ['latencia_prevista_ms', 'previsao_regressao_ms'],
        ['Referência simulada', 'Regressão linear'], cores,
    ):
        ax.scatter(teste['latencia_observada_ms'], teste[coluna], color=cor, alpha=0.85)
        ax.plot([0, limite], [0, limite], '--', color='#888888', label='Previsão = observação')
        ax.set(title=titulo, xlabel='Observada (ms)', ylabel='Prevista (ms)', xlim=(0, limite), ylim=(0, limite))
        ax.legend(fontsize=8)
    fig.suptitle('Avaliação nos ciclos reservados de teste')
    fig.savefig(pasta / 'previsoes_no_teste.png', dpi=160)
    plt.close(fig)
