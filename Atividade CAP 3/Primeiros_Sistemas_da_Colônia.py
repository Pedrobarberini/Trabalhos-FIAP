# Dados da colônia organizado de forma hierárquica usando dicionários e listas
colonia = {
    "energia": {
        "baterias": 4500,
        "consumo": {
            "habitacao": 560,
            "laboratorio": 210,
            "manutencao": 130
        },
        "fontes": [{
                "tipo": "solar",
                "geracao": 3100
            },
            {
                "tipo": "eolico",
                "geracao": 1650
            }]
    },"clima": {
        "temperatura_externa": -25,
        "vento": 14,
        "temperatura_interna": 22,
        "umidade": 45
    }
}


# Soma do consumo total
def consumo_total():
    total = 0
    for valor in colonia["energia"]["consumo"].values():
        total += valor
    return total

# Mostrar fontes de energia
def mostrar_fontes():
    for fonte in colonia["energia"]["fontes"]:
        print(f"{fonte['tipo']} -> "f"{fonte['geracao']} kW")

# Verificar situação energética
def verificar_energia():
    geracao_total = 0 #Energia total gerada pelas fontes
    for fonte in colonia["energia"]["fontes"]:
        geracao_total += fonte["geracao"]

    consumo = consumo_total()
    print(f"Geração total: {geracao_total} kW")
    print(f"Consumo total: {consumo} kW")

    if consumo > geracao_total:
        print("ALERTA: consumo maior que geração")
    else:
        print("Energia suficiente")

# Programa principal
print("=== COLÔNIA AURORA SIGER ===\n")
print(f"Baterias: "f"{colonia['energia']['baterias']} kWh\n")
print("Fontes de energia:")

mostrar_fontes()
print()
verificar_energia()
print()

print(f"Temperatura interna: "f"{colonia['clima']['temperatura_interna']}°C")
print(f"Umidade interna: "f"{colonia['clima']['umidade']}%")