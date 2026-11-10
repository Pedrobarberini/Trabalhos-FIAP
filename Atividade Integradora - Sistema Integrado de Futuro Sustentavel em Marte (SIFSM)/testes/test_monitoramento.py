"""Testes da regra, dos sensores, das estruturas e da execução integrada."""
from dataclasses import replace
import json
from pathlib import Path
import random
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parte2.demo import DADOS, carregar_cenario, exportar_evidencias
from parte2.estruturas import Alerta, FilaPrioridade, MonitorSensores
from parte2.logica_risco import avaliar_portas, tabela_verdade
from parte2.sensores import Leitura, Sensor, avaliar_leitura

SENSOR = Sensor('SNS-TESTE', 'Habitação de teste', True, 10.0, 19.5)
LEITURA = Leitura('TESTE-1', SENSOR.codigo, 1, 8.0, 21.0, True)


class TesteCircuito(unittest.TestCase):
    def test_todas_as_16_combinacoes_por_casos_sem_alarme(self):
        linhas = tabela_verdade()
        self.assertEqual(len(linhas), 16)
        self.assertEqual(len({tuple(linha[chave] for chave in ('E', 'C', 'O', 'V')) for linha in linhas}), 16)
        sem_alarme = {(False, False, False, True), (False, True, False, True), (True, False, False, True)}
        for linha in linhas:
            entradas = tuple(linha[chave] for chave in ('E', 'C', 'O', 'V'))
            self.assertEqual(linha['R'], entradas not in sem_alarme)
            self.assertEqual(linha['F'], not linha['V'])
        self.assertEqual(sum(linha['R'] for linha in linhas), 13)

    def test_falha_tem_alarme_em_qualquer_combinacao(self):
        for linha in tabela_verdade():
            if not linha['V']:
                self.assertTrue(linha['R'])

    def test_rejeita_numeros_e_textos_no_lugar_de_bits_booleanos(self):
        for valor in (0, 1, 'false', None):
            with self.assertRaises(ValueError):
                avaliar_portas(valor, True, False, True)


class TesteSensores(unittest.TestCase):
    def test_medicao_normal_nao_aciona_atuadores(self):
        resultado = avaliar_leitura(SENSOR, LEITURA)
        self.assertEqual(resultado.classificacao, 'normal')
        self.assertIsNone(resultado.prioridade)
        self.assertFalse(resultado.led_alarme)
        self.assertFalse(resultado.buzzer)

    def test_limites_exatos_nao_sao_excesso_ou_oxigenio_critico(self):
        resultado = avaliar_leitura(SENSOR, replace(LEITURA, consumo_kwh=10.0, oxigenio_pct=19.5))
        sinais = dict(resultado.sinais)
        self.assertFalse(sinais['E'])
        self.assertFalse(sinais['O'])
        self.assertFalse(sinais['R'])

    def test_ultrapassagem_minima_dos_limites_e_detectada(self):
        energia = avaliar_leitura(SENSOR, replace(LEITURA, consumo_kwh=10.000001))
        oxigenio = avaliar_leitura(SENSOR, replace(LEITURA, oxigenio_pct=19.499999))
        self.assertEqual(energia.prioridade, 3)
        self.assertEqual(oxigenio.prioridade, 1)

    def test_excesso_em_nao_critico_gera_aviso_sem_alarme_critico(self):
        resultado = avaliar_leitura(replace(SENSOR, critico=False), replace(LEITURA, consumo_kwh=15.0))
        self.assertEqual(resultado.classificacao, 'atencao')
        self.assertEqual(resultado.prioridade, 4)
        self.assertTrue(resultado.indicador_atencao)
        self.assertFalse(resultado.led_alarme)
        self.assertFalse(resultado.buzzer)

    def test_oxigenio_baixo_prioriza_mesmo_modulo_nao_critico(self):
        resultado = avaliar_leitura(replace(SENSOR, critico=False), replace(LEITURA, oxigenio_pct=18.0))
        self.assertEqual(resultado.prioridade, 1)
        self.assertTrue(resultado.buzzer)

    def test_estado_invalido_nao_confia_nos_valores_do_sensor(self):
        resultado = avaliar_leitura(SENSOR, replace(LEITURA, sensor_valido=False, consumo_kwh=50, oxigenio_pct=10))
        sinais = dict(resultado.sinais)
        self.assertFalse(sinais['V'])
        self.assertFalse(sinais['E'])
        self.assertFalse(sinais['O'])
        self.assertTrue(sinais['F'])
        self.assertTrue(sinais['R'])
        self.assertEqual(resultado.prioridade, 2)

    def test_ausencias_e_valores_fisicos_invalidos_geram_falha(self):
        for leitura in (replace(LEITURA, consumo_kwh=None), replace(LEITURA, consumo_kwh=-1),
                        replace(LEITURA, oxigenio_pct=None), replace(LEITURA, oxigenio_pct=101),
                        replace(LEITURA, oxigenio_pct=-1)):
            resultado = avaliar_leitura(SENSOR, leitura)
            self.assertTrue(dict(resultado.sinais)['F'])
            self.assertTrue(resultado.led_alarme)
            self.assertEqual(resultado.prioridade, 2)

    def test_canal_oxigenio_conhecido_critico_prevalece_sobre_falta_de_consumo(self):
        resultado = avaliar_leitura(SENSOR, replace(LEITURA, consumo_kwh=None, oxigenio_pct=18))
        self.assertTrue(dict(resultado.sinais)['F'])
        self.assertTrue(dict(resultado.sinais)['O'])
        self.assertEqual(resultado.prioridade, 1)

    def test_entrada_nao_finita_booleana_ou_textual_e_recusada(self):
        for valor in (float('nan'), float('inf'), True, '8.0'):
            with self.assertRaises(ValueError):
                replace(LEITURA, consumo_kwh=valor)
        with self.assertRaises(ValueError):
            replace(LEITURA, ciclo=True)

    def test_configuracao_invalida_nao_entra_no_catalogo(self):
        for alteracao in ({'limite_consumo_kwh': 0}, {'minimo_oxigenio_pct': 101},
                          {'critico': 1}, {'codigo': ''}, {'modulo': ''}):
            with self.assertRaises(ValueError):
                replace(SENSOR, **alteracao)


class TesteEstruturas(unittest.TestCase):
    def test_heap_equivale_a_ordenacao_por_urgencia_e_chegada(self):
        rng = random.Random(42)
        alertas = [Alerta(f'A{indice}', 'SNS-TESTE', 'Habitação', 1, rng.randint(1, 4), ('Ocorrência',))
                   for indice in range(150)]
        fila = FilaPrioridade()
        for alerta in alertas:
            fila.inserir(alerta)
        esperados = sorted(enumerate(alertas), key=lambda par: (par[1].prioridade, par[0]))
        self.assertEqual(fila.listar(), [alerta for _, alerta in esperados])
        self.assertEqual(len(fila), 150)
        for _, alerta in esperados:
            self.assertEqual(fila.proximo(), alerta)
            self.assertEqual(fila.retirar(), alerta)
        self.assertIsNone(fila.proximo())
        self.assertIsNone(fila.retirar())

    def test_vetor_heap_respeita_pai_menor_que_filhos(self):
        monitor = carregar_cenario()
        vetor = monitor.fila.vetor()
        for no in vetor[1:]:
            pai = vetor[no['pai']]
            self.assertLessEqual((pai['prioridade'], pai['ordem_chegada']),
                                 (no['prioridade'], no['ordem_chegada']))

    def test_reenvio_identico_nao_duplica_historico_ou_fila(self):
        monitor = MonitorSensores([SENSOR])
        leitura = replace(LEITURA, oxigenio_pct=18)
        resultado = monitor.registrar(leitura)
        self.assertIs(monitor.registrar(leitura), resultado)
        self.assertEqual(len(monitor.historico()), 1)
        self.assertEqual(len(monitor.fila), 1)

    def test_id_conflitante_nao_modifica_o_estado(self):
        monitor = MonitorSensores([SENSOR])
        monitor.registrar(LEITURA)
        with self.assertRaises(ValueError):
            monitor.registrar(replace(LEITURA, consumo_kwh=99))
        self.assertEqual(len(monitor.historico()), 1)
        self.assertEqual(monitor.ultimas_leituras()[0].leitura.consumo_kwh, 8)

    def test_ciclo_antigo_nao_sobrescreve_falha_recente(self):
        monitor = MonitorSensores([SENSOR])
        monitor.registrar(replace(LEITURA, id='ATUAL', ciclo=2, sensor_valido=False))
        with self.assertRaises(ValueError):
            monitor.registrar(replace(LEITURA, id='ATRASADA', ciclo=1))
        self.assertTrue(monitor.ultimas_leituras()[0].led_alarme)
        self.assertEqual(len(monitor.historico()), 1)

    def test_sensor_desconhecido_e_duplicado_sao_tratados(self):
        monitor = MonitorSensores([SENSOR])
        with self.assertRaises(ValueError):
            monitor.buscar_sensor('DESCONHECIDO')
        with self.assertRaises(ValueError):
            monitor.registrar(replace(LEITURA, codigo_sensor='OUTRO'))
        self.assertEqual(monitor.historico(), [])
        with self.assertRaises(ValueError):
            MonitorSensores([SENSOR, SENSOR])

    def test_cenario_mantem_eventos_passados_apos_normalizacao(self):
        monitor = carregar_cenario()
        self.assertEqual(len(monitor.historico()), 13)
        self.assertEqual(len(monitor.fila), 9)
        atual = next(item for item in monitor.ultimas_leituras() if item.leitura.codigo_sensor == 'SNS-HAB-N')
        self.assertFalse(atual.led_alarme)
        self.assertIn('L009', [alerta.id_leitura for alerta in monitor.fila.listar()])
        self.assertEqual([alerta.id_leitura for alerta in monitor.fila.listar()[:3]], ['L004', 'L007', 'L009'])

    def test_encaminhamento_registra_historico_sem_alterar_leituras(self):
        monitor = carregar_cenario()
        alerta = monitor.encaminhar_proximo()
        self.assertEqual(alerta.id_leitura, 'L004')
        self.assertEqual(len(monitor.fila), 8)
        self.assertEqual(monitor.encaminhados(), [alerta])
        self.assertEqual(len(monitor.historico()), 13)

    def test_consultas_nao_expoem_listas_mutaveis_internas(self):
        monitor = carregar_cenario()
        historico = monitor.historico()
        historico.clear()
        self.assertEqual(len(monitor.historico()), 13)
        dados = monitor.historico()[0].para_dict()
        dados['sinais']['R'] = True
        self.assertFalse(dict(monitor.historico()[0].sinais)['R'])


class TesteExecucao(unittest.TestCase):
    def test_demo_sem_bibliotecas_externas_funciona_fora_da_pasta(self):
        principal = Path(__file__).resolve().parents[1] / 'parte2_regras.py'
        with TemporaryDirectory() as pasta:
            processo = subprocess.run([sys.executable, '-S', str(principal), '--cenario-json', '--demo', '--saida', pasta],
                                      cwd=pasta, text=True, encoding='utf-8', capture_output=True, timeout=20)
            self.assertEqual(processo.returncode, 0, processo.stderr)
            dados = json.loads((Path(pasta) / 'execucao.json').read_text(encoding='utf-8'))
            self.assertEqual(dados['classificacoes'], {'normal': 4, 'atencao': 2, 'critico': 7})
            self.assertEqual(len(dados['tabela_verdade']), 16)
            self.assertEqual(dados['demonstracao_retirada']['retirado_na_copia']['id_leitura'], 'L004')
            self.assertEqual(dados['demonstracao_retirada']['pendentes_na_fila_original'], 9)
            self.assertIn('RETIRADA DO ALERTA MAIS URGENTE', processo.stdout)
            self.assertTrue((Path(pasta) / 'execucao_terminal.txt').is_file())

    def test_menu_trata_erros_e_exporta_alteracao_da_sessao(self):
        principal = Path(__file__).resolve().parents[1] / 'parte2_regras.py'
        entradas = '\n'.join(['99', '1', '2', 'DESCONHECIDO', '3', '4', '5', '6', '7',
                               '8', 'L014', 'SNS-MED', '4', '8', '19.4', '1', '9', '0', ''])
        with TemporaryDirectory() as pasta:
            processo = subprocess.run([sys.executable, '-S', str(principal), '--cenario-json', '--saida', pasta],
                                      cwd=pasta, input=entradas, text=True, encoding='utf-8',
                                      capture_output=True, timeout=20)
            self.assertEqual(processo.returncode, 0, processo.stderr)
            self.assertIn('Opção inválida', processo.stdout)
            self.assertIn('Sensor não cadastrado', processo.stdout)
            dados = json.loads((Path(pasta) / 'execucao.json').read_text(encoding='utf-8'))
            self.assertEqual(dados['quantidade_leituras'], 14)
            self.assertEqual(dados['encaminhados_na_sessao'][0]['id_leitura'], 'L004')
            self.assertEqual(dados['alertas_priorizados'][0]['id_leitura'], 'L007')

    def test_json_inexistente_ou_invalido_da_mensagem_clara(self):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / 'invalido.json'
            for texto in ('[]', '{"sensores": []}', '{"sensores": NaN, "leituras": []}', '{quebrado'):
                caminho.write_text(texto, encoding='utf-8')
                with self.assertRaises(ValueError):
                    carregar_cenario(caminho)
            with self.assertRaises(OSError):
                carregar_cenario(Path(pasta) / 'inexistente.json')

    def test_exportacao_nao_consume_a_fila(self):
        monitor = carregar_cenario()
        with TemporaryDirectory() as pasta:
            exportar_evidencias(monitor, pasta)
            self.assertEqual(len(monitor.fila), 9)
            linhas = (Path(pasta) / 'tabela_verdade.csv').read_text(encoding='utf-8').splitlines()
            self.assertEqual(len(linhas), 17)


if __name__ == '__main__':
    unittest.main()
