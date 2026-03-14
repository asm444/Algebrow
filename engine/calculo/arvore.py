"""AST para expressoes simbolicas compostas."""

import math


class NoExpressao:
    """No da arvore de expressao simbolica."""

    def __init__(self, tipo: str, valor: str = '', filhos: list = None):
        """
        tipo: 'numero', 'variavel', 'operacao', 'funcao'
        valor: o valor/simbolo (ex: '+', 'sin', '3', 'x')
        filhos: lista de NoExpressao
        """
        self.tipo = tipo
        self.valor = valor
        self.filhos = filhos if filhos is not None else []

    def representacao_latex(self) -> str:
        """Retorna representacao LaTeX da expressao."""
        if self.tipo == 'numero':
            return self.valor
        if self.tipo == 'variavel':
            return self.valor
        if self.tipo == 'operacao':
            if self.valor == '+':
                return f'{self.filhos[0].representacao_latex()} + {self.filhos[1].representacao_latex()}'
            if self.valor == '-':
                return f'{self.filhos[0].representacao_latex()} - {self.filhos[1].representacao_latex()}'
            if self.valor == '*':
                esq = self.filhos[0].representacao_latex()
                dir_ = self.filhos[1].representacao_latex()
                return f'{esq} \\cdot {dir_}'
            if self.valor == '/':
                num = self.filhos[0].representacao_latex()
                den = self.filhos[1].representacao_latex()
                return f'\\frac{{{num}}}{{{den}}}'
            if self.valor == '^':
                base = self.filhos[0].representacao_latex()
                exp = self.filhos[1].representacao_latex()
                return f'{{{base}}}^{{{exp}}}'
        if self.tipo == 'funcao':
            arg = self.filhos[0].representacao_latex() if self.filhos else ''
            nomes_latex = {
                'sin': '\\sin',
                'cos': '\\cos',
                'tan': '\\tan',
                'arcsin': '\\arcsin',
                'arccos': '\\arccos',
                'arctan': '\\arctan',
                'ln': '\\ln',
                'exp': 'e',
                'abs': '\\left|',
                'sqrt': '\\sqrt',
            }
            if self.valor == 'exp':
                return f'e^{{{arg}}}'
            if self.valor == 'abs':
                return f'\\left|{arg}\\right|'
            if self.valor == 'sqrt':
                return f'\\sqrt{{{arg}}}'
            nome = nomes_latex.get(self.valor, f'\\operatorname{{{self.valor}}}')
            return f'{nome}\\left({arg}\\right)'
        return self.valor

    def avaliar(self, variaveis: dict) -> float:
        """Avalia a expressao numericamente dado um dicionario de variaveis."""
        if self.tipo == 'numero':
            return float(self.valor)
        if self.tipo == 'variavel':
            if self.valor in variaveis:
                return float(variaveis[self.valor])
            raise ValueError(f"Variavel '{self.valor}' nao definida")
        if self.tipo == 'operacao':
            esq = self.filhos[0].avaliar(variaveis)
            dir_ = self.filhos[1].avaliar(variaveis)
            if self.valor == '+':
                return esq + dir_
            if self.valor == '-':
                return esq - dir_
            if self.valor == '*':
                return esq * dir_
            if self.valor == '/':
                return esq / dir_
            if self.valor == '^':
                return esq ** dir_
        if self.tipo == 'funcao':
            arg = self.filhos[0].avaliar(variaveis)
            funcoes = {
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'arcsin': math.asin,
                'arccos': math.acos,
                'arctan': math.atan,
                'ln': math.log,
                'exp': math.exp,
                'abs': abs,
                'sqrt': math.sqrt,
            }
            if self.valor in funcoes:
                return funcoes[self.valor](arg)
            raise ValueError(f"Funcao '{self.valor}' nao reconhecida")
        raise ValueError(f"Tipo de no desconhecido: {self.tipo}")

    def __eq__(self, other):
        if not isinstance(other, NoExpressao):
            return False
        return (self.tipo == other.tipo
                and self.valor == other.valor
                and self.filhos == other.filhos)

    def __repr__(self):
        if self.filhos:
            return f"NoExpressao({self.tipo!r}, {self.valor!r}, {self.filhos!r})"
        return f"NoExpressao({self.tipo!r}, {self.valor!r})"


# --- Helpers para construcao rapida ---

def num(v) -> NoExpressao:
    """Cria no numerico."""
    return NoExpressao('numero', str(v))

def var(nome: str) -> NoExpressao:
    """Cria no variavel."""
    return NoExpressao('variavel', nome)

def op(operador: str, esq: NoExpressao, dir_: NoExpressao) -> NoExpressao:
    """Cria no operacao."""
    return NoExpressao('operacao', operador, [esq, dir_])

def func(nome: str, arg: NoExpressao) -> NoExpressao:
    """Cria no funcao."""
    return NoExpressao('funcao', nome, [arg])
