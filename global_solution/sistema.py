

import csv
COL_SOLAR    = 0  
COL_EOLICA   = 1 
COL_CONSUMO  = 2 
COL_RESERVA  = 3   
COL_TEMP     = 4   
COL_RADIACAO = 5   
COL_QUALCOM  = 6   

PRIORIDADE = {"CRITICO": 0, "ALERTA": 1, "NORMAL": 2}
def ler_telemetria(caminho):
    horarios = []
    matriz = []
    with open(r"C:\Users\Igor\Downloads\Global Solutions\dados.csv", "r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)         
        for linha in leitor:
            horarios.append(linha["horario"])
            leitura = [
                int(linha["geracao_solar"]),
                int(linha["geracao_eolica"]),
                int(linha["consumo"]),
                int(linha["reserva_pct"]),
                int(linha["temp_externa"]),
                linha["radiacao"],              
                int(linha["qualidade_com"]),
            ]
            matriz.append(leitura)
    return horarios, matriz
def coluna(matriz, indice):
    """Devolve uma LISTA com todos os valores de uma coluna da matriz.
    Ex.: coluna(matriz, COL_RESERVA) -> [85, 78, 70, 58, 44, 32]
    """
    valores = []
    for linha in matriz:
        valores.append(linha[indice])
    return valores

MODULOS = {
    "suporte_vida":  1,
    "energia":       1,
    "comunicacao":   1,   
    "habitat":       1,
    "laboratorio":   1,
    "armazenamento": 0,   
}
HIERARQUIA = {
    "energia": ["solar", "eolica", "baterias"],
    "habitat": ["oxigenio", "temperatura", "comunicacao"],
}

LOG_EVENTOS = [
    ("00:10", "Inicializacao dos sistemas concluida"),
    ("03:45", "Modo de economia de energia ativado"),
    ("07:20", "Reinicializacao do sensor de radiacao"),
    ("09:05", "Alerta: reserva de energia abaixo de 75 por cento"),
    ("12:30", "Mudanca de prioridade: habitat acima do laboratorio"),
    ("15:10", "Falha detectada no modulo de armazenamento"),
    ("16:40", "Alerta: qualidade de comunicacao em queda"),
    ("19:55", "Alerta critico: reserva de energia abaixo de 35 por cento"),
]


def classificar_modulo(nome, estado, qual_com_atual):
   
    if estado == 0:
        return "CRITICO"                      
    if nome == "comunicacao" and qual_com_atual < 30:
        return "ALERTA"
    return "NORMAL"


def tabela_status(modulos, qual_com_atual):
    """Imprime uma tabela simples com o status de cada modulo."""
    print("MODULO          | BINARIO | STATUS")
    print("-" * 40)
    for nome, estado in modulos.items():
        status = classificar_modulo(nome, estado, qual_com_atual)
        print("%-15s |    %d    | %s" % (nome, estado, status))
    print("-" * 40)


def detectar_inconsistencias(modulos, qual_com_atual):
  
    inconsistencias = []
    if modulos["comunicacao"] == 1 and qual_com_atual < 30:
        inconsistencias.append(
            "Modulo de comunicacao marcado como OK (binario = 1), mas a "
            "qualidade do sinal esta em %d%% (abaixo do minimo seguro)."
            % qual_com_atual
        )
    return inconsistencias


def diagnosticar(reserva_atual, radiacao_atual, qual_com_atual, modulos):
   
    suporte = modulos["suporte_vida"]
    energia = modulos["energia"]
    situacao_critica = (reserva_atual < 35) or (suporte == 0) or (energia == 0)
    situacao_alerta = (
        (35 <= reserva_atual < 60)
        or (radiacao_atual == "alta")
        or (qual_com_atual < 30)
    )
    if situacao_critica:
        return "CRITICO"
    elif situacao_alerta:
        return "ALERTA"
    else:
        return "NORMAL"
def comunicacao_esta_ok(modulos, qual_com_atual):
 
    return (modulos["comunicacao"] == 1) and (qual_com_atual >= 30)
def gerar_alertas(matriz, modulos):
   
    fila_alertas = []
    reserva_atual = coluna(matriz, COL_RESERVA)[-1]   
    qual_atual    = coluna(matriz, COL_QUALCOM)[-1]
    radiacao_atual = coluna(matriz, COL_RADIACAO)[-1]

    for nome, estado in modulos.items():
        if estado == 0:
            fila_alertas.append({
                "severidade": "CRITICO",
                "mensagem": "Modulo '%s' fora de operacao (binario = 0)." % nome,
                "acao": "Acionar manutencao e isolar o modulo afetado.",
            })

    if reserva_atual < 35:
        fila_alertas.append({
            "severidade": "CRITICO",
            "mensagem": "Reserva de energia em %d%% (nivel critico)." % reserva_atual,
            "acao": "Cortar consumo nao essencial imediatamente.",
        })
    elif reserva_atual < 60:
        fila_alertas.append({
            "severidade": "ALERTA",
            "mensagem": "Reserva de energia em %d%% (atencao)." % reserva_atual,
            "acao": "Reduzir consumo e priorizar recarga.",
        })

    if qual_atual < 30:
        fila_alertas.append({
            "severidade": "ALERTA",
            "mensagem": "Qualidade de comunicacao em %d%% (sinal fraco)." % qual_atual,
            "acao": "Reorientar antena ou usar canal de emergencia.",
        })

    if radiacao_atual == "alta":
        fila_alertas.append({
            "severidade": "ALERTA",
            "mensagem": "Nivel de radiacao externo ALTO.",
            "acao": "Manter tripulacao em area protegida.",
        })

    return fila_alertas


def prioridade_do_alerta(alerta):
    return PRIORIDADE[alerta["severidade"]]


def mostrar_alertas(fila_alertas):
    if not fila_alertas:
        print("Nenhum alerta. Operacao normal.")
        return
    ordenados = sorted(fila_alertas, key=prioridade_do_alerta)
    for alerta in ordenados:
        print("[%s] %s" % (alerta["severidade"], alerta["mensagem"]))
        print("       -> Acao: %s" % alerta["acao"])


def montar_pilha_eventos(log_eventos):
    
    pilha = []
    for horario, descricao in log_eventos:
        if ("Alerta" in descricao) or ("Falha" in descricao):
            pilha.append((horario, descricao))   
    return pilha


def mostrar_ultimos_eventos(pilha, quantidade):
    print("Ultimos eventos criticos (mais recente primeiro):")
    copia = list(pilha)               
    contador = 0
    while copia and contador < quantidade:
        horario, descricao = copia.pop()  
        print("   - %s -> %s" % (horario, descricao))
        contador += 1



def regressao_linear(x, y):
 
    n = len(x)
    soma_x = sum(x)
    soma_y = sum(y)
    soma_xy = 0
    soma_xx = 0
    for i in range(n):
        soma_xy += x[i] * y[i]
        soma_xx += x[i] * x[i]
    a = (n * soma_xy - soma_x * soma_y) / (n * soma_xx - soma_x * soma_x)
    b = (soma_y - a * soma_x) / n
    return a, b


def prever_proxima_reserva(reservas):
  
    x = list(range(len(reservas)))        
    a, b = regressao_linear(x, reservas)
    proximo_x = len(reservas)            
    previsto = a * proximo_x + b
    return a, b, previsto



def gerar_recomendacoes(diagnostico, reserva_prevista, comunicacao_ok):

    recomendacoes = []

    if diagnostico == "CRITICO":
        recomendacoes.append(("CRITICA", "Manter suporte a vida e comunicacao de emergencia."))
        recomendacoes.append(("ALTA", "Desligar laboratorio e sistemas nao essenciais."))

    if reserva_prevista < 25:
        recomendacoes.append(("ALTA",
            "Previsao indica reserva de %.1f%% no proximo ciclo. "
            "Redirecionar energia para habitat e recarga de baterias."
            % reserva_prevista))

    if not comunicacao_ok:
        recomendacoes.append(("MEDIA", "Ativar canal de comunicacao redundante."))

    if not recomendacoes:
        recomendacoes.append(("BAIXA", "Operacao normal. Manter monitoramento de rotina."))

    return recomendacoes

def main():
   

    horarios, matriz = ler_telemetria(r"C:\Users\Igor\Downloads\Global Solutions\dados.csv")

    reservas = coluna(matriz, COL_RESERVA)
    qualcom  = coluna(matriz, COL_QUALCOM)
    radiacoes = coluna(matriz, COL_RADIACAO)

    reserva_atual = reservas[-1]
    qual_atual    = qualcom[-1]
    radiacao_atual = radiacoes[-1]

    print("=" * 60)
    print("  ESTACAO ARES-1 - PAINEL DE MONITORAMENTO")
    print("=" * 60)

    print("\n[ LEITURAS POR HORARIO ]")
    print("Horario | Solar Eolica Consumo Reserva Temp Radiacao QualCom")
    for i in range(len(horarios)):
        ln = matriz[i]
        print(" %s  |  %3d   %3d    %3d     %3d%%  %4d  %-7s %3d%%" % (
            horarios[i], ln[COL_SOLAR], ln[COL_EOLICA], ln[COL_CONSUMO],
            ln[COL_RESERVA], ln[COL_TEMP], ln[COL_RADIACAO], ln[COL_QUALCOM]))

    print("\n[ STATUS DOS MODULOS ]")
    tabela_status(MODULOS, qual_atual)

    print("\n[ HIERARQUIA DA MISSAO ]")
    for sistema, partes in HIERARQUIA.items():
        print(" %s: %s" % (sistema, ", ".join(partes)))

    print("\n[ VERIFICACAO DE INCONSISTENCIAS ]")
    inconsistencias = detectar_inconsistencias(MODULOS, qual_atual)
    if inconsistencias:
        for item in inconsistencias:
            print(" (!) " + item)
    else:
        print(" Nenhuma inconsistencia detectada.")

    diagnostico = diagnosticar(reserva_atual, radiacao_atual, qual_atual, MODULOS)
    print("\n[ DIAGNOSTICO GERAL ]")
    print(" Situacao da missao: %s" % diagnostico)

    print("\n[ ALERTAS ATIVOS (priorizados) ]")
    fila = gerar_alertas(matriz, MODULOS)
    mostrar_alertas(fila)

    print("\n[ HISTORICO (pilha de eventos criticos) ]")
    pilha = montar_pilha_eventos(LOG_EVENTOS)
    mostrar_ultimos_eventos(pilha, 3)

    print("\n[ PREVISAO DE ENERGIA (regressao linear) ]")
    a, b, previsto = prever_proxima_reserva(reservas)
    print(" Reservas medidas: %s" % reservas)
    print(" Reta ajustada: reserva = %.2f * x + %.2f" % (a, b))
    print(" Tendencia: %.2f%% por ciclo (queda)." % a)
    print(" Reserva prevista no proximo ciclo: %.1f%%" % previsto)

    print("\n[ RECOMENDACOES ]")
    com_ok = comunicacao_esta_ok(MODULOS, qual_atual)
    recomendacoes = gerar_recomendacoes(diagnostico, previsto, com_ok)
    for nivel, texto in recomendacoes:
        print(" (%s) %s" % (nivel, texto))

    print("\n")

main()
