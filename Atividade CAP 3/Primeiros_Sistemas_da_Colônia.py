# Dados da colônia organizado de forma hierárquica usando dicionários e listas
# com consumo e geração em diferentes cenários
colonia = {
    "nome": "Aurora Singer",
    "localizacao": "Marte",
    "modulos_totais": 9,
    "energia": {
        "baterias": 4400,  # Capacidade total em kWh
        "carga_atual": 4400,  # Carga atual das baterias
        # Consumo por módulo em diferentes cenários (em Watts)
        "consumo": {
            "cenarios": {
                "dia": {
                    "habitacao": 5000,
                    "energia": 300,
                    "laboratorio": 3500,
                    "logistica": 1500,
                    "saude": 4000,
                    "comunicacoes": 1000,
                    "agricultura": 2500,
                    "reciclagem": 3000,
                    "defesa": 1200,
                    "total": 22000,  # em W ou 22 kW
                },
                "dia_tempestade": {
                    "habitacao": 6500,
                    "energia": 700,
                    "laboratorio": 2000,
                    "logistica": 1800,
                    "saude": 5000,
                    "comunicacoes": 2500,
                    "agricultura": 3500,
                    "reciclagem": 3500,
                    "defesa": 2000,
                    "total": 27500,  # em W ou 27.5 kW
                },
                "noite": {
                    "habitacao": 8500,
                    "energia": 400,
                    "laboratorio": 4000,
                    "logistica": 2500,
                    "saude": 6000,
                    "comunicacoes": 1200,
                    "agricultura": 5000,
                    "reciclagem": 4500,
                    "defesa": 1500,
                    "total": 33600,  # em W ou 33.6 kW
                },
                "noite_tempestade": {
                    "habitacao": 10000,
                    "energia": 900,
                    "laboratorio": 1500,
                    "logistica": 2800,
                    "saude": 7500,
                    "comunicacoes": 3000,
                    "agricultura": 6500,
                    "reciclagem": 5000,
                    "defesa": 2500,
                    "total": 39700,  # em W ou 39.7 kW
                },
            }
        },
        # Geração de energia em diferentes cenários (em Watts)
        "geracao": {
            "cenarios": {
                "dia": {"solar": 160000, "eolica": 100, "total": 160100},  # 160 kW
                "dia_tempestade": {
                    "solar": 2000,  # Reduz drasticamente com tempestade
                    "eolica": 450,
                    "total": 2450,
                },
                "noite": {
                    "solar": 0,  # Sem geração solar à noite
                    "eolica": 120,
                    "total": 120,
                },
                "noite_tempestade": {
                    "solar": 0,
                    "eolica": 550,  # Aumenta com mais vento
                    "total": 550,
                },
            }
        },
    },
    "clima": {
        "temperatura_externa": -25,
        "vento": 14,  # m/s
        "temperatura_interna": 22,
        "umidade": 45,  # Percentual
        "tempestade_areia": False,
    },
}


# Função:Calcula o percentual de bateria
def calcular_percentual_carga():
    # Calcula quantos % de bateria temos
    carga_atual = colonia["energia"]["carga_atual"]
    capacidade_total = colonia["energia"]["baterias"]
    percentual = (carga_atual / capacidade_total) * 100
    return percentual


# Função:Exibe o clima
def exibir_clima():
    # Mostra as condições do clima atual
    print("\n" + "=" * 70)
    print("CONDIÇÕES CLIMÁTICAS")
    print("=" * 70)

    temp_externa = colonia["clima"]["temperatura_externa"]
    temp_interna = colonia["clima"]["temperatura_interna"]
    vento = colonia["clima"]["vento"]
    umidade = colonia["clima"]["umidade"]
    tempestade = colonia["clima"]["tempestade_areia"]

    print(f"Temperatura Externa: {temp_externa}°C")
    print(f"Temperatura Interna: {temp_interna}°C")
    print(f"Velocidade do Vento: {vento} m/s")
    print(f"Umidade: {umidade}%")

    if tempestade:
        print("Tempestade de Areia: SIM")
    else:
        print("Tempestade de Areia: Não")

    print("=" * 70)


# Função:Exibe o status de energia
def exibir_status_energia():
    # Mostra o status da bateria
    print("\n" + "=" * 70)
    print("STATUS DE ENERGIA")
    print("=" * 70)

    carga = colonia["energia"]["carga_atual"]
    capacidade = colonia["energia"]["baterias"]
    percentual = calcular_percentual_carga()

    print(f"Bateria Atual: {carga} kWh")
    print(f"Capacidade Total: {capacidade} kWh")
    print(f"Percentual: {percentual:.1f}%")

    print("=" * 70)


# Função:Determina o modo de operação
def determinar_modo():
    # Decide qual modo a colônia vai usar
    percentual = calcular_percentual_carga()
    tem_tempestade = colonia["clima"]["tempestade_areia"]

    # Modo NORMAL: bateria > 60% E sem tempestade
    if percentual > 60 and not tem_tempestade:
        return "NORMAL"

    # Modo ECONOMIA: bateria entre 30% e 60%
    elif percentual >= 30 and percentual <= 60:
        return "ECONOMIA"

    # Modo CRÍTICO: bateria < 30%
    else:
        return "CRITICO"


# Função:Exibe o modo de operação
def exibir_modo_operacao():
    # Mostra qual é o modo e quais módulos estão ligados
    modo = determinar_modo()

    print("\n" + "=" * 70)
    print(f"MODO DE OPERAÇÃO: {modo}")
    print("=" * 70)

    if modo == "NORMAL":
        print("MODO NORMAL - Operação total")
        print("\nTodos os 9 módulos operando em 100%:")
        print("   Habitação")
        print("   Energia")
        print("   Laboratório Científico")
        print("   Logística e Armazenamento")
        print("   Suporte Médico")
        print("   Comunicações")
        print("   Agricultura Hidropônica")
        print("   Reciclagem e Água")
        print("   Defesa e Segurança")

    elif modo == "ECONOMIA":
        print("MODO ECONOMIA - Corte de cargas não essenciais")
        print("\nMantendo os módulos essenciais:")
        print("   Habitação")
        print("   Suporte Médico")
        print("   Comunicações")
        print("   Reciclagem e Água")
        print("\nDesativando os módulos não essenciais:")
        print("   Laboratório Científico")
        print("   Logística e Armazenamento")
        print("   Agricultura Hidropônica")
        print("   Defesa e Segurança")

    elif modo == "CRITICO":
        print("MODO CRÍTICO - Emergência!")
        print("\nMantendo APENAS os módulos vitais:")
        print("   Habitação")
        print("   Suporte Médico")
        print("\nDesativando todos os outros 7 módulos")
        print("\nALERTA: Modo de Emergência Ativado!")
        print("Priorizando Suporte à Vida!")

    print("=" * 70)


# Função:Verificar umidade
def verificar_umidade():
    # Verifica se a umidade está normal
    print("\n--- Verificação de Umidade ---")

    umidade = colonia["clima"]["umidade"]

    if umidade < 30 or umidade > 60:
        print(f"ALERTA: Umidade fora do padrão ({umidade}%)")
        print("Verificar sistemas de HVAC")
    else:
        print(f" * Umidade em níveis normais: {umidade}%")


# Função:Verificar geração de energia
def verificar_energia_sistemas():
    # Verifica se os sistemas de geração estão funcionando
    print("\n--- Verificação dos Sistemas de Geração ---")

    cenario = "dia"  # Simulação
    geracao_solar = colonia["energia"]["geracao"]["cenarios"][cenario]["solar"]
    geracao_eolica = colonia["energia"]["geracao"]["cenarios"][cenario]["eolica"]
    vento = colonia["clima"]["vento"]

    # Verifica geraçãosolar
    if geracao_solar == 0:
        print("ALERTA: Sistema solar não está gerando energia!")
    else:
        print(f"Sistema solar está funcionando: {geracao_solar} W")

    # Verifica geraçãoeólica
    if geracao_eolica == 0 and vento > 12:
        print("ALERTA: Sistema eólico não está funcionando!")
    else:
        print(f"Sistema eólico está funcionando: {geracao_eolica} W")


# PROGRAMA PRINCIPAL
print("\n")
print("=" * 70)
print(f"SISTEMA DE GERENCIAMENTO DA COLÔNIA {colonia['nome'].upper()}")
print("Localização: Marte")
print("9 Módulos Instalados")
print("=" * 70)

# Chama as funções na ordem desejada
exibir_clima()
exibir_status_energia()
exibir_modo_operacao()

# Verifica os  alertas
print("\n" + "=" * 70)
print("VERIFICAÇÃO DOS SISTEMAS")
print("=" * 70)

verificar_umidade()
verificar_energia_sistemas()

print("\n" + "=" * 70)
print("FIM DO RELATÓRIO")
print("=" * 70)
