# SIFSM – Sistema em Python e CRUD

```
O banco `aurora_siger.db` é criado automaticamente com dados de exemplo.
```

## Arquivos

| Arquivo         | Função                                                                            |
| --------------- | --------------------------------------------------------------------------------- |
| `main.py`       | Menu interativo, entrada de dados e tratamento de erros                           |
| `crud.py`       | Cadastrar, listar, alterar e excluir (genérico para todas as tabelas) e validação |
| `banco.py`      | Conexão, criação das tabelas e dados de exemplo                                   |
| `integracao.py` | Pontos de integração das Partes 2, 3 e 4 e exportação de CSV                      |

## Tabelas

`modulos`, `sensores`, `leituras`, `alertas`, `manutencoes` (relacionadas por chaves estrangeiras com `ON DELETE CASCADE`).

## Tratamento de erros

- `try/except/else` em validação de entradas, `IntegrityError` (código duplicado) e chaves inexistentes.
- `finally` garante o fechamento da conexão.

## Limitações

Sem login, sem interface gráfica; ids digitados manualmente; dados simulados.
