


from os import name


name: str = input("Coloque o tipo de potência que deseja calcular \ndigite 1 para Calcular potencia aparente \ndigite 2 para Calcular fator de potência \ndigite 3 para Calcular potência reativa \ndigite 4 para Calcular Armazenamento em Baterias \ndigite x para sair:\n ")


if name == "1":

    v = float(input("Coloque o valor da tensão: "))
    i = float(input("Coloque o valor da corrente: "))
    S = v * i

    print("A potência aparente é: ", S, "VA")


if name == "2":
    P = float(input("Coloque o valor do fator de potência: "))
    S = float(input("Coloque o valor da potência aparente: "))

    Fp = P / S

    print("O fator de potência é: ", Fp)

if name == "3":

    i = float(input("Coloque o valor da corrente elétrica: "))
    t = float(input("Coloque o valor da potência tempo: "))

    Q = i * t
    print("A potência reativa é: ", Q, "mAh")

if name == "4":
    v = float(input("Coloque o valor de vats: "))
    Ah = float(input("Coloque o valor da corrente elétrica: "))
    
    Wh = v * Ah


    print("O armazenamento da bateria é: ", Wh, "kWh")

elif name == "x":
    print("Saindo do programa...")