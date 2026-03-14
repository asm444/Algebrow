"""Grupos finitos e suas propriedades."""
from itertools import permutations
from engine.basic.passo import Passo, Historico


class Grupo:
    """Grupo finito definido por tabela de Cayley ou geradores."""

    def __init__(self, elementos: list, operacao=None, tabela_cayley: dict = None):
        """
        elementos: lista de elementos do grupo
        operacao: callable(a, b) -> c (operacao do grupo)
        tabela_cayley: dict[(a,b)] -> c alternativo
        """
        self.elementos = list(elementos)
        self._operacao = operacao
        self._tabela = tabela_cayley or {}

        # Se temos operacao mas nao tabela, construir tabela
        if operacao and not tabela_cayley:
            for a in self.elementos:
                for b in self.elementos:
                    self._tabela[(a, b)] = operacao(a, b)

    def operar(self, a, b):
        """Aplica a operacao do grupo."""
        if (a, b) in self._tabela:
            return self._tabela[(a, b)]
        if self._operacao:
            return self._operacao(a, b)
        raise ValueError(f"Operacao nao definida para ({a}, {b})")

    def identidade(self):
        """Encontra o elemento identidade do grupo."""
        for e in self.elementos:
            eh_identidade = True
            for g in self.elementos:
                if self.operar(e, g) != g or self.operar(g, e) != g:
                    eh_identidade = False
                    break
            if eh_identidade:
                return e
        raise ValueError("Grupo nao possui identidade")

    def inverso(self, elemento):
        """Encontra o inverso de um elemento."""
        e = self.identidade()
        for g in self.elementos:
            if self.operar(elemento, g) == e and self.operar(g, elemento) == e:
                return g
        raise ValueError(f"Elemento {elemento} nao possui inverso")

    def ordem(self) -> int:
        """Ordem do grupo (numero de elementos)."""
        return len(self.elementos)

    def ordem_elemento(self, elemento) -> int:
        """Ordem de um elemento: menor n tal que g^n = e."""
        e = self.identidade()
        atual = elemento
        for n in range(1, self.ordem() + 1):
            if atual == e:
                return n
            atual = self.operar(atual, elemento)
        raise ValueError(f"Elemento {elemento} nao possui ordem finita neste grupo")

    def eh_abeliano(self) -> bool:
        """Verifica se o grupo eh abeliano (comutativo)."""
        for a in self.elementos:
            for b in self.elementos:
                if self.operar(a, b) != self.operar(b, a):
                    return False
        return True

    def _eh_subgrupo(self, subset):
        """Verifica se um subconjunto eh subgrupo."""
        subset_set = set(subset)
        # Fechamento
        for a in subset:
            for b in subset:
                if self.operar(a, b) not in subset_set:
                    return False
        # Identidade
        e = self.identidade()
        if e not in subset_set:
            return False
        # Inversos
        for a in subset:
            if self.inverso(a) not in subset_set:
                return False
        return True

    def subgrupos(self) -> list:
        """Encontra todos os subgrupos do grupo."""
        n = self.ordem()
        elementos = self.elementos
        resultado = []
        # Gerar todos subconjuntos (para grupos pequenos)
        for i in range(1, 2 ** n):
            subset = []
            for j in range(n):
                if i & (1 << j):
                    subset.append(elementos[j])
            if self._eh_subgrupo(subset):
                resultado.append(sorted(subset, key=lambda x: str(x)))
        return resultado

    def classes_conjugacao(self) -> list:
        """Encontra as classes de conjugacao do grupo."""
        visitados = set()
        classes = []
        for g in self.elementos:
            if g in visitados:
                continue
            classe = set()
            for h in self.elementos:
                # h g h^{-1}
                h_inv = self.inverso(h)
                conjugado = self.operar(self.operar(h, g), h_inv)
                classe.add(conjugado)
            visitados.update(classe)
            classes.append(sorted(classe, key=lambda x: str(x)))
        return classes

    def centro(self) -> list:
        """Encontra o centro do grupo Z(G) = {g : gx = xg para todo x}."""
        resultado = []
        for g in self.elementos:
            comuta = True
            for x in self.elementos:
                if self.operar(g, x) != self.operar(x, g):
                    comuta = False
                    break
            if comuta:
                resultado.append(g)
        return resultado

    def tabela_cayley_latex(self) -> str:
        """Retorna representacao LaTeX da tabela de Cayley."""
        n = self.ordem()
        elems = self.elementos
        header = " & ".join(str(e) for e in elems)
        linhas = [f"\\cdot & {header} \\\\ \\hline"]
        for a in elems:
            vals = " & ".join(str(self.operar(a, b)) for b in elems)
            linhas.append(f"{a} & {vals} \\\\")
        corpo = "\n".join(linhas)
        cols = "c|" + "c" * n
        return f"\\begin{{array}}{{{cols}}}\n{corpo}\n\\end{{array}}"


# ---------------------------------------------------------------------------
# Grupos classicos pre-definidos
# ---------------------------------------------------------------------------

def grupo_ciclico(n: int) -> Grupo:
    """Z_n = {0, 1, ..., n-1} com adicao mod n."""
    elementos = list(range(n))
    operacao = lambda a, b: (a + b) % n
    return Grupo(elementos, operacao=operacao)


def _compor_perm(p1: tuple, p2: tuple) -> tuple:
    """Composicao de permutacoes: (p1 o p2)(i) = p1(p2(i))."""
    return tuple(p1[p2[i]] for i in range(len(p1)))


def grupo_simetrico(n: int) -> Grupo:
    """S_n -- grupo de permutacoes. Para n<=4."""
    if n > 4:
        raise ValueError("S_n suportado apenas para n <= 4")
    elementos = list(permutations(range(n)))
    operacao = lambda a, b: _compor_perm(a, b)
    return Grupo(elementos, operacao=operacao)


def grupo_diedral(n: int) -> Grupo:
    """D_n -- simetrias do n-gono regular. Ordem 2n."""
    # Elementos: (k, s) onde k = rotacao por k*(2pi/n), s = 0 ou 1 (reflexao)
    # Operacao: (k1, s1) * (k2, s2):
    #   se s1 == 0: (k1 + k2, s2) mod n
    #   se s1 == 1: (k1 - k2, 1 - s2) mod n  -- reflexao inverte rotacao
    elementos = []
    for k in range(n):
        elementos.append((k, 0))
    for k in range(n):
        elementos.append((k, 1))

    def operacao(a, b):
        k1, s1 = a
        k2, s2 = b
        if s1 == 0:
            return ((k1 + k2) % n, s2)
        else:
            return ((k1 - k2) % n, (s2 + 1) % 2)

    return Grupo(elementos, operacao=operacao)


def grupo_klein() -> Grupo:
    """Grupo de Klein V4 = Z_2 x Z_2."""
    elementos = [(0, 0), (0, 1), (1, 0), (1, 1)]

    def operacao(a, b):
        return ((a[0] + b[0]) % 2, (a[1] + b[1]) % 2)

    return Grupo(elementos, operacao=operacao)
