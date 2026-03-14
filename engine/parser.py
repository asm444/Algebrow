"""Parser descendente recursivo para expressões matemáticas.

Gramática:
    expressao := termo (('+' | '-') termo)*
    termo     := fator (('*' | '/') fator)*
    fator     := atomo ('^' fator)?
    atomo     := numero | fracao | 'sqrt' '(' expr ')' | 'sqrt' indice '(' expr ')'
               | 'log_' base '(' expr ')' | 'log' '(' expr ')'
               | '(' expressao ')' | '-' fator

Exemplos de entrada:
    "3 + 4"         → soma(Racional('3'), Racional('4'))
    "sqrt(216)"     → Raiz('2', '216')
    "2^3"           → Exponencial('2', '3')
    "log_3(9)"      → Logaritmo('3', '9')
    "3/4 + sqrt(2)" → soma(Racional('3/4'), Raiz('2', '2'))
"""

from engine.basic.numeros import Racional, Raiz, Exponencial, Logaritmo
from engine.basic.expressao import soma, subtracao, multiplicacao, Expressao


class TokenizadorError(Exception):
    pass


class ParserError(Exception):
    pass


# ============================================================
# Tokenizador
# ============================================================

def tokenizar(texto):
    """Converte texto em lista de tokens."""
    tokens = []
    i = 0
    texto = texto.replace(' ', '')

    while i < len(texto):
        c = texto[i]

        # Números (inteiros e decimais)
        if c.isdigit() or (c == '.' and i + 1 < len(texto) and texto[i + 1].isdigit()):
            inicio = i
            while i < len(texto) and (texto[i].isdigit() or texto[i] == '.'):
                i += 1
            tokens.append(('NUM', texto[inicio:i]))
            continue

        # Palavras-chave: sqrt, log
        if c.isalpha():
            inicio = i
            while i < len(texto) and texto[i].isalpha():
                i += 1
            palavra = texto[inicio:i]
            if palavra == 'sqrt':
                tokens.append(('SQRT', 'sqrt'))
            elif palavra == 'log':
                tokens.append(('LOG', 'log'))
            else:
                raise TokenizadorError(f"Identificador desconhecido: '{palavra}'")
            continue

        # Operadores e símbolos
        if c in '+-*/^()_':
            tokens.append((c, c))
            i += 1
            continue

        raise TokenizadorError(f"Caractere inesperado: '{c}' na posição {i}")

    tokens.append(('EOF', ''))
    return tokens


# ============================================================
# Parser
# ============================================================

class Parser:
    """Parser descendente recursivo para expressões matemáticas."""

    MAX_PROFUNDIDADE = 50

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self._profundidade = 0

    def _entrar(self):
        self._profundidade += 1
        if self._profundidade > self.MAX_PROFUNDIDADE:
            raise ParserError("Expressão excede a profundidade máxima permitida (50 níveis)")

    def _sair(self):
        self._profundidade -= 1

    def peek(self):
        return self.tokens[self.pos]

    def consume(self, tipo_esperado=None):
        token = self.tokens[self.pos]
        if tipo_esperado and token[0] != tipo_esperado:
            raise ParserError(f"Esperado '{tipo_esperado}', encontrado '{token[0]}' ('{token[1]}')")
        self.pos += 1
        return token

    def parse(self):
        resultado = self.expressao()
        if self.peek()[0] != 'EOF':
            raise ParserError(f"Tokens não consumidos a partir de '{self.peek()[1]}'")
        return resultado

    def expressao(self):
        """expressao := termo (('+' | '-') termo)*"""
        self._entrar()
        try:
            esquerda = self.termo()

            while self.peek()[0] in ('+', '-'):
                op = self.consume()
                direita = self.termo()
                if op[0] == '+':
                    esquerda = soma(esquerda, direita)
                else:
                    esquerda = subtracao(esquerda, direita)

            return esquerda
        finally:
            self._sair()

    def termo(self):
        """termo := fator (('*' | '/') fator)*"""
        self._entrar()
        try:
            esquerda = self.fator()

            while self.peek()[0] in ('*', '/'):
                op = self.consume()
                direita = self.fator()
                if op[0] == '*':
                    esquerda = multiplicacao(esquerda, direita)
                else:
                    # Divisão: converte para fração
                    if (esquerda.tipo_de_numero == 'racional' and
                            direita.tipo_de_numero == 'racional'):
                        from engine.basic import operacoes_basicas as ops
                        resultado = ops.div(esquerda.return_number(), direita.return_number())
                        return Racional(resultado)
                    esquerda = multiplicacao(esquerda, direita)

            return esquerda
        finally:
            self._sair()

    def fator(self):
        """fator := atomo ('^' fator)?"""
        self._entrar()
        try:
            base = self.atomo()

            if self.peek()[0] == '^':
                self.consume('^')
                expoente = self.fator()
                # Se ambos são racionais inteiros, criar Exponencial
                if (base.tipo_de_numero == 'racional' and
                        expoente.tipo_de_numero == 'racional'):
                    return Exponencial(base.return_number(), expoente.return_number())
                raise ParserError("Exponencial com base/expoente não-racional ainda não suportado")

            return base
        finally:
            self._sair()

    def atomo(self):
        """atomo := numero | fracao | sqrt(...) | log_b(...) | '(' expr ')' | '-' fator"""
        self._entrar()
        try:
            tipo, valor = self.peek()

            # Número negativo (unário)
            if tipo == '-':
                self.consume('-')
                operando = self.fator()
                if operando.tipo_de_numero == 'racional':
                    from engine.basic import operacoes_basicas as ops
                    return Racional(ops.multi('-1', operando.return_number()))
                # Para irracionais, inverte o coeficiente
                from engine.basic import operacoes_basicas as ops
                novo_coef = ops.multi('-1', operando.coeficiente)
                if operando.tipo_de_numero == 'raiz':
                    return Raiz(operando.return_indice(), operando.return_radicando(), novo_coef)
                elif operando.tipo_de_numero == 'exponencial':
                    return Exponencial(operando.return_base(), operando.return_expoente(), novo_coef)
                elif operando.tipo_de_numero == 'logaritmo':
                    return Logaritmo(operando.return_base(), operando.return_logaritmando(), novo_coef)

            # Número (pode ser parte de fração: "3/4")
            if tipo == 'NUM':
                return self._parse_numero()

            # sqrt(...) ou sqrt_n(...)
            if tipo == 'SQRT':
                return self._parse_raiz()

            # log_b(...) ou log(...)
            if tipo == 'LOG':
                return self._parse_logaritmo()

            # Parênteses
            if tipo == '(':
                self.consume('(')
                resultado = self.expressao()
                self.consume(')')
                return resultado

            raise ParserError(f"Token inesperado: '{tipo}' ('{valor}')")
        finally:
            self._sair()

    def _parse_numero(self):
        """Parse número inteiro, decimal ou fração (3/4)."""
        token = self.consume('NUM')
        numerador = token[1]

        # Verifica se é fração: "3/4"
        if self.peek()[0] == '/':
            # Olhar adiante para ver se é divisão ou fração
            prox_pos = self.pos + 1
            if prox_pos < len(self.tokens) and self.tokens[prox_pos][0] == 'NUM':
                self.consume('/')
                denominador = self.consume('NUM')[1]
                return Racional(f"{numerador}/{denominador}")

        return Racional(numerador)

    def _parse_raiz(self):
        """Parse sqrt(x) ou sqrt_n(x) onde n é o índice."""
        self.consume('SQRT')
        indice = '2'  # padrão: raiz quadrada

        # Verifica se tem índice: sqrt_3(...)
        if self.peek()[0] == '_':
            self.consume('_')
            indice = self.consume('NUM')[1]

        self.consume('(')
        # O argumento é uma expressão simples (número)
        argumento = self.expressao()
        self.consume(')')

        if argumento.tipo_de_numero == 'racional':
            return Raiz(indice, argumento.return_number())

        raise ParserError("Raiz com argumento não-racional ainda não suportado")

    def _parse_logaritmo(self):
        """Parse log_b(x) ou log(x) (base 10 por padrão)."""
        self.consume('LOG')
        base = '10'  # padrão: log base 10

        # Verifica se tem base: log_3(...)
        if self.peek()[0] == '_':
            self.consume('_')
            base = self.consume('NUM')[1]

        self.consume('(')
        argumento = self.expressao()
        self.consume(')')

        if argumento.tipo_de_numero == 'racional':
            return Logaritmo(base, argumento.return_number())

        raise ParserError("Logaritmo com argumento não-racional ainda não suportado")


# ============================================================
# Interface pública
# ============================================================

def parsear(texto):
    """Converte texto em objeto do engine.

    Exemplos:
        parsear("3 + 4")       → Racional('7')
        parsear("sqrt(216)")   → Raiz('2', '216')
        parsear("2^3")         → Exponencial('2', '3')
        parsear("log_3(9)")    → Logaritmo('3', '9')
    """
    tokens = tokenizar(texto)
    parser = Parser(tokens)
    return parser.parse()
