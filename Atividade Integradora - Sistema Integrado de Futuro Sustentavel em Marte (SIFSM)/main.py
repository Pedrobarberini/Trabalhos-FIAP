"""SIFSM - Sistema Integrado de Futuro Sustentável em Marte (Aurora Siger).
menu interativo + CRUD + banco de dados + tratamento de erros.
Execute com:  python main.py
"""
import sqlite3
import banco
import crud
import integracao

"""Lê um inteiro; repete até o usuário digitar um valor válido."""
def ler_numero(msg):
    while True:
        try:
            return int(input(msg).strip())
        except ValueError:
            print("Entrada inválida: digite um número inteiro.")

def mostrar(registros):
    if not registros:
        print("(nenhum registro encontrado)")
        return
    colunas = registros[0].keys()
    print("  " + " | ".join(colunas))
    print("  " + "-" * 60)
    for r in registros:
        print("  " + " | ".join(str(r[c]) for c in colunas))
def escolher_entidade():
    nomes = list(crud.ENTIDADES)
    for i, n in enumerate(nomes, 1):
        print(f"  {i}. {crud.ENTIDADES[n]['titulo']}")
    print("  0. Voltar")
    op = ler_numero("Escolha: ")
    return nomes[op - 1] if 1 <= op <= len(nomes) else None

"""Pergunta cada campo. Em alteração (atual != None), Enter mantém o valor."""
def pedir_campos(conn, entidade, atual=None):
    dados = {}
    for nome, rotulo, tipo, obrigatorio, extra in crud.ENTIDADES[entidade]["campos"]:
        if tipo == "auto":
            continue
        dica = f" [{atual[nome]}]" if atual else ""
        while True:
            texto = input(f"  {rotulo}{dica}: ")
            if atual and not texto.strip():
                break  # mantém o valor atual
            try:
                dados[nome] = crud.converter(conn, tipo, extra, texto)
            except ValueError as erro:
                print(f"  Valor inválido: {erro}")
            else:
                break
    return dados

def acao_cadastrar(conn):
    entidade = escolher_entidade()
    if entidade:
        novo_id = crud.cadastrar(conn, entidade, pedir_campos(conn, entidade))
        print(f"Registro cadastrado com id {novo_id}.")

def acao_listar(conn):
    entidade = escolher_entidade()
    if entidade:
        mostrar(crud.listar(conn, entidade))
def acao_alterar(conn):
    entidade = escolher_entidade()
    if not entidade:
        return
    id_reg = ler_numero("  ID do registro: ")
    atual = crud.buscar(conn, entidade, id_reg)
    if atual is None:
        print("Registro não encontrado.")
        return
    print("  (Enter mantém o valor entre colchetes)")
    novos = pedir_campos(conn, entidade, atual)
    print("Registro alterado." if crud.alterar(conn, entidade, id_reg, novos)
          else "  Nada foi alterado.")

def acao_excluir(conn):
    entidade = escolher_entidade()
    if not entidade:
        return
    id_reg = ler_numero("  ID do registro: ")
    if crud.buscar(conn, entidade, id_reg) is None:
        print("Registro não encontrado.")
        return
    aviso = " (isso apaga também os registros dependentes)" if entidade in ("modulos", "sensores") else ""
    if input(f"Confirma a exclusão{aviso}? (s/n): ").strip().lower() == "s":
        crud.excluir(conn, entidade, id_reg)
        print("Registro excluído.")
    else:
        print("Exclusão cancelada.")

def acao_exportar(conn):
    total, caminho = integracao.exportar_leituras_csv(conn)
    print(f"{total} leituras exportadas para '{caminho}'.")

MENU = """
===== SIFSM - Aurora Siger =====
 1. Cadastrar registro
 2. Listar registros
 3. Alterar registro
 4. Excluir registro
 5. Exportar leituras para CSV

 6. Regras lógicas, alertas e estruturas de dados
 7. Simulação e regressão linear
 8. Agentes de IA e arquitetura
 0. Sair
"""
def main():
    conn = None
    try:
        conn = banco.conectar()
        banco.inicializar(conn)
        acoes = {"1": acao_cadastrar, "2": acao_listar, "3": acao_alterar,
                 "4": acao_excluir, "5": acao_exportar}
        externas = {"6": "2", "7": "3", "8": "4"}
        while True:
            print(MENU)
            opcao = input("Opção: ").strip()
            if opcao == "0":
                break
            try:
                if opcao in acoes:
                    acoes[opcao](conn)
                elif opcao in externas:
                    integracao.executar_parte(conn, externas[opcao])
                else:
                    print("Opção inválida.")
            except ValueError as erro:
                print(f"Não foi possível concluir a operação: {erro}")
            except sqlite3.Error as erro:
                conn.rollback()
                print(f"Erro no banco de dados: {erro}")
            except Exception as erro:  # falha numa parte integrada não derruba o menu
                print(f"Erro inesperado: {erro}")
    except sqlite3.Error as erro:
        print(f"Não foi possível acessar o banco de dados: {erro}")
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado pelo usuário.")
    finally:
        if conn:
            conn.close()
        print("Conexão encerrada. Até logo!")

main()
