"""Entrada do SCIC: menu interativo e demonstração completa reproduzível."""
import argparse
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys

try:
    from analise_numerica import calcular_erros, indicadores, precisao_numerica, verificar_potencia
    from alertas_heap import construir_fila
    from busca_trie import construir_indice
    from carregar_dados import carregar_base, consultar_registros, resumo_por_tipo
    from configuracao import ARQUIVO_DADOS, PASTA_PROJETO
    from dispositivos import exemplo_eletrico
    from modelo_previsao import avaliar_modelo, prever_proximo_ciclo
    from relatorio import gerar_relatorio
except ModuleNotFoundError as erro:
    print(f'Dependência ausente: {erro.name}. Execute: python -m pip install -r requirements.txt')
    raise SystemExit(2) from erro


def mostrar_tabela(df, colunas=None, limite=12):
    if df.empty:
        print('Nenhum registro corresponde à consulta.')
        return
    tabela = df[colunas] if colunas else df
    print(tabela.head(limite).to_string(index=False, float_format=lambda valor: f'{valor:.3f}'))
    if len(df) > limite:
        print(f'Exibidos {limite} de {len(df)} registros.')


class SCIC:
    def __init__(self, caminho):
        self.carregar(caminho)

    def carregar(self, caminho):
        # Primeiro valida tudo. Uma carga inválida não destrói a sessão anterior.
        carga = carregar_base(caminho)
        dados = calcular_erros(carga.dados)
        fila = construir_fila(dados, carga.rejeitados)
        indice = construir_indice(dados)
        self.carga, self.dados, self.fila, self.indice = carga, dados, fila, indice
        self.avaliacao = None
        self.caminho = Path(caminho)

    def obter_avaliacao(self):
        if self.avaliacao is None:
            self.avaliacao = avaliar_modelo(self.dados)
        return self.avaliacao

    def resumo(self):
        print('\nBASE SIMULADA DA AURORA SIGER')
        print('Arquivo:', self.caminho.name)
        for chave, valor in self.carga.resumo().items():
            print(f'  {chave.replace("_", " ")}: {valor}')
        print('\nIndicadores por tipo de módulo:')
        print(resumo_por_tipo(self.dados).round(3).to_string())
        if not self.carga.rejeitados.empty:
            print('\nLeituras rejeitadas mantidas como falhas de telemetria:')
            mostrar_tabela(self.carga.rejeitados, ['id_registro', 'nome_modulo', 'ciclo', 'motivo_rejeicao'])

    def consultar(self, modulo='', status='', prioridade=None):
        resultado = consultar_registros(self.dados, modulo, status, prioridade)
        mostrar_tabela(resultado, ['id_registro', 'ciclo', 'nome_modulo', 'codigo_sensor',
                                   'latencia_prevista_ms', 'latencia_observada_ms', 'status', 'prioridade'])

    def erros(self):
        print('\nINDICADORES E ERROS NUMÉRICOS')
        print('Erro absoluto = |previsto - observado|; relativo = absoluto / |observado|.')
        print('Até 5%: aceitável; até 15%: atenção; acima de 15%: crítico. Abaixo de 1 ms: indefinido.')
        for chave, valor in indicadores(self.dados).items():
            exibido = 'indefinido' if valor is None else str(valor) if isinstance(valor, int) else f'{valor:.4f}'
            print(f'  {chave}: {exibido}')
        mostrar_tabela(self.dados.sort_values('erro_absoluto_ms', ascending=False),
                      ['id_registro', 'nome_modulo', 'erro_absoluto_ms', 'erro_percentual', 'classificacao_erro'], 5)
        precisao = precisao_numerica(self.dados)
        print(f"\nPonto flutuante: 0.1 + 0.2 = {precisao['soma_decimal']!r}")
        print(f"Igualdade exata: {precisao['igualdade_exata']}; math.isclose: {precisao['igualdade_com_tolerancia']}")
        print(f"math.fsum das latências: {precisao['soma_compensada']!r}")
        print('A mediana e os maiores erros complementam a média; erro crítico não prova causa física.')

    def modelo(self):
        avaliacao = self.obter_avaliacao()
        print('\nREGRESSÃO LINEAR: referência nominal + ciclo -> latência observada')
        for nome, parte in avaliacao.resumo['particoes'].items():
            print(f"{nome}: {', '.join(parte['ciclos'])} | {parte['registros']} registros")
        print('Escolha por RMSE da validação:', avaliacao.preferido)
        for particao in ('validacao', 'teste'):
            print(f'\n{particao.upper()}:')
            for metodo, valores in avaliacao.resumo[particao].items():
                r2 = 'indefinido' if valores['r2'] is None else f"{valores['r2']:.4f}"
                print(f"  {metodo}: MAE={valores['mae_ms']:.3f} ms; MSE={valores['mse_ms2']:.3f} ms²; "
                      f"RMSE={valores['rmse_ms']:.3f} ms; R²={r2}")
        print('O teste fica fora do ajuste e da seleção; RMSE destaca erros grandes. R² não garante perfeição.')
        print('\nEstimativa simulada do próximo ciclo, mantendo a referência mais recente:')
        mostrar_tabela(prever_proximo_ciclo(self.dados, avaliacao), limite=15)

    def alertas(self):
        print(f'\nFILA DE PRIORIDADE: {len(self.fila)} alertas em memória')
        print('Chave: nível, prioridade do módulo, -idade, -erro; desempate por ordem de entrada.')
        print('Nível 1: degradação crítica/falha de telemetria; nível 2: demais desvios relevantes.')
        for posicao, alerta in enumerate(self.fila.em_ordem()[:5], start=1):
            print(f'{posicao}. ID {alerta.id_registro} | {alerta.modulo} | {alerta.ciclo} | '
                  f'nível {alerta.nivel} | prioridade {alerta.prioridade_modulo} | idade {alerta.idade_ciclos}')
            print('   Motivo:', alerta.motivo)
        print('\nPrimeiros nós do vetor do heap (ordem interna não é ordenação completa):')
        for no in self.fila.estrutura()[:7]:
            print(f"  índice={no['indice']}; pai={no['pai']}; ID={no['id_registro']}; chave={no['chave']}")
        print('Inserção/retirada: O(log n); raiz: O(1). Lista não ordenada: O(n) para localizar o próximo.')

    def buscar(self, prefixo):
        encontrados = self.indice.buscar_prefixo(prefixo)
        print(f'\nTRIE - prefixo {prefixo!r}: {len(encontrados)} termo(s), limite 20')
        for item in encontrados:
            print(f"  [{item['tipo']}] {item['termo']} | IDs: {', '.join(map(str, item['ids'][:8]))}"
                  + (' ...' if len(item['ids']) > 8 else ''))
        if not encontrados:
            print('Nenhum termo localizado. Informe um prefixo não vazio.')
        return encontrados

    def dispositivos(self):
        exemplo = exemplo_eletrico(self.dados.sort_values('id_registro').iloc[0])
        sensor = exemplo['sensor']
        print('\nDISPOSITIVOS, BASES E ELETRICIDADE')
        print('Entrada: CSV de sensores simulados e teclado. Saída: terminal, relatório, CSVs e gráficos.')
        print('Rede/USB seriam interfaces de aquisição; rádio e relés seriam enlaces, apenas conceituais aqui.')
        print(f"Sensor {sensor['codigo']}: hexadecimal {sensor['hexadecimal']} = decimal {sensor['decimal']} "
              f"= binário {sensor['binario']}")
        print(f"{exemplo['modulo']}: P = {exemplo['tensao_v']:.2f} V x {exemplo['corrente_a']:.3f} A "
              f"= {exemplo['potencia_calculada_w']:.5f} W (CSV: {exemplo['potencia_gravada_w']:.2f} W)")
        resistencia = exemplo['resistencia_equivalente_ohm']
        print('R equivalente = V/I:', f'{resistencia:.4f} ohms' if resistencia is not None else 'indefinida (I=0)')
        print('Trata-se de consumo elétrico aproximado; potência de rádio e energia em Wh não foram medidas.')
        print('Coerência por tolerância propagada de arredondamento:', verificar_potencia(self.dados))

    def atender(self):
        alerta = self.fila.retirar()
        if alerta:
            print(f'Próximo para atendimento: ID {alerta.id_registro} | {alerta.modulo} | {alerta.motivo}')
            print(f'Restam {len(self.fila)} alertas. Retirada apenas em memória; resolução física não é presumida.')
        else:
            print('A fila está vazia.')

    def relatorio(self, pasta):
        # Exporta a análise integral da base, independentemente das retiradas do menu.
        fila_completa = construir_fila(self.dados, self.carga.rejeitados)
        caminho = gerar_relatorio(self.carga, self.dados, self.obter_avaliacao(), fila_completa, self.indice, pasta)
        print('\nANÁLISE FINAL:', caminho.name)
        print('Resultados calculados e gráficos exportados. Leituras rejeitadas precisam de conferência.')
        print('Os erros e a fila orientam inspeção; a previsão foi comparada à referência em ciclos reservados.')
        print('Priorizar mensagens essenciais, conservar recursos e validar decisões com supervisão humana.')
        return caminho

    def demonstrar(self, pasta):
        self.resumo()
        print('\nCONSULTA: Antena Central Aurora')
        self.consultar('Antena')
        self.erros()
        self.modelo()
        self.alertas()
        for prefixo in ('com', 'SNS-0x1A0', 'enf'):
            self.buscar(prefixo)
        self.dispositivos()
        print('\nDEMONSTRAÇÃO DE RETIRADA DO HEAP')
        self.atender()
        self.relatorio(pasta)


def menu(sistema, pasta_saida):
    while True:
        print('''
SCIC - AURORA SIGER (simulação)
1. Resumo da base e qualidade dos dados
2. Consultar registros
3. Indicadores e erros numéricos
4. Modelo, métricas e estimativa do próximo ciclo
5. Priorizar alertas e visualizar o heap
6. Buscar registros por prefixo (trie)
7. Dispositivos, bases numéricas e eletricidade
8. Retirar próximo alerta para atendimento em memória
9. Gerar relatório técnico, resultados e gráficos
10. Carregar outro CSV
0. Sair''')
        try:
            opcao = input('Escolha: ').strip()
            if opcao == '0':
                return
            if opcao == '1':
                sistema.resumo()
            elif opcao == '2':
                modulo = input('Nome ou parte do módulo (Enter = todos): ').strip()
                status = input('Status: ativo/alerta/manutencao (Enter = todos): ').strip().lower()
                prioridade = input('Prioridade máxima de 1 a 5 (Enter = todas): ').strip()
                sistema.consultar(modulo, status, int(prioridade) if prioridade else None)
            elif opcao == '3':
                sistema.erros()
            elif opcao == '4':
                sistema.modelo()
            elif opcao == '5':
                sistema.alertas()
            elif opcao == '6':
                encontrados = sistema.buscar(input('Prefixo de módulo, sensor, tipo ou mensagem: '))
                if encontrados:
                    identificador = input('ID da leitura para consultar (Enter = voltar): ').strip()
                    if identificador:
                        ids = {id_leitura for item in encontrados for id_leitura in item['ids']}
                        selecionado = int(identificador)
                        if selecionado not in ids:
                            raise ValueError('O ID não pertence aos resultados da busca.')
                        mostrar_tabela(sistema.dados[sistema.dados['id_registro'].eq(selecionado)])
            elif opcao == '7':
                sistema.dispositivos()
            elif opcao == '8':
                sistema.atender()
            elif opcao == '9':
                sistema.relatorio(pasta_saida)
            elif opcao == '10':
                caminho = input('Caminho do CSV (Enter = base original): ').strip().strip('"')
                sistema.carregar(caminho or ARQUIVO_DADOS)
                print('Base carregada; fila e índice reconstruídos.')
            else:
                print('Opção inválida. Escolha uma opção do menu.')
        except (ValueError, OSError) as erro:
            print('Não foi possível concluir:', erro)
        except (EOFError, KeyboardInterrupt):
            print('\nSessão encerrada.')
            return


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='SCIC Aurora Siger: análise e comunicação simuladas.')
    parser.add_argument('--dados', type=Path, default=ARQUIVO_DADOS, help='Base CSV a carregar.')
    parser.add_argument('--saida', type=Path, default=PASTA_PROJETO, help='Pasta do relatório, resultados e gráficos.')
    parser.add_argument('--demo', action='store_true', help='Executa todas as funcionalidades sem entrada interativa.')
    args = parser.parse_args()
    try:
        sistema = SCIC(args.dados)
        if args.demo:
            transcricao = StringIO()
            with redirect_stdout(transcricao):
                sistema.demonstrar(args.saida)
            saida = transcricao.getvalue()
            print(saida, end='')
            destino = args.saida / 'resultados'
            destino.mkdir(parents=True, exist_ok=True)
            (destino / 'exemplo_execucao.txt').write_text(saida, encoding='utf-8')
        else:
            menu(sistema, args.saida)
    except (ValueError, OSError) as erro:
        print('Erro na execução:', erro)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
