"""Trie adaptada da busca existente, agora alimentada pelos registros do SCIC."""
import unicodedata


def normalizar(texto):
    decomposto = unicodedata.normalize('NFD', texto.strip())
    return ''.join(caractere for caractere in decomposto if not unicodedata.combining(caractere)).casefold()


class No:
    def __init__(self):
        self.filhos = {}
        self.registros = []


class Trie:
    def __init__(self):
        self.raiz = No()

    def inserir(self, registro):
        chave = normalizar(registro['termo'])
        if not chave:
            raise ValueError('O termo não pode ser vazio.')
        no = self.raiz
        for caractere in chave:
            no = no.filhos.setdefault(caractere, No())
        no.registros.append(registro)

    def buscar_prefixo(self, prefixo, limite=20):
        chave = normalizar(prefixo)
        if not chave or limite <= 0:
            return []
        no = self.raiz
        for caractere in chave:
            no = no.filhos.get(caractere)
            if no is None:
                return []
        # Visita apenas a subárvore do prefixo, preservando a grafia de apresentação.
        pilha, resultados = [no], []
        while pilha and len(resultados) < limite:
            atual = pilha.pop()
            resultados.extend(atual.registros[:limite - len(resultados)])
            for caractere in sorted(atual.filhos, reverse=True):
                pilha.append(atual.filhos[caractere])
        return resultados


def construir_indice(df):
    trie = Trie()
    for coluna, tipo in [('nome_modulo', 'modulo'), ('codigo_sensor', 'sensor'),
                         ('tipo_modulo', 'tipo'), ('mensagem_alerta', 'alerta')]:
        for termo, grupo in df.groupby(coluna, sort=True):
            if isinstance(termo, str) and termo.strip():
                trie.inserir({'termo': termo, 'tipo': tipo,
                              'ids': sorted(grupo['id_registro'].astype(int).tolist())})
    return trie
