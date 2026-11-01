"""Camada de banco de dados do SIFSM (SQLite).
SQLite foi escolhido por ser um que não precisar de um
servidor. Toda a comunicação com o banco passa por este módulo.
"""
import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).parent / "aurora_siger.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS modulos (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo  TEXT NOT NULL UNIQUE,
    nome    TEXT NOT NULL,
    tipo    TEXT NOT NULL,
    critico INTEGER NOT NULL DEFAULT 0,
    status  TEXT NOT NULL DEFAULT 'ativo'
);
CREATE TABLE IF NOT EXISTS sensores (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo    TEXT NOT NULL UNIQUE,
    tipo      TEXT NOT NULL,
    unidade   TEXT NOT NULL,
    modulo_id INTEGER NOT NULL REFERENCES modulos(id) ON DELETE CASCADE,
    ativo     INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS leituras (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL REFERENCES sensores(id) ON DELETE CASCADE,
    valor     REAL NOT NULL,
    data_hora TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS alertas (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo_id INTEGER NOT NULL REFERENCES modulos(id) ON DELETE CASCADE,
    descricao TEXT NOT NULL,
    nivel     TEXT NOT NULL,
    resolvido INTEGER NOT NULL DEFAULT 0,
    data_hora TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS manutencoes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo_id INTEGER NOT NULL REFERENCES modulos(id) ON DELETE CASCADE,
    descricao TEXT NOT NULL,
    status    TEXT NOT NULL DEFAULT 'pendente',
    data_hora TEXT NOT NULL
);
"""
DADOS_EXEMPLO = """
INSERT INTO modulos (codigo, nome, tipo, critico, status) VALUES
  ('MOD-ENE', 'Central de Energia', 'energia', 1, 'ativo'),
  ('MOD-HAB', 'Habitação Principal', 'habitacao', 1, 'ativo'),
  ('MOD-AGR', 'Estufa Agrícola', 'agricultura', 0, 'ativo'),
  ('MOD-LAB', 'Laboratório', 'laboratorio', 0, 'ativo');
INSERT INTO sensores (codigo, tipo, unidade, modulo_id) VALUES
  ('SEN-ENE-01', 'consumo', 'kWh', 1),
  ('SEN-HAB-O2', 'oxigenio', '%', 2),
  ('SEN-AGR-UM', 'umidade', '%', 3),
  ('SEN-LAB-TP', 'temperatura', 'C', 4);
INSERT INTO leituras (sensor_id, valor, data_hora) VALUES
  (1, 42.5, '2026-10-01 08:00:00'), (1, 47.1, '2026-10-01 12:00:00'),
  (1, 55.8, '2026-10-01 16:00:00'), (2, 20.9, '2026-10-01 08:00:00'),
  (2, 20.4, '2026-10-01 12:00:00'), (3, 38.0, '2026-10-01 08:00:00'),
  (4, 22.3, '2026-10-01 08:00:00');
INSERT INTO alertas (modulo_id, descricao, nivel, resolvido, data_hora) VALUES
  (1, 'Consumo acima do esperado', 'alto', 0, '2026-10-01 16:05:00');
INSERT INTO manutencoes (modulo_id, descricao, status, data_hora) VALUES
  (3, 'Trocar filtro do sistema de irrigação', 'pendente', '2026-10-01 09:00:00');
"""
"""Abre a conexão e ativa as chaves estrangeiras (desligadas por padrão no SQLite)."""
def conectar(caminho=CAMINHO_BANCO):
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

"""Cria as tabelas e, se o banco estiver vazio, insere dados de exemplo."""
def inicializar(conn):
    
    conn.executescript(SCHEMA)
    vazio = conn.execute("SELECT COUNT(*) FROM modulos").fetchone()[0] == 0
    if vazio:
        conn.executescript(DADOS_EXEMPLO)
    conn.commit()
