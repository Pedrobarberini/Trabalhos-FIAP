"""Verificações do SCIC com a base distribuída e casos de limite controlados."""
from pathlib import Path
import json
import random
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from alertas_heap import Alerta, FilaAlertas, construir_fila
from analise_numerica import calcular_erros, verificar_potencia
from busca_trie import Trie, construir_indice
from carregar_dados import carregar_base, consultar_registros
from codigo_fonte import SCIC
from configuracao import ARQUIVO_DADOS
from dispositivos import converter_sensor, exemplo_eletrico
from gerar_base import gerar_base
from modelo_previsao import avaliar_modelo, metricas, separar_temporal
from relatorio import gerar_relatorio


class TesteCarga(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.carga = carregar_base()

    def carregar_amostra(self, dados):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / 'base.csv'
            dados.to_csv(caminho, index=False)
            return carregar_base(caminho)

    def test_base_original_e_auditoria(self):
        resumo = self.carga.resumo()
        self.assertEqual(resumo['linhas_originais'], 154)
        self.assertEqual(resumo['duplicatas_removidas'], 4)
        self.assertEqual(resumo['registros_rejeitados'], 6)
        self.assertEqual(resumo['registros_validos'], 144)
        self.assertEqual(resumo['modulos'], 15)
        self.assertEqual(resumo['ciclos'], 10)
        self.assertTrue(self.carga.rejeitados['motivo_rejeicao'].str.contains('latencia_observada_ms').all())

    def test_status_e_codigos_sao_normalizados(self):
        amostra = self.carga.dados.head(3).copy()
        amostra['status'] = ' ATIVO '
        amostra['codigo_sensor'] = amostra['codigo_sensor'].str.lower()
        carga = self.carregar_amostra(amostra)
        self.assertTrue(carga.dados['status'].eq('ativo').all())
        self.assertTrue(carga.dados['codigo_sensor'].str.fullmatch(r'SNS-0x[0-9A-F]{4}').all())

    def test_id_com_conflito_nao_escolhe_versao_arbitraria(self):
        amostra = self.carga.dados.head(1).copy()
        alterada = amostra.copy()
        alterada['latencia_observada_ms'] += 5
        with self.assertRaisesRegex(ValueError, 'conflitantes'):
            self.carregar_amostra(pd.concat([amostra, alterada]))

    def test_coluna_obrigatoria_ausente(self):
        with self.assertRaisesRegex(ValueError, 'Colunas ausentes'):
            self.carregar_amostra(self.carga.dados.drop(columns='codigo_sensor'))

    def test_zero_infinito_e_prioridade_fracionaria_sao_rejeitados(self):
        amostra = self.carga.dados.head(5).copy()
        amostra.loc[amostra.index[0], 'latencia_observada_ms'] = 0
        amostra.loc[amostra.index[1], 'tensao_v'] = np.inf
        amostra['prioridade'] = amostra['prioridade'].astype(float)
        amostra.loc[amostra.index[2], 'prioridade'] = 1.5
        carga = self.carregar_amostra(amostra)
        self.assertEqual(len(carga.rejeitados), 3)
        self.assertEqual(len(carga.dados), 2)

    def test_consulta_nao_interpreta_regex(self):
        self.assertTrue(consultar_registros(self.carga.dados, modulo='[').empty)

    def test_carga_invalida_preserva_sessao_anterior(self):
        sistema = SCIC(ARQUIVO_DADOS)
        dados, fila = sistema.dados, sistema.fila
        with self.assertRaises(OSError):
            sistema.carregar(ARQUIVO_DADOS.with_name('nao_existe.csv'))
        self.assertIs(sistema.dados, dados)
        self.assertIs(sistema.fila, fila)

    def test_gerador_reproduz_base_sem_dependencia_de_diretorio(self):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / 'base.csv'
            nova = gerar_base(caminho)
            original = pd.read_csv(ARQUIVO_DADOS)
            pd.testing.assert_frame_equal(nova, original)


class TesteNumerico(unittest.TestCase):
    def test_limites_e_relativo_indefinido(self):
        dados = pd.DataFrame({'latencia_prevista_ms': [0, 1, 105, 115, 116],
                              'latencia_observada_ms': [0, 0.5, 100, 100, 100]})
        resultado = calcular_erros(dados)
        self.assertEqual(resultado['classificacao_erro'].tolist(),
                         ['indefinido', 'indefinido', 'aceitavel', 'atencao', 'critico'])
        self.assertTrue(resultado['erro_relativo'].iloc[:2].isna().all())
        self.assertEqual(resultado['erro_absoluto_ms'].iloc[2], 5)
        self.assertEqual(resultado['erro_relativo'].iloc[2], 0.05)

    def test_erro_grande_com_latencia_menor_nao_e_degradacao(self):
        resultado = calcular_erros(pd.DataFrame({'latencia_prevista_ms': [100], 'latencia_observada_ms': [50]}))
        self.assertEqual(resultado['classificacao_erro'].iloc[0], 'critico')
        self.assertFalse(resultado['degradacao'].iloc[0])

    def test_metricas_conhecidas_e_r2_negativo(self):
        resultado = metricas([0, 1], [1, 3])
        self.assertEqual(resultado['mae_ms'], 1.5)
        self.assertEqual(resultado['mse_ms2'], 2.5)
        self.assertAlmostEqual(resultado['rmse_ms'], np.sqrt(2.5))
        self.assertEqual(resultado['r2'], -9)

    def test_r2_alvo_constante_e_amostra_unica_indefinido(self):
        self.assertIsNone(metricas([1, 1], [1, 2])['r2'])
        self.assertIsNone(metricas([1], [2])['r2'])

    def test_potencia_respeita_arredondamento_e_detecta_corrupcao(self):
        dados = carregar_base().dados
        self.assertEqual(verificar_potencia(dados)['incoerentes'], 0)
        alterados = dados.copy()
        alterados.loc[0, 'potencia_w'] += 10
        self.assertEqual(verificar_potencia(alterados)['incoerentes'], 1)

    def test_conversao_entre_bases_e_eletricidade(self):
        sensor = converter_sensor('SNS-0x1A01')
        self.assertEqual(sensor['decimal'], 6657)
        self.assertEqual(int(sensor['binario'], 2), 6657)
        linha = {'nome_modulo': 'Antena', 'codigo_sensor': 'SNS-0x1A01',
                 'tensao_v': 48, 'corrente_a': 2.4, 'potencia_w': 115.2}
        exemplo = exemplo_eletrico(linha)
        self.assertAlmostEqual(exemplo['potencia_calculada_w'], 115.2)
        self.assertEqual(exemplo['resistencia_equivalente_ohm'], 20)
        with self.assertRaises(ValueError):
            converter_sensor('SNS-0xZZZZ')


class TesteModelo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = carregar_base().dados

    def test_particoes_temporais_disjuntas(self):
        treino, validacao, teste = separar_temporal(self.dados.sample(frac=1, random_state=7))
        self.assertLess(treino['data_registro'].max(), validacao['data_registro'].min())
        self.assertLess(validacao['data_registro'].max(), teste['data_registro'].min())
        self.assertTrue(set(treino.id_registro).isdisjoint(validacao.id_registro))
        self.assertTrue(set(treino.id_registro).isdisjoint(teste.id_registro))
        self.assertEqual(set(teste.ciclo), {'C009', 'C010'})

    def test_alterar_alvo_do_teste_nao_muda_modelo_nem_selecao(self):
        primeira = avaliar_modelo(self.dados)
        adulterada = self.dados.copy()
        adulterada.loc[adulterada['numero_ciclo'] >= 9, 'latencia_observada_ms'] += 10000
        segunda = avaliar_modelo(adulterada)
        np.testing.assert_array_equal(primeira.modelo.coef_, segunda.modelo.coef_)
        self.assertEqual(primeira.modelo.intercept_, segunda.modelo.intercept_)
        self.assertEqual(primeira.preferido, segunda.preferido)
        self.assertNotEqual(primeira.resumo['teste'], segunda.resumo['teste'])

    def test_recusa_historico_insuficiente_e_datas_sobrepostas(self):
        with self.assertRaisesRegex(ValueError, 'cinco ciclos'):
            separar_temporal(self.dados[self.dados['numero_ciclo'] < 5])
        alterada = self.dados.copy()
        alterada.loc[alterada['numero_ciclo'] == 2, 'data_registro'] = alterada['data_registro'].min()
        with self.assertRaisesRegex(ValueError, 'sobrepostas'):
            separar_temporal(alterada)


class TesteEstruturas(unittest.TestCase):
    def test_heap_equivale_ao_criterio_e_preserva_propriedade(self):
        rng = random.Random(42)
        alertas = [Alerta(i, 'Módulo', 'C001', rng.randint(1, 2), rng.randint(1, 5),
                          rng.randint(0, 9), rng.random(), 'Teste de fila') for i in range(150)]
        fila = FilaAlertas()
        for alerta in alertas:
            fila.inserir(alerta)
            for indice in range(1, len(fila._itens)):
                self.assertLessEqual(fila._itens[(indice - 1) // 2][:2], fila._itens[indice][:2])
        esperado = sorted(enumerate(alertas), key=lambda par: (par[1].chave, par[0]))
        self.assertEqual([a.id_registro for a in fila.em_ordem()], [a.id_registro for _, a in esperado])
        self.assertEqual(len(fila), 150)
        for _, alerta in esperado:
            self.assertEqual(fila.retirar(), alerta)
            for indice in range(1, len(fila._itens)):
                self.assertLessEqual(fila._itens[(indice - 1) // 2][:2], fila._itens[indice][:2])
        self.assertIsNone(fila.retirar())
        self.assertIsNone(fila.primeiro())

    def test_heap_desempata_em_ordem_de_entrada(self):
        primeiro = Alerta(3, 'A', 'C001', 1, 1, 0, 0.1, 'Primeiro')
        segundo = Alerta(1, 'B', 'C001', 1, 1, 0, 0.1, 'Segundo')
        fila = FilaAlertas([primeiro, segundo])
        self.assertEqual(fila.retirar(), primeiro)
        self.assertEqual(fila.retirar(), segundo)

    def test_leituras_rejeitadas_continuam_como_alertas(self):
        carga = carregar_base()
        fila = construir_fila(calcular_erros(carga.dados), carga.rejeitados)
        ids = {alerta.id_registro for alerta in fila.em_ordem()}
        self.assertTrue(set(carga.rejeitados.id_registro.astype(int)).issubset(ids))

    def test_trie_ignora_acentos_e_caixa_preservando_termo(self):
        trie = Trie()
        trie.inserir({'termo': 'Comunicação', 'tipo': 'modulo', 'ids': [1]})
        trie.inserir({'termo': 'Comando', 'tipo': 'comando', 'ids': [2]})
        self.assertEqual(trie.buscar_prefixo(' COMUNICACAO')[0]['termo'], 'Comunicação')
        self.assertEqual(len(trie.buscar_prefixo('co')), 2)
        self.assertEqual(len(trie.buscar_prefixo('co', limite=1)), 1)
        self.assertEqual(trie.buscar_prefixo(''), [])
        self.assertEqual(trie.buscar_prefixo('xyz'), [])

    def test_trie_retorna_ids_que_correspondem_aos_registros(self):
        dados = carregar_base().dados
        indice = construir_indice(dados)
        termo = indice.buscar_prefixo('ENF')[0]
        encontrados = dados[dados.id_registro.isin(termo['ids'])]
        self.assertTrue(encontrados.nome_modulo.eq('Enfermaria Central').all())
        self.assertEqual(set(termo['ids']), set(dados[dados.nome_modulo.eq('Enfermaria Central')].id_registro))


class TesteTerminal(unittest.TestCase):
    def test_relatorio_exporta_relativo_indefinido_sem_nan_em_json(self):
        carga = carregar_base()
        carga.dados['latencia_observada_ms'] = 0.5
        dados = calcular_erros(carga.dados)
        avaliacao = avaliar_modelo(dados)
        with TemporaryDirectory() as pasta:
            destino = gerar_relatorio(carga, dados, avaliacao,
                                      construir_fila(dados, carga.rejeitados), construir_indice(dados), pasta)
            resumo = json.loads((Path(pasta) / 'resultados/resumo_execucao.json').read_text(encoding='utf-8'))
            self.assertIsNone(resumo['indicadores']['erro_relativo_medio_pct'])
            self.assertIsNone(resumo['avaliacao']['teste']['regressao_linear']['r2'])
            self.assertIn('O erro relativo mediano é indefinido', destino.read_text(encoding='utf-8'))

    def test_menu_completo_funciona_fora_da_pasta_do_projeto(self):
        principal = Path(__file__).resolve().parents[1] / 'codigo_fonte.py'
        entradas = '\n'.join(['99', '1', '2', 'Antena', 'alerta', '1', '3', '4', '5',
                               '6', 'enf', '111', '7', '8', '9', '10', 'inexistente.csv', '10', '', '0', ''])
        with TemporaryDirectory() as pasta:
            processo = subprocess.run(
                [sys.executable, str(principal), '--saida', pasta], input=entradas,
                cwd=pasta, text=True, encoding='utf-8', capture_output=True, timeout=60,
            )
            self.assertEqual(processo.returncode, 0, processo.stderr)
            for esperado in ['Opção inválida', 'INDICADORES E ERROS NUMÉRICOS',
                             'REGRESSÃO LINEAR', 'FILA DE PRIORIDADE', 'Enfermaria Central',
                             '6657', 'Próximo para atendimento', 'ANÁLISE FINAL',
                             'Não foi possível concluir', 'Base carregada']:
                self.assertIn(esperado, processo.stdout)
            resumo = json.loads((Path(pasta) / 'resultados' / 'resumo_execucao.json').read_text(encoding='utf-8'))
            self.assertEqual(resumo['qualidade']['registros_validos'], 144)
            self.assertEqual(len(resumo['alertas']), 76)
            self.assertTrue((Path(pasta) / 'relatorio_tecnico.md').is_file())
            self.assertEqual(len(list((Path(pasta) / 'graficos_ou_imagens').glob('*.png'))), 3)

    def test_csv_inexistente_retorna_erro_claro(self):
        principal = Path(__file__).resolve().parents[1] / 'codigo_fonte.py'
        processo = subprocess.run([sys.executable, str(principal), '--dados', 'nao_existe.csv', '--demo'],
                                  text=True, encoding='utf-8', capture_output=True, timeout=30)
        self.assertEqual(processo.returncode, 1)
        self.assertIn('Erro na execução', processo.stdout)
        self.assertNotIn('Traceback', processo.stdout + processo.stderr)


if __name__ == '__main__':
    unittest.main()
