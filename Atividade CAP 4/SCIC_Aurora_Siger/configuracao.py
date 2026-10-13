"""Caminhos e limites operacionais da simulação Aurora Siger."""
from pathlib import Path

PASTA_PROJETO = Path(__file__).resolve().parent
ARQUIVO_DADOS = PASTA_PROJETO / 'dados_aurora_siger.csv'
PASTA_RESULTADOS = PASTA_PROJETO / 'resultados'
PASTA_GRAFICOS = PASTA_PROJETO / 'graficos_ou_imagens'
SEMENTE = 42
PISO_LATENCIA_MS = 1.0
LIMITE_ACEITAVEL = 0.05
LIMITE_ATENCAO = 0.15
TIPOS_MODULO = {
    'habitacao', 'agricultura', 'comunicacao', 'laboratorio',
    'suporte_medico', 'armazenamento_dados',
}

COLUNAS = [
    'id_registro', 'ciclo', 'data_registro', 'nome_modulo', 'tipo_modulo',
    'codigo_sensor', 'latencia_prevista_ms', 'latencia_observada_ms',
    'tensao_v', 'corrente_a', 'potencia_w', 'status', 'prioridade', 'mensagem_alerta',
]
