"""Operações CRUD genéricas do SIFSM, guiadas por uma descrição das tabelas.
Cada entidade descreve seus campos como:
    (nome_coluna, rótulo, tipo, obrigatório, extra)
Tipos: texto | int | float | bool | escolha | fk | auto
"""
import sqlite3
import math
from datetime import datetime

TIPOS_MODULO = ["energia", "habitacao", "agricultura", "laboratorio",
                "comunicacao", "suporte_medico", "armazenamento"]
TIPOS_SENSOR = ["consumo", "temperatura", "luminosidade", "umidade",
                "oxigenio", "carga", "presenca"]

ENTIDADES = {
    "modulos": {"titulo": "Módulos", "campos": [
        ("codigo", "Código (ex: MOD-ENE)", "texto", True, None),
        ("nome", "Nome", "texto", True, None),
        ("tipo", "Tipo", "escolha", True, TIPOS_MODULO),
        ("critico", "Módulo crítico? (s/n)", "bool", True, None),
        ("status", "Status", "escolha", True, ["ativo", "inativo", "manutencao"]),
    ]},
    "sensores": {"titulo": "Sensores", "campos": [
        ("codigo", "Código (ex: SEN-ENE-01)", "texto", True, None),
        ("tipo", "Tipo", "escolha", True, TIPOS_SENSOR),
        ("unidade", "Unidade (kWh, %, C...)", "texto", True, None),
        ("modulo_id", "ID do módulo", "fk", True, "modulos"),
        ("ativo", "Sensor ativo? (s/n)", "bool", True, None),
    ]},
    "leituras": {"titulo": "Leituras", "campos": [
        ("sensor_id", "ID do sensor", "fk", True, "sensores"),
        ("valor", "Valor medido", "float", True, None),
        ("data_hora", "", "auto", False, None),
    ]},
    "alertas": {"titulo": "Alertas", "campos": [
        ("modulo_id", "ID do módulo", "fk", True, "modulos"),
        ("descricao", "Descrição", "texto", True, None),
        ("nivel", "Nível", "escolha", True, ["baixo", "medio", "alto", "critico"]),
        ("resolvido", "Já resolvido? (s/n)", "bool", True, None),
        ("data_hora", "", "auto", False, None),
    ]},
    "manutencoes": {"titulo": "Manutenções", "campos": [
        ("modulo_id", "ID do módulo", "fk", True, "modulos"),
        ("descricao", "Descrição", "texto", True, None),
        ("status", "Status", "escolha", True, ["pendente", "em_andamento", "concluida"]),
        ("data_hora", "", "auto", False, None),
    ]},
}
def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def converter(conn, tipo, extra, texto):
    """Valida e converte a entrada do usuário. Levanta ValueError se for inválida."""
    texto = texto.strip()
    if tipo == "texto":
        if not texto:
            raise ValueError("o campo não pode ficar vazio.")
        return texto
    if tipo == "int":
        return int(texto)
    if tipo == "float":
        valor = float(texto.replace(",", "."))
        if not math.isfinite(valor):
            raise ValueError("o valor deve ser um número finito.")
        return valor
    if tipo == "bool":
        if texto.lower() in ("s", "sim", "1"):
            return 1
        if texto.lower() in ("n", "nao", "não", "0"):
            return 0
        raise ValueError("responda com 's' ou 'n'.")
    if tipo == "escolha":
        if texto.lower() not in extra:
            raise ValueError(f"escolha uma das opções: {', '.join(extra)}.")
        return texto.lower()
    if tipo == "fk":
        id_ref = int(texto)
        existe = conn.execute(f"SELECT 1 FROM {extra} WHERE id = ?", (id_ref,)).fetchone()
        if not existe:
            raise ValueError(f"não existe registro com id {id_ref} em '{extra}'.")
        return id_ref
    raise ValueError(f"tipo desconhecido: {tipo}")
def cadastrar(conn, entidade, dados):
    """CREATE: insere um registro. `dados` é um dict {coluna: valor já validado}."""
    campos = ENTIDADES[entidade]["campos"]
    if any(c[2] == "auto" for c in campos):
        dados.setdefault("data_hora", agora())
    colunas = ", ".join(dados)
    marcas = ", ".join("?" for _ in dados)
    try:
        cur = conn.execute(f"INSERT INTO {entidade} ({colunas}) VALUES ({marcas})",
                           list(dados.values()))
    except sqlite3.IntegrityError as erro:
        conn.rollback()
        raise ValueError(f"violação de integridade ({erro}). O código já existe?")
    else:
        conn.commit()
        return cur.lastrowid

def listar(conn, entidade, filtro_coluna=None, filtro_valor=None):
    """READ: devolve lista de registros (sqlite3.Row), opcionalmente filtrada."""
    sql = f"SELECT * FROM {entidade}"
    params = []
    if filtro_coluna:
        sql += f" WHERE {filtro_coluna} = ?"
        params.append(filtro_valor)
    return conn.execute(sql + " ORDER BY id", params).fetchall()

def buscar(conn, entidade, id_registro):
    return conn.execute(f"SELECT * FROM {entidade} WHERE id = ?", (id_registro,)).fetchone()

def alterar(conn, entidade, id_registro, novos_dados):
    """UPDATE: altera apenas as colunas informadas. Devolve True se achou o registro."""
    if not novos_dados:
        return False
    sets = ", ".join(f"{c} = ?" for c in novos_dados)
    try:
        cur = conn.execute(f"UPDATE {entidade} SET {sets} WHERE id = ?",
                           [*novos_dados.values(), id_registro])
    except sqlite3.IntegrityError as erro:
        conn.rollback()
        raise ValueError(f"violação de integridade ({erro}).")
    else:
        conn.commit()
        return cur.rowcount > 0

def excluir(conn, entidade, id_registro):
    """DELETE: remove o registro (e dependentes, via ON DELETE CASCADE)."""
    cur = conn.execute(f"DELETE FROM {entidade} WHERE id = ?", (id_registro,))
    conn.commit()
    return cur.rowcount > 0
