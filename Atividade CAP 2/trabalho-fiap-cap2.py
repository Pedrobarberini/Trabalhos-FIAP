# Estruturas de dados
fila_pouso = []    
modulos_pousados = []  
pilha_alertas = []   


def cadastrar_modulo(nome, prioridade, combustivel, criticidade, sensores_ok, clima_ok, area_ok):
    modulo = {
        "nome": nome,
        "prioridade": prioridade,
        "combustivel": combustivel,
        "criticidade": criticidade,
        "sensores_ok": sensores_ok,
        "clima_ok": clima_ok,
        "area_ok": area_ok
    }
    fila_pouso.append(modulo)

# Buscar módulo com MENOR combustível
def buscar_menor_combustivel():
    return min(fila_pouso, key=lambda x: x["combustivel"])

# Buscar módulo com MAIOR prioridade
def buscar_maior_prioridade():
    return max(fila_pouso, key=lambda x: x["prioridade"])


# Ordenar por prioridade (maior primeiro)
def ordenar_por_prioridade():
    return sorted(fila_pouso, key=lambda x: x["prioridade"], reverse=True)


def autorizar_pouso(modulo):
    combustivel_ok = modulo["combustivel"] > 30
    clima_estavel = modulo["clima_ok"]
    sensores_ok = modulo["sensores_ok"]
    area_livre = modulo["area_ok"]

    # EXPRESSÃO BOOLEANA (AND, OR, NOT)
    # POUSO = combustível_ok AND clima_estavel AND area_livre AND NOT erro_sensor
    pouso_autorizado = (
        combustivel_ok and
        clima_estavel and
        area_livre and
        sensores_ok
    )

    return pouso_autorizado

def simular_pouso():
    global fila_pouso

    fila_ordenada = ordenar_por_prioridade()

    for modulo in fila_ordenada:
        print(f"\nAnalisando módulo: {modulo['nome']}")

        if autorizar_pouso(modulo):
            print(">>> POUSO AUTORIZADO")
            modulos_pousados.append(modulo)
        elif modulo["combustivel"] <= 30:
            print(">>> ALERTA: Combustível crítico!")
            pilha_alertas.append(f"{modulo['nome']} - combustível baixo")
        elif not modulo["sensores_ok"]:
            print(">>> ERRO: Falha nos sensores")
            pilha_alertas.append(f"{modulo['nome']} - falha sensores")
        else:
            print(">>> POUSO ADIADO")
            pilha_alertas.append(f"{modulo['nome']} - condições ruins")

    # Limpa fila após simulação
    fila_pouso = []

cadastrar_modulo("Habitação", 95, 60, 100, True, True, True)
cadastrar_modulo("Energia Solar", 90, 80, 90, True, True, True)
cadastrar_modulo("Laboratório", 70, 65, 60, True, False, True)
cadastrar_modulo("Suporte Médico", 95, 40, 100, False, True, True)
cadastrar_modulo("Comunicações", 85, 60, 85, True, True, False)


print("\n=== BUSCAS ===")
print("Menor combustível:", buscar_menor_combustivel()["nome"])
print("Maior prioridade:", buscar_maior_prioridade()["nome"])

print("\n=== SIMULAÇÃO DE POUSO ===")
simular_pouso()

print("\n=== MÓDULOS POUSADOS ===")
for m in modulos_pousados:
    print(m["nome"])

print("\n=== PILHA DE ALERTAS ===")
for alerta in reversed(pilha_alertas):
    print(alerta)


# utilizei lambda para facilitar a estrutra do codigo, e também para deixar mais legível as funções de busca e ordenação. ass. predinho se quiserem mudar fiquem avontade mas avisa no commit, e da commit em outra branch sem ser a main pra não sobre escreve a main.