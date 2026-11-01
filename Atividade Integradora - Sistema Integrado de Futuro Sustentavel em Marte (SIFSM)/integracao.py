"""Pontos de integração com as outras partes.
o menu continua funcionando e avisa que a parte não foi integrada.
Cada executar(conn) recebe a conexão SQLite aberta e pode usar crud.listar().
"""
import csv
import importlib

MODULOS_EXTERNOS = {
    "2": ("Regras lógicas, alertas e estruturas de dados", "parte2_regras"),
    "3": ("Simulação e regressão linear", "parte3_simulacao"),
    "4": ("Agentes de IA e arquitetura", "parte4_ia"),
}

def executar_parte(conn, opcao):
    titulo, nome_modulo = MODULOS_EXTERNOS[opcao]
    try:
        modulo = importlib.import_module(nome_modulo)
        funcao = modulo.executar
    except ModuleNotFoundError:
        print(f"\n[!] '{nome_modulo}.py' ainda não foi adicionado à pasta ({titulo}).")
    except AttributeError:
        print(f"\n[!] '{nome_modulo}.py' precisa definir a função executar(conn).")
    else:
        print(f"\n--- {titulo} ---")
        funcao(conn)

def exportar_leituras_csv(conn, caminho="leituras_exportadas.csv"):
    """Gera um CSV com as leituras (útil para a regressão da Parte 3 com Pandas)."""
    linhas = conn.execute("""
        SELECT l.id, s.codigo AS sensor, s.tipo, s.unidade, m.codigo AS modulo,
               l.valor, l.data_hora
        FROM leituras l
        JOIN sensores s ON s.id = l.sensor_id
        JOIN modulos m ON m.id = s.modulo_id
        ORDER BY l.data_hora""").fetchall()
    with open(caminho, "w", newline="", encoding="utf-8") as arq:
        escritor = csv.writer(arq)
        escritor.writerow(linhas[0].keys() if linhas else ["sem_dados"])
        escritor.writerows([tuple(l) for l in linhas])
    return len(linhas), caminho
