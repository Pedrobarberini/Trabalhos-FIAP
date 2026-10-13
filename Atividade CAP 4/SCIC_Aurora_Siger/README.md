# SCIC - Sistema de Comunicação Interplanetária da Colônia Aurora Siger

Protótipo em Python da Atividade CAP 4. Integra a base simulada e a análise numérica existentes à previsão com avaliação temporal, ao atendimento de alertas com heap e à consulta por trie. Não usa sensores físicos, APIs externas ou serviços web.

## Execução

Use Python 3.12. Após extrair o ZIP, entre na pasta `SCIC_Aurora_Siger` e execute:

```bash
python -m venv .venv
```

Ative o ambiente no Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Windows, se preferir executar diretamente sem ativação:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe codigo_fonte.py --demo
.\.venv\Scripts\python.exe codigo_fonte.py
```

No Linux/macOS, ative com `source .venv/bin/activate`. Com o ambiente ativo, em qualquer sistema:

```bash
python -m pip install -r requirements.txt
python codigo_fonte.py --demo
python codigo_fonte.py
```

O CSV necessário já está incluído. `--demo` executa todas as funcionalidades, exporta a análise e termina. Sem essa opção, o sistema abre o menu. Os caminhos padrão são relativos à localização do código, permitindo iniciar o programa de outra pasta. `--dados` e `--saida` aceitam caminhos personalizados:

```bash
python codigo_fonte.py --dados dados_aurora_siger.csv --saida analise_local --demo
```

Os gráficos são salvos em PNG, sem exigir janela gráfica ou navegador. Não há treinamento remoto nem downloads de modelos durante a execução.

## Arquivos da entrega

| Arquivo/pasta | Função |
|---|---|
| `codigo_fonte.py` | Entrada principal: menu, consulta e demonstração completa |
| `dados_aurora_siger.csv` | Base distribuída: 154 linhas simuladas, 15 módulos e dez ciclos |
| `configuracao.py` | Caminhos, campos e limites da simulação |
| `gerar_base.py` | Geração reproduzível dos perfis originais, com semente 42 |
| `carregar_dados.py` | Limpeza auditável, validação e filtros |
| `analise_numerica.py` | Indicadores, erros, precisão e coerência da potência |
| `modelo_previsao.py` | Regressão linear, comparação com referência, treino/validação/teste temporal |
| `alertas_heap.py` | Min-heap com heapify-up e heapify-down explícitos |
| `busca_trie.py` | Índice por prefixo conectado aos registros reais do CSV |
| `dispositivos.py` | Conversão de bases e cálculos elétricos da leitura |
| `gerar_graficos.py` | Gráficos de latência e previsão nos ciclos de teste |
| `relatorio.py` | Geração do relatório técnico a partir dos resultados calculados |
| `relatorio_tecnico.md` | Relatório completo da execução distribuída |
| `resultados/` | CSVs analisados, leituras rejeitadas, métricas JSON e exemplo de execução |
| `graficos_ou_imagens/` | Três gráficos produzidos pela execução |
| `testes/` | Testes de cálculo, estruturas, qualidade e separação temporal |
| `requirements.txt` | Versões das quatro bibliotecas utilizadas |
| `link_video.txt` | Etapa de publicação do vídeo, ainda pendente |

## Menu e exemplos

1. **Resumo:** mostra 154 linhas de origem, quatro reenvios removidos, seis leituras rejeitadas e 144 leituras válidas.
2. **Consulta:** filtre por `Antena`, status `alerta` e prioridade `1`; Enter permite deixar filtros em aberto.
3. **Indicadores:** erro absoluto em ms, erro relativo em %, média, mediana, máximo, p95 e ponto flutuante.
4. **Modelo:** exibe MAE, MSE, RMSE e R² na validação e teste; estima o próximo ciclo.
5. **Heap:** mostra os mais urgentes e o vetor interno da fila, que não é uma lista inteiramente ordenada.
6. **Trie:** experimente `com`, `enf` ou `SNS-0x1A0`; depois informe um ID listado para abrir a leitura.
7. **Dispositivos:** mostra conversão decimal/binário/hexadecimal, P=VxI e R=V/I com uma leitura da Antena Central Aurora.
8. **Atendimento:** retira a raiz do heap em memória. Recarregar a base restaura a fila histórica.
9. **Análise final:** gera relatório, CSVs, JSON e gráficos usando a base completa, sem ocultar alertas retirados durante a exploração.
10. **Carga:** permite abrir outro CSV com o mesmo esquema; um arquivo inválido não substitui a sessão anterior.
0. **Saída.** Entradas inválidas exibem mensagens sem encerrar o menu.

## Dependências

- NumPy: simulação com semente e cálculos vetorizados.
- Pandas: leitura, limpeza, consultas e agregações do CSV.
- Matplotlib: gráficos das leituras e das previsões de teste.
- scikit-learn: regressão linear e métricas de regressão.

As demais importações diretas pertencem à biblioteca padrão do Python, como `argparse`, `json`, `math`, `pathlib`, `dataclasses`, `unicodedata` e `unittest`. Dependências indiretas dessas quatro bibliotecas são instaladas automaticamente pelo pip. Nenhuma biblioteca adicional de aplicação é exigida.

## Modelo e limites

A regressão usa somente referência nominal e número do ciclo para estimar a observação. Os ciclos C001-C006 são treino, C007-C008 validação e C009-C010 teste. A escolha entre regressão e referência usa o RMSE de validação; o teste não participa do ajuste nem da escolha. As métricas e a interpretação efetivamente obtidas estão no relatório e em `resultados/resumo_execucao.json`.

O erro relativo usa a observação como denominador. Limites de 5% e 15% são regras da simulação, não padrões universais. Dados faltantes são excluídos dos cálculos e preservados em arquivo com motivo e na fila como falhas de telemetria. As latências em ms representam a rede local/relés da colônia, não propagação Terra-Marte. Potência elétrica não é potência de rádio irradiada; a base não informa duração para calcular energia em Wh.

## Testes e reprodução da base

```bash
python -m unittest discover -s testes -v
```

Para criar uma nova cópia da base, sem sobrescrever automaticamente a distribuída:

```bash
python gerar_base.py --saida dados_regerados.csv
```

Não é necessário regenerar a base para executar o sistema. A importação de módulos não gera arquivos nem inicia menus.

## Vídeo

A gravação e publicação serão feitas pelo aluno responsável. Após publicar o vídeo de até cinco minutos no YouTube como **Não listado**, substitua o conteúdo de `link_video.txt` pela URL real e atualize esse arquivo dentro do ZIP antes da submissão. A execução e os arquivos técnicos já podem ser avaliados; o requisito do vídeo depende dessa etapa externa.
