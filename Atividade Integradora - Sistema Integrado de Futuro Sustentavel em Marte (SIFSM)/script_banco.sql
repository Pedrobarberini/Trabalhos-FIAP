-- Tabelas da Parte 1 e auditoria da Parte 2 do SIFSM.
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

CREATE TABLE IF NOT EXISTS parte2_eventos (
    assinatura TEXT PRIMARY KEY,
    sensor_id INTEGER NOT NULL REFERENCES sensores(id) ON DELETE CASCADE,
    leitura_id INTEGER REFERENCES leituras(id) ON DELETE SET NULL,
    alerta_id INTEGER NOT NULL UNIQUE REFERENCES alertas(id) ON DELETE CASCADE,
    prioridade INTEGER NOT NULL CHECK (prioridade BETWEEN 1 AND 4),
    dados_json TEXT NOT NULL
);
