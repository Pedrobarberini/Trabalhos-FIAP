"""Compatibilidade entre a Parte 2, o schema, o CRUD e o menu da Parte 1."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import banco
import crud
import integracao
import main
import parte2_regras as regras


class IntegracaoSQLite(unittest.TestCase):
    def setUp(self):
        self.conn = banco.conectar(':memory:')
        banco.inicializar(self.conn)

    def tearDown(self):
        self.conn.close()

    def avaliacao(self, codigo):
        return next(item for item in regras.analisar(self.conn)['avaliacoes']
                    if item['origem']['sensor_codigo'] == codigo)

    def test_dados_publicados_sao_lidos_sem_exigir_canais_inexistentes(self):
        analise = regras.analisar(self.conn)
        self.assertEqual(len(analise['avaliacoes']), 2)
        self.assertEqual(len(analise['fora_escopo']), 2)
        energia = self.avaliacao('SEN-ENE-01')
        oxigenio = self.avaliacao('SEN-HAB-O2')
        self.assertEqual(energia['origem']['valor'], 55.8)
        self.assertEqual(energia['origem']['leitura_id'], 3)
        self.assertTrue(energia['resultado']['sinais']['V'])
        self.assertTrue(energia['resultado']['sinais']['R'])
        self.assertEqual(energia['resultado']['prioridade'], 3)
        self.assertEqual(oxigenio['origem']['valor'], 20.4)
        self.assertTrue(oxigenio['resultado']['sinais']['V'])
        self.assertFalse(oxigenio['resultado']['sinais']['R'])
        self.assertEqual(len(analise['fila']), 1)

    def test_analise_nao_escreve_ou_cria_tabelas(self):
        mudancas = self.conn.total_changes
        antes = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        regras.analisar(self.conn)
        self.assertEqual(self.conn.total_changes, mudancas)
        self.assertEqual(antes, self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())

    def test_persistencia_idempotente_preserva_alerta_manual(self):
        original = dict(crud.buscar(self.conn, 'alertas', 1))
        self.assertEqual(regras.registrar_alertas(self.conn), {'novos': 1, 'ja_registrados': 0})
        self.assertEqual(regras.registrar_alertas(self.conn), {'novos': 0, 'ja_registrados': 1})
        self.assertEqual(len(crud.listar(self.conn, 'alertas')), 2)
        self.assertEqual(dict(crud.buscar(self.conn, 'alertas', 1)), original)
        evento = self.conn.execute('SELECT * FROM parte2_eventos').fetchone()
        self.assertEqual(evento['sensor_id'], 1)
        self.assertEqual(evento['leitura_id'], 3)
        self.assertEqual(evento['prioridade'], 3)
        self.assertTrue(json.loads(evento['dados_json'])['resultado']['sinais']['R'])

    def test_alteracao_via_crud_chega_ao_circuito(self):
        crud.alterar(self.conn, 'leituras', 5, {'valor': 18.0})
        resultado = self.avaliacao('SEN-HAB-O2')
        self.assertEqual(resultado['resultado']['prioridade'], 1)
        self.assertEqual(regras.analisar(self.conn)['fila'][0]['codigo_sensor'], 'SEN-HAB-O2')
        crud.alterar(self.conn, 'modulos', 1, {'critico': 0})
        energia = self.avaliacao('SEN-ENE-01')
        self.assertFalse(energia['resultado']['sinais']['R'])
        self.assertEqual(energia['resultado']['classificacao'], 'atencao')
        self.assertEqual(energia['resultado']['prioridade'], 4)

    def test_mudanca_de_leitura_reconhece_novo_evento(self):
        regras.registrar_alertas(self.conn)
        crud.alterar(self.conn, 'leituras', 3, {'valor': 60.0})
        self.assertEqual(regras.registrar_alertas(self.conn)['novos'], 1)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM parte2_eventos').fetchone()[0], 2)

    def test_limites_sao_configuraveis_e_validados(self):
        resultado = regras.analisar(self.conn, limite_consumo_kwh=60.0)
        self.assertEqual(resultado['fila'], [])
        with self.assertRaises(ValueError):
            regras.analisar(self.conn, limite_consumo_kwh=-1)

    def test_sensor_sem_leitura_gera_evento_e_nao_duplica(self):
        self.conn.execute('DELETE FROM leituras WHERE sensor_id=1')
        self.conn.commit()
        resultado = self.avaliacao('SEN-ENE-01')
        self.assertTrue(resultado['resultado']['sinais']['F'])
        self.assertEqual(resultado['resultado']['prioridade'], 2)
        self.assertIsNone(resultado['origem']['leitura_id'])
        regras.registrar_alertas(self.conn)
        self.assertEqual(regras.registrar_alertas(self.conn)['novos'], 0)

    def test_exclusao_da_ultima_leitura_volta_a_leitura_anterior(self):
        crud.excluir(self.conn, 'leituras', 3)
        energia = self.avaliacao('SEN-ENE-01')
        self.assertEqual(energia['origem']['leitura_id'], 2)
        self.assertEqual(energia['origem']['valor'], 47.1)
        self.assertFalse(energia['resultado']['sinais']['R'])

    def test_sensor_inativo_ou_unidade_incompativel_gera_falha(self):
        crud.alterar(self.conn, 'sensores', 1, {'ativo': 0})
        resultado = self.avaliacao('SEN-ENE-01')
        self.assertTrue(resultado['resultado']['sinais']['F'])
        crud.alterar(self.conn, 'sensores', 1, {'ativo': 1, 'unidade': 'kW'})
        resultado = self.avaliacao('SEN-ENE-01')
        self.assertTrue(resultado['resultado']['sinais']['F'])
        self.assertIsNone(resultado['resultado']['leitura']['consumo_kwh'])
        self.assertTrue(any('Unidade incompatível' in item for item in resultado['motivos']))

    def test_valor_nao_finito_recebido_diretamente_do_banco_e_tratado(self):
        self.conn.execute('UPDATE leituras SET valor=? WHERE id=3', (float('inf'),))
        self.conn.commit()
        energia = self.avaliacao('SEN-ENE-01')
        self.assertTrue(energia['resultado']['sinais']['F'])
        self.assertEqual(energia['origem']['valor'], 'inf')
        json.dumps(energia, allow_nan=False)

    def test_entrada_crud_recusa_nan_e_infinito(self):
        for valor in ('nan', 'inf', '-inf'):
            with self.assertRaises(ValueError):
                crud.converter(self.conn, 'float', None, valor)
        self.assertEqual(crud.converter(self.conn, 'float', None, '42,5'), 42.5)

    def test_data_invalida_e_detectada(self):
        self.conn.execute("UPDATE leituras SET data_hora='data-invalida' WHERE id=3")
        self.conn.commit()
        energia = self.avaliacao('SEN-ENE-01')
        self.assertTrue(energia['resultado']['sinais']['F'])
        self.assertTrue(any('Data da leitura inválida' in item for item in energia['motivos']))

    def test_alerta_resolvido_sai_da_fila_sem_reabrir_na_reanalise(self):
        regras.registrar_alertas(self.conn)
        crud.alterar(self.conn, 'alertas', 2, {'resolvido': 1})
        self.assertEqual([item['id_leitura'] for item in regras.fila_do_banco(self.conn)], ['ALERTA-1'])
        self.assertEqual(regras.registrar_alertas(self.conn)['novos'], 0)
        self.assertEqual(crud.buscar(self.conn, 'alertas', 2)['resolvido'], 1)

    def test_falha_na_gravacao_reverte_o_lote_de_alertas(self):
        crud.alterar(self.conn, 'leituras', 5, {'valor': 18.0})
        self.conn.execute(regras.SCHEMA_PARTE2)
        self.conn.executescript("""
            CREATE TRIGGER recusar_evento BEFORE INSERT ON parte2_eventos
            WHEN NEW.sensor_id=1 BEGIN SELECT RAISE(ABORT, 'falha simulada'); END;
        """)
        with self.assertRaises(sqlite3.IntegrityError):
            regras.registrar_alertas(self.conn)
        self.assertEqual(len(crud.listar(self.conn, 'alertas')), 1)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM parte2_eventos').fetchone()[0], 0)

    def test_gravacao_preserva_transacao_externa_do_chamador(self):
        self.conn.execute("UPDATE modulos SET nome='Nome em transação' WHERE id=1")
        regras.registrar_alertas(self.conn)
        self.assertTrue(self.conn.in_transaction)
        self.conn.rollback()
        self.assertEqual(len(crud.listar(self.conn, 'alertas')), 1)
        self.assertEqual(crud.buscar(self.conn, 'modulos', 1)['nome'], 'Central de Energia')

    def test_menu_original_chama_a_parte2_e_crud_lista_os_novos_alertas(self):
        saida = io.StringIO()
        with patch('banco.conectar', return_value=self.conn), patch('builtins.input', side_effect=['6', '2', '0', '2', '4', '0']), redirect_stdout(saida):
            main.main()
        texto = saida.getvalue()
        self.assertIn('PARTE 2 - LEITURAS DO SQLITE', texto)
        self.assertIn('SEN-ENE-01', texto)
        self.assertIn("'novos': 1", texto)
        self.assertIn('[Parte 2] Sensor', texto)
        self.assertIn('Conexão encerrada', texto)
        self.assertNotIn('ainda não foi adicionado', texto)
        self.assertNotIn('Erro inesperado', texto)

    def test_entrada_padronizada_importa_menu_sem_criar_banco(self):
        import codigo_fonte
        self.assertIs(codigo_fonte.main, main.main)

    def test_demo_sqlite_portavel_e_isolada(self):
        principal = Path(__file__).resolve().parents[1] / 'parte2_regras.py'
        with TemporaryDirectory() as pasta:
            processo = subprocess.run(
                [sys.executable, '-S', str(principal), '--demo', '--saida', pasta],
                cwd=pasta, capture_output=True, text=True, encoding='utf-8', timeout=20)
            self.assertEqual(processo.returncode, 0, processo.stderr)
            evidencia = json.loads((Path(pasta) / 'execucao_sqlite.json').read_text(encoding='utf-8'))
            self.assertEqual(evidencia['estado_inicial']['leituras'], 7)
            self.assertEqual(evidencia['primeira_gravacao']['novos'], 1)
            self.assertEqual(evidencia['segunda_gravacao']['novos'], 0)
            self.assertEqual(len(evidencia['alertas_apos_gravacao']), 2)
            self.assertFalse((Path(pasta) / 'aurora_siger.db').exists())


if __name__ == '__main__':
    unittest.main()
