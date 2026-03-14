"""Módulo de matrizes com aritmética exata via strings."""

from engine.basic.operacoes_basicas import soma, diff, multi, reduz_fracao


class Matriz:
    """Matriz com coeficientes como strings para aritmética exata.
    Representação interna: list[list[str]]
    """

    def __init__(self, dados: list[list[str]]):
        self.dados = dados
        self.linhas = len(dados)
        self.colunas = len(dados[0]) if dados else 0

    def elemento(self, i: int, j: int) -> str:
        """Retorna o elemento na posição (i, j) (indexação começando em 0)."""
        return self.dados[i][j]

    def transposta(self) -> 'Matriz':
        """Retorna a matriz transposta."""
        novos_dados = []
        for j in range(self.colunas):
            linha = []
            for i in range(self.linhas):
                linha.append(self.dados[i][j])
            novos_dados.append(linha)
        return Matriz(novos_dados)

    def somar(self, outra: 'Matriz') -> 'Matriz':
        """Soma duas matrizes de mesmas dimensões."""
        if self.linhas != outra.linhas or self.colunas != outra.colunas:
            raise ValueError(
                f"Dimensões incompatíveis para soma: "
                f"{self.linhas}x{self.colunas} e {outra.linhas}x{outra.colunas}"
            )
        novos_dados = []
        for i in range(self.linhas):
            linha = []
            for j in range(self.colunas):
                linha.append(soma(self.dados[i][j], outra.dados[i][j]))
            novos_dados.append(linha)
        return Matriz(novos_dados)

    def subtrair(self, outra: 'Matriz') -> 'Matriz':
        """Subtrai outra matriz desta."""
        if self.linhas != outra.linhas or self.colunas != outra.colunas:
            raise ValueError(
                f"Dimensões incompatíveis para subtração: "
                f"{self.linhas}x{self.colunas} e {outra.linhas}x{outra.colunas}"
            )
        novos_dados = []
        for i in range(self.linhas):
            linha = []
            for j in range(self.colunas):
                linha.append(diff(self.dados[i][j], outra.dados[i][j]))
            novos_dados.append(linha)
        return Matriz(novos_dados)

    def multiplicar_escalar(self, escalar: str) -> 'Matriz':
        """Multiplica a matriz por um escalar."""
        novos_dados = []
        for i in range(self.linhas):
            linha = []
            for j in range(self.colunas):
                linha.append(multi(escalar, self.dados[i][j]))
            novos_dados.append(linha)
        return Matriz(novos_dados)

    def multiplicar(self, outra: 'Matriz') -> 'Matriz':
        """Multiplica esta matriz pela outra (self * outra)."""
        if self.colunas != outra.linhas:
            raise ValueError(
                f"Dimensões incompatíveis para multiplicação: "
                f"{self.linhas}x{self.colunas} e {outra.linhas}x{outra.colunas}"
            )
        novos_dados = []
        for i in range(self.linhas):
            linha = []
            for j in range(outra.colunas):
                acumulador = '0'
                for k in range(self.colunas):
                    produto = multi(self.dados[i][k], outra.dados[k][j])
                    acumulador = soma(acumulador, produto)
                linha.append(acumulador)
            novos_dados.append(linha)
        return Matriz(novos_dados)

    def representacao_latex(self) -> str:
        """Retorna representação LaTeX da matriz usando pmatrix."""
        linhas_latex = []
        for i in range(self.linhas):
            elementos = []
            for j in range(self.colunas):
                val = self.dados[i][j]
                if '/' in val:
                    num, den = val.split('/')
                    elementos.append(f'\\frac{{{num}}}{{{den}}}')
                else:
                    elementos.append(val)
            linhas_latex.append(' & '.join(elementos))
        corpo = ' \\\\ '.join(linhas_latex)
        return f'\\begin{{pmatrix}} {corpo} \\end{{pmatrix}}'

    def __eq__(self, other) -> bool:
        if not isinstance(other, Matriz):
            return False
        if self.linhas != other.linhas or self.colunas != other.colunas:
            return False
        for i in range(self.linhas):
            for j in range(self.colunas):
                if self.dados[i][j] != other.dados[i][j]:
                    return False
        return True

    def __repr__(self):
        return f"Matriz({self.dados})"
