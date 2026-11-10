"""Parte 2 integrada ao contrato executar(conn) e ao SQLite da Parte 1."""
import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import sys
from contextlib import redirect_stdout

import banco
import crud
from parte2 import Alerta, FilaPrioridade, Leitura, Sensor, avaliar_leitura, tabela_verdade

LIMITE_CONSUMO_KWH = 50.0
MINIMO_OXIGENIO_PCT = 19.5
PASTA = Path(__file__).resolve().parent
SCHEMA_PARTE2 = """
CREATE TABLE IF NOT EXISTS parte2_eventos (
    assinatura TEXT PRIMARY KEY,
    sensor_id INTEGER NOT NULL REFERENCES sensores(id) ON DELETE CASCADE,
    leitura_id INTEGER REFERENCES leituras(id) ON DELETE SET NULL,
    alerta_id INTEGER NOT NULL UNIQUE REFERENCES alertas(id) ON DELETE CASCADE,
    prioridade INTEGER NOT NULL CHECK (prioridade BETWEEN 1 AND 4),
    dados_json TEXT NOT NULL
);
"""


def consultar(conn, sql, parametros=()):
    cursor = conn.execute(sql, parametros)
    campos = [coluna[0] for coluna in cursor.description]
    return [dict(zip(campos, linha)) for linha in cursor.fetchall()]


def valor_json(valor):
    if isinstance(valor, float) and not math.isfinite(valor):
        return str(valor)
    return valor if type(valor) in (str, int, float, bool, type(None)) else str(valor)


def analisar(conn, *, limite_consumo_kwh=LIMITE_CONSUMO_KWH,
             minimo_oxigenio_pct=MINIMO_OXIGENIO_PCT):
    """Analisa o último registro de cada sensor, sem escrever no banco."""
    # Reutiliza as validações dos limites antes de ler ou alterar qualquer estado.
    Sensor('VALIDACAO', 'Configuração', True, limite_consumo_kwh, minimo_oxigenio_pct)
    registros = consultar(conn, """
        SELECT s.id AS sensor_id, s.codigo AS sensor_codigo, s.tipo AS sensor_tipo,
               s.unidade, s.ativo, m.id AS modulo_id, m.codigo AS modulo_codigo,
               m.nome AS modulo_nome, m.critico, m.status AS modulo_status,
               l.id AS leitura_id, l.valor, l.data_hora
        FROM sensores s
        JOIN modulos m ON m.id = s.modulo_id
        LEFT JOIN leituras l ON l.id = (
            SELECT recente.id FROM leituras recente WHERE recente.sensor_id = s.id
            ORDER BY recente.data_hora DESC, recente.id DESC LIMIT 1
        )
        ORDER BY COALESCE(l.data_hora, ''), COALESCE(l.id, 0), s.id
    """)
    fila = FilaPrioridade()
    resultados, fora_escopo = [], []
    for origem in registros:
        tipo = str(origem['sensor_tipo']).strip().lower()
        if tipo not in ('consumo', 'oxigenio'):
            fora_escopo.append({'sensor': origem['sensor_codigo'], 'tipo': tipo,
                               'motivo': 'Tipo reservado às demais análises; não exige oxigênio ou consumo fictício.'})
            continue
        if origem['critico'] not in (0, 1):
            raise ValueError(f"Módulo {origem['modulo_codigo']}: critico deve ser 0 ou 1.")
        unidade_correta = str(origem['unidade']).strip().lower() == ('kwh' if tipo == 'consumo' else '%')
        diagnosticos = []
        if origem['ativo'] != 1:
            diagnosticos.append('Sensor inativo ou com sinal de atividade inválido no cadastro.')
        if origem['leitura_id'] is None:
            diagnosticos.append('Sensor cadastrado sem leitura.')
        if not unidade_correta:
            diagnosticos.append(f"Unidade incompatível: {origem['unidade']!r}; não há conversão automática de kW para kWh.")
        data_valida = True
        if origem['leitura_id'] is not None:
            try:
                datetime.strptime(origem['data_hora'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                data_valida = False
                diagnosticos.append('Data da leitura inválida; esperado AAAA-MM-DD HH:MM:SS.')
        bruto = origem['valor']
        medicao = float(bruto) if type(bruto) in (int, float) and math.isfinite(bruto) else None
        if bruto is not None and medicao is None:
            diagnosticos.append('Valor não numérico ou não finito recebido do banco.')
        if not unidade_correta:
            medicao = None
        codigo_interno = f"BD-S{origem['sensor_id']}"
        sensor = Sensor(codigo_interno, origem['modulo_nome'], bool(origem['critico']),
                        limite_consumo_kwh, minimo_oxigenio_pct,
                        monitorar_consumo=tipo == 'consumo', monitorar_oxigenio=tipo == 'oxigenio')
        leitura = Leitura(
            f"{codigo_interno}-L{origem['leitura_id'] if origem['leitura_id'] is not None else 'SEM'}",
            codigo_interno, max(1, int(origem['leitura_id'] or 1)),
            medicao if tipo == 'consumo' else None, medicao if tipo == 'oxigenio' else None,
            origem['ativo'] == 1 and unidade_correta and data_valida and origem['leitura_id'] is not None,
        )
        resultado = avaliar_leitura(sensor, leitura)
        motivos = [*diagnosticos, *resultado.motivos]
        origem = {campo: valor_json(valor) for campo, valor in origem.items()}
        item = {'origem': origem, 'resultado': resultado.para_dict(), 'motivos': motivos,
                'limites': {'consumo_kwh': limite_consumo_kwh, 'oxigenio_pct': minimo_oxigenio_pct}}
        # Inclui valor, unidade, limites, criticidade e estado para detectar alterações via CRUD.
        item['assinatura'] = hashlib.sha256(
            json.dumps(item, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')
        ).hexdigest()
        resultados.append(item)
        if resultado.prioridade is not None:
            fila.inserir(Alerta(leitura.id, origem['sensor_codigo'], sensor.modulo, leitura.ciclo,
                               resultado.prioridade, tuple(motivos)))
    return {'regra': 'R = (E and C) or O or (not V)', 'avaliacoes': resultados,
            'fora_escopo': fora_escopo, 'fila': [item.para_dict() for item in fila.listar()],
            'vetor_heap': fila.vetor(),
            'limites': {'consumo_kwh': limite_consumo_kwh, 'oxigenio_pct': minimo_oxigenio_pct}}


def registrar_alertas(conn, **limites):
    """Persiste no esquema existente; a tabela auxiliar evita duplicação e mantém a origem."""
    conn.execute('SAVEPOINT sifsm_parte2')
    try:
        # A leitura e a gravação participam da mesma transação.
        analise = analisar(conn, **limites)
        conn.execute(SCHEMA_PARTE2)
        novos, existentes = 0, 0
        for item in analise['avaliacoes']:
            prioridade = item['resultado']['prioridade']
            if prioridade is None:
                continue
            if conn.execute('SELECT 1 FROM parte2_eventos WHERE assinatura = ?',
                            (item['assinatura'],)).fetchone():
                existentes += 1
                continue
            origem = item['origem']
            descricao = (f"[Parte 2] Sensor {origem['sensor_codigo']}; leitura "
                         f"{origem['leitura_id'] if origem['leitura_id'] is not None else 'ausente'}: "
                         + ' '.join(item['motivos']))
            nivel = {1: 'critico', 2: 'alto', 3: 'alto', 4: 'medio'}[prioridade]
            cursor = conn.execute(
                'INSERT INTO alertas (modulo_id, descricao, nivel, resolvido, data_hora) VALUES (?, ?, ?, 0, ?)',
                (origem['modulo_id'], descricao, nivel, crud.agora()),
            )
            conn.execute("""INSERT INTO parte2_eventos
                (assinatura, sensor_id, leitura_id, alerta_id, prioridade, dados_json)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (item['assinatura'], origem['sensor_id'], origem['leitura_id'], cursor.lastrowid,
                 prioridade, json.dumps(item, ensure_ascii=False, allow_nan=False)))
            novos += 1
    except Exception:
        conn.execute('ROLLBACK TO SAVEPOINT sifsm_parte2')
        conn.execute('RELEASE SAVEPOINT sifsm_parte2')
        raise
    else:
        conn.execute('RELEASE SAVEPOINT sifsm_parte2')
        return {'novos': novos, 'ja_registrados': existentes}


def fila_do_banco(conn):
    """Inclui alertas manuais e da Parte 2; resolvidos ficam fora da fila."""
    possui_auditoria = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'parte2_eventos'"
    ).fetchone() is not None
    ligacao = 'LEFT JOIN parte2_eventos p ON p.alerta_id = a.id' if possui_auditoria else ''
    campo_prioridade = 'p.prioridade' if possui_auditoria else 'NULL'
    registros = consultar(conn, f"""
        SELECT a.*, m.codigo AS codigo_modulo, m.nome AS nome_modulo,
               {campo_prioridade} AS prioridade_parte2
        FROM alertas a JOIN modulos m ON m.id = a.modulo_id
        {ligacao} WHERE a.resolvido = 0 ORDER BY a.data_hora, a.id
    """)
    fila = FilaPrioridade()
    for linha in registros:
        prioridade = linha['prioridade_parte2']
        if prioridade is None:
            prioridade = {'critico': 1, 'alto': 2, 'medio': 3, 'baixo': 4}.get(linha['nivel'], 1)
        fila.inserir(Alerta(f"ALERTA-{linha['id']}", linha['codigo_modulo'], linha['nome_modulo'],
                           linha['id'], prioridade, (linha['descricao'],)))
    return [alerta.para_dict() for alerta in fila.listar()]


def mostrar_analise(analise):
    print('\nPARTE 2 - LEITURAS DO SQLITE DA AURORA SIGER')
    print('R = (E AND C) OR O OR (NOT V)')
    for item in analise['avaliacoes']:
        origem, resultado = item['origem'], item['resultado']
        sinais = resultado['sinais']
        print(f"{origem['sensor_codigo']} | {origem['modulo_nome']} | leitura {origem['leitura_id']} "
              f"| valor {origem['valor']} {origem['unidade']} | "
              + ' '.join(f"{nome}={int(sinais[nome])}" for nome in ('E', 'C', 'O', 'V', 'R'))
              + f" | {resultado['classificacao']} | prioridade {resultado['prioridade']}")
        print('  ' + ' '.join(item['motivos']))
    for item in analise['fora_escopo']:
        print(f"{item['sensor']}: {item['tipo']} fora da regra de energia/oxigênio.")
    print(f"Fila calculada: {len(analise['fila'])} alerta(s).")
    for item in analise['fila']:
        print(f"  prioridade {item['prioridade']} | {item['codigo_sensor']} | {item['modulo']}")
    print('LED e buzzer são saídas virtuais; nenhum equipamento é desligado.')


def executar(conn):
    """Contrato chamado pela opção 6 do main.py da Parte 1."""
    mostrar_analise(analisar(conn))
    while True:
        print('\n1. Reanalisar leituras do banco\n2. Registrar novos alertas no banco'
              '\n3. Consultar fila de alertas não resolvidos\n4. Mostrar tabela-verdade\n0. Voltar')
        opcao = input('Parte 2: ').strip()
        if opcao == '0':
            return
        if opcao == '1':
            mostrar_analise(analisar(conn))
        elif opcao == '2':
            print('Resultado da gravação:', registrar_alertas(conn))
        elif opcao == '3':
            for alerta in fila_do_banco(conn):
                print(alerta)
        elif opcao == '4':
            print('E C O V | F EC R')
            for linha in tabela_verdade():
                print(' '.join(str(int(linha[chave])) for chave in ('E', 'C', 'O', 'V'))
                      + ' | ' + ' '.join(str(int(linha[chave])) for chave in ('F', 'EC', 'R')))
        else:
            print('Opção inválida.')


def demonstrar_sqlite(pasta):
    """Usa o schema e os dados de exemplo da Parte 1 em memória, sem tocar no banco local."""
    conn = banco.conectar(':memory:')
    try:
        banco.inicializar(conn)
        estado_inicial = {tabela: conn.execute(f'SELECT COUNT(*) FROM {tabela}').fetchone()[0]
                          for tabela in crud.ENTIDADES}
        analise = analisar(conn)
        mostrar_analise(analise)
        primeira = registrar_alertas(conn)
        segunda = registrar_alertas(conn)
        print('Primeira gravação:', primeira)
        print('Repetição da gravação:', segunda)
        fila = fila_do_banco(conn)
        print('Alertas pendentes do banco:')
        for alerta in fila:
            print(alerta)
        evidencia = {'cenario': 'Schema e dados de exemplo da Parte 1 em SQLite :memory:',
                     'estado_inicial': estado_inicial, 'analise': analise,
                     'primeira_gravacao': primeira, 'segunda_gravacao': segunda,
                     'fila_banco': fila, 'tabela_verdade': tabela_verdade(),
                     'alertas_apos_gravacao': consultar(conn, 'SELECT * FROM alertas ORDER BY id')}
        pasta = Path(pasta)
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / 'execucao_sqlite.json').write_text(
            json.dumps(evidencia, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
        with (pasta / 'alertas_banco.csv').open('w', encoding='utf-8', newline='') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(['id_alerta', 'prioridade', 'modulo', 'descricao'])
            for alerta in fila:
                escritor.writerow([alerta['id_leitura'], alerta['prioridade'], alerta['modulo'],
                                    ' '.join(alerta['motivos'])])
        print('Evidências SQLite geradas; o banco de uso local foi preservado.')
        return evidencia
    finally:
        conn.close()


def main(argumentos=None):
    argumentos = list(sys.argv[1:] if argumentos is None else argumentos)
    if '--cenario-json' in argumentos:
        from parte2.demo import main as demonstracao_json
        return demonstracao_json([arg for arg in argumentos if arg != '--cenario-json'])
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='Parte 2 integrada ao SQLite da Parte 1 do SIFSM.')
    parser.add_argument('--demo', action='store_true', help='Demonstra a integração em banco isolado.')
    parser.add_argument('--saida', type=Path, default=PASTA / 'evidencias/parte2_sqlite')
    args = parser.parse_args(argumentos)
    if not args.demo:
        parser.error('Use python main.py e a opção 6, ou --demo para a validação isolada.')
    texto = io.StringIO()
    with redirect_stdout(texto):
        demonstrar_sqlite(args.saida)
    saida = texto.getvalue()
    print(saida, end='')
    (args.saida / 'terminal_sqlite.txt').write_text(saida, encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
