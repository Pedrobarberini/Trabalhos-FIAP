"""Demonstração da responsabilidade 2 do SIFSM: circuito, sensores e alertas."""
import argparse
from collections import Counter
from contextlib import redirect_stdout
import csv
from dataclasses import asdict
from datetime import datetime, timezone
from io import StringIO
import json
from pathlib import Path
import sys

from .estruturas import FilaPrioridade, MonitorSensores
from .logica_risco import tabela_verdade
from .sensores import Leitura, Sensor

PASTA = Path(__file__).resolve().parent
DADOS = PASTA / 'dados_aurora_siger.json'


def constante_invalida(valor):
    raise ValueError(f'Constante JSON não permitida: {valor}. Use null para leitura ausente.')


def carregar_cenario(caminho=DADOS):
    dados = json.loads(Path(caminho).read_text(encoding='utf-8-sig'), parse_constant=constante_invalida)
    if not isinstance(dados, dict):
        raise ValueError('A raiz do cenário deve ser um objeto JSON.')
    if not isinstance(dados.get('sensores'), list) or not isinstance(dados.get('leituras'), list):
        raise ValueError('O cenário deve conter as listas sensores e leituras.')
    monitor = MonitorSensores([Sensor.de_dict(item) for item in dados['sensores']])
    # A carga só é devolvida após todas as leituras passarem pela validação.
    for posicao, item in enumerate(dados['leituras'], start=1):
        try:
            monitor.registrar(Leitura.de_dict(item))
        except ValueError as erro:
            raise ValueError(f'Leitura #{posicao}: {erro}') from erro
    return monitor


def mostrar_historico(monitor):
    print('\nLEITURAS E SAÍDAS DO CIRCUITO')
    print('ID    SENSOR       CICLO E C O V F | R | CLASSIFICAÇÃO / PRIORIDADE')
    for resultado in monitor.historico():
        sinais = dict(resultado.sinais)
        bits = ' '.join(str(int(sinais[chave])) for chave in ('E', 'C', 'O', 'V', 'F'))
        print(f'{resultado.leitura.id:<5} {resultado.leitura.codigo_sensor:<12} '
              f'{resultado.leitura.ciclo:>5} {bits} | {int(sinais["R"])} | '
              f'{resultado.classificacao:<13} / {resultado.prioridade or "-"}')
    contagens = Counter(item.classificacao for item in monitor.historico())
    print('Resumo:', ', '.join(f'{nome}={contagens[nome]}' for nome in ('normal', 'atencao', 'critico')))


def mostrar_atuadores(monitor):
    print('\nATUADORES VIRTUAIS - ÚLTIMA LEITURA DE CADA SENSOR')
    for resultado in monitor.ultimas_leituras():
        print(f'{resultado.leitura.codigo_sensor} | ciclo {resultado.leitura.ciclo} | '
              f'LED alarme={int(resultado.led_alarme)} | buzzer={int(resultado.buzzer)} | '
              f'indicador atenção={int(resultado.indicador_atencao)}')
    print('A saída combinacional muda com a leitura; o histórico e os alertas anteriores permanecem.')
    print('Não há acionamento de hardware nem desligamento de sistemas essenciais.')


def mostrar_fila(monitor):
    print(f'\nFILA DE PRIORIDADE: {len(monitor.fila)} alerta(s) pendente(s)')
    for ordem, alerta in enumerate(monitor.fila.listar(), start=1):
        print(f'{ordem}. prioridade {alerta.prioridade} | {alerta.id_leitura} | '
              f'{alerta.modulo} | ciclo {alerta.ciclo}')
        print('   ' + ' '.join(alerta.motivos))
    print('Menor número = maior urgência. Empates respeitam a ordem de chegada.')


def mostrar_tabela_verdade():
    print('\nTABELA-VERDADE - R = (E AND C) OR O OR (NOT V)')
    print('E C O V | F EC | R')
    for linha in tabela_verdade():
        print(' '.join(str(int(linha[campo])) for campo in ('E', 'C', 'O', 'V')) + ' | '
              + ' '.join(str(int(linha[campo])) for campo in ('F', 'EC')) + ' | ' + str(int(linha['R'])))


def demonstrar_retirada(monitor):
    # Faz a retirada numa cópia da fila, preservando o cenário para nova exploração.
    copia = FilaPrioridade()
    for alerta in monitor.fila.listar():
        copia.inserir(alerta)
    proximo = copia.retirar()
    return {'retirado_na_copia': proximo.para_dict() if proximo else None,
            'pendentes_na_copia': len(copia), 'pendentes_na_fila_original': len(monitor.fila)}


def exportar_evidencias(monitor, pasta):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    retirada = demonstrar_retirada(monitor)
    contagens = Counter(item.classificacao for item in monitor.historico())
    resumo = {
        'executado_em_utc': datetime.now(timezone.utc).isoformat(),
        'escopo': 'Responsabilidade 2 do SIFSM - circuito lógico, sensores e estruturas de dados',
        'regra': 'R = (E and C) or O or (not V)',
        'sensores': [asdict(sensor) for sensor in monitor.sensores()],
        'quantidade_leituras': len(monitor.historico()),
        'classificacoes': {nome: contagens[nome] for nome in ('normal', 'atencao', 'critico')},
        'tabela_verdade': tabela_verdade(),
        'resultados': [item.para_dict() for item in monitor.historico()],
        'atuadores_ultimas_leituras': [item.para_dict() for item in monitor.ultimas_leituras()],
        'alertas_priorizados': [alerta.para_dict() for alerta in monitor.fila.listar()],
        'vetor_heap': monitor.fila.vetor(),
        'encaminhados_na_sessao': [alerta.para_dict() for alerta in monitor.encaminhados()],
        'demonstracao_retirada': retirada,
    }
    (pasta / 'execucao.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=2,
                                                   allow_nan=False) + '\n', encoding='utf-8')
    with (pasta / 'tabela_verdade.csv').open('w', encoding='utf-8', newline='') as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=['E', 'C', 'O', 'V', 'F', 'EC', 'R'])
        writer.writeheader()
        writer.writerows({chave: int(valor) for chave, valor in linha.items()} for linha in tabela_verdade())
    with (pasta / 'alertas_priorizados.csv').open('w', encoding='utf-8', newline='') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(['ordem', 'prioridade', 'id_leitura', 'sensor', 'modulo', 'ciclo', 'motivos'])
        for ordem, alerta in enumerate(monitor.fila.listar(), start=1):
            writer.writerow([ordem, alerta.prioridade, alerta.id_leitura, alerta.codigo_sensor,
                             alerta.modulo, alerta.ciclo, ' '.join(alerta.motivos)])
    print('\nEvidências geradas: execucao.json, tabela_verdade.csv e alertas_priorizados.csv.')
    return resumo


def demonstrar(monitor, pasta):
    print('SIFSM - AURORA SIGER | CIRCUITO LÓGICO, SENSORES E ESTRUTURAS DE DADOS')
    print('E: consumo alto; C: módulo crítico; O: oxigênio crítico; V: medições válidas.')
    print('Regra: R = (E AND C) OR O OR (NOT V). F = NOT V.')
    print('Limites de energia por ciclo e oxigênio são parâmetros didáticos da simulação.')
    mostrar_tabela_verdade()
    mostrar_historico(monitor)
    mostrar_atuadores(monitor)
    print('\nCONSULTA POR CÓDIGO - TABELA HASH')
    sensor = monitor.sensores()[0]
    print(asdict(monitor.buscar_sensor(sensor.codigo)))
    mostrar_fila(monitor)
    print('\nVETOR INTERNO DO HEAP - NÃO É UMA LISTA COMPLETAMENTE ORDENADA')
    for no in monitor.fila.vetor():
        print(no)
    retirada = demonstrar_retirada(monitor)
    print('\nRETIRADA DO ALERTA MAIS URGENTE EM UMA CÓPIA DA FILA')
    print(retirada)
    print('Encaminhar não significa resolver a ocorrência física; decisões operacionais exigem conferência humana.')
    exportar_evidencias(monitor, pasta)


def ler_numero(pergunta):
    entrada = input(pergunta).strip()
    if entrada.lower() in ('', 'null', 'nulo'):
        return None
    return float(entrada.replace(',', '.'))


def registrar_manual(monitor):
    identificador = input('ID único da leitura: ').strip()
    codigo = input('Código do sensor cadastrado: ').strip()
    ciclo = int(input('Ciclo inteiro, maior que o último do sensor: '))
    consumo = ler_numero('Consumo em kWh no ciclo (Enter = ausente): ')
    oxigenio = ler_numero('Oxigênio em % (Enter = ausente): ')
    valido = input('Sensor informou estado válido? 1=sim, 0=não: ').strip()
    if valido not in ('0', '1'):
        raise ValueError('Informe 1 ou 0 para o estado do sensor.')
    resultado = monitor.registrar(Leitura(identificador, codigo, ciclo, consumo, oxigenio, valido == '1'))
    print(json.dumps(resultado.para_dict(), ensure_ascii=False, indent=2))


def menu(monitor, pasta):
    while True:
        print('''
SIFSM - RESPONSABILIDADE 2
1. Listar sensores e limites
2. Buscar sensor por código
3. Consultar histórico e resultados booleanos
4. Consultar os atuadores virtuais atuais
5. Listar alertas por prioridade
6. Encaminhar o próximo alerta
7. Mostrar a tabela-verdade completa
8. Registrar uma leitura manual em memória
9. Exportar evidências da sessão
0. Sair''')
        try:
            opcao = input('Escolha: ').strip()
            if opcao == '0':
                return
            if opcao == '1':
                for sensor in monitor.sensores():
                    print(asdict(sensor))
            elif opcao == '2':
                print(asdict(monitor.buscar_sensor(input('Código: ').strip())))
            elif opcao == '3':
                mostrar_historico(monitor)
            elif opcao == '4':
                mostrar_atuadores(monitor)
            elif opcao == '5':
                mostrar_fila(monitor)
            elif opcao == '6':
                alerta = monitor.encaminhar_proximo()
                print(alerta.para_dict() if alerta else 'Fila vazia.')
                print('Encaminhamento apenas em memória, sem resolver automaticamente a ocorrência.')
            elif opcao == '7':
                mostrar_tabela_verdade()
            elif opcao == '8':
                registrar_manual(monitor)
            elif opcao == '9':
                exportar_evidencias(monitor, pasta)
            else:
                print('Opção inválida. Escolha uma das opções do menu.')
        except (ValueError, OSError) as erro:
            print('Não foi possível concluir:', erro)
        except (EOFError, KeyboardInterrupt):
            print('\nSessão encerrada.')
            return


def main(argumentos=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='Circuito, sensores e alertas da responsabilidade 2 do SIFSM.')
    parser.add_argument('--dados', type=Path, default=DADOS)
    parser.add_argument('--saida', type=Path, default=PASTA / 'evidencias')
    parser.add_argument('--demo', action='store_true', help='Executa e registra toda a demonstração, sem solicitar entrada.')
    args = parser.parse_args(argumentos)
    try:
        monitor = carregar_cenario(args.dados)
        if args.demo:
            transcricao = StringIO()
            with redirect_stdout(transcricao):
                demonstrar(monitor, args.saida)
            saida = transcricao.getvalue()
            print(saida, end='')
            (args.saida / 'execucao_terminal.txt').write_text(saida, encoding='utf-8')
        else:
            menu(monitor, args.saida)
    except (ValueError, OSError) as erro:
        print('Erro na execução:', erro)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
