"""Parser simbólico: converte texto em árvore NoExpressao.

Produz a AST usada pelo motor de cálculo (derivadas, integrais, limites, etc.).
Suporta: números, variáveis, operadores (+, -, *, /, ^), funções (sin, cos, tan,
arcsin, arccos, arctan, ln, exp, sqrt, abs), parênteses, e multiplicação implícita.

Gramática:
    expressao := termo (('+' | '-') termo)*
    termo     := unario (('*' | '/') unario)*
    unario    := '-' unario | potencia
    potencia  := atomo ('^' unario)?
    atomo     := NUM | VAR | FUNC '(' expressao ')' | '(' expressao ')'

Exemplos:
    parsear_simbolico("x^2 + 3*x + 1")      → op('+', op('+', op('^', var('x'), num('2')),
                                                               op('*', num('3'), var('x'))),
                                                        num('1'))
    parsear_simbolico("sin(x)")               → func('sin', var('x'))
    parsear_simbolico("2x")                   → op('*', num('2'), var('x'))
    parsear_simbolico("e^x")                  → func('exp', var('x'))
"""

from engine.calculo.arvore import NoExpressao, num, var, op, func


# ============================================================
# Funções reconhecidas
# ============================================================

FUNCOES_RECONHECIDAS = {
    'sin', 'cos', 'tan',
    'arcsin', 'arccos', 'arctan',
    'asin', 'acos', 'atan',
    'sinh', 'cosh', 'tanh',
    'ln', 'log', 'exp',
    'sqrt', 'abs',
    'sec', 'csc', 'cot',
}

VARIAVEIS_PERMITIDAS = {'x', 'y', 'z', 'a', 'b', 'c', 'n', 't', 'u', 'v', 'w', 'r', 's'}

# Constantes matemáticas
CONSTANTES = {
    'pi': '3.14159265358979323846',
    'e': '2.71828182845904523536',
}


class TokenizadorSimbolico:
    """Tokenizador para expressões simbólicas."""

    def __init__(self, texto: str):
        self.texto = texto.replace(' ', '')
        self.pos = 0
        self.tokens = []
        self._tokenizar()

    def _tokenizar(self):
        texto = self.texto
        i = 0

        while i < len(texto):
            c = texto[i]

            # Números (inteiros e decimais)
            if c.isdigit() or (c == '.' and i + 1 < len(texto) and texto[i + 1].isdigit()):
                inicio = i
                while i < len(texto) and (texto[i].isdigit() or texto[i] == '.'):
                    i += 1
                self.tokens.append(('NUM', texto[inicio:i]))
                continue

            # Palavras: funções, variáveis, constantes
            if c.isalpha():
                inicio = i
                while i < len(texto) and (texto[i].isalpha() or texto[i].isdigit()):
                    i += 1
                palavra = texto[inicio:i]

                if palavra in FUNCOES_RECONHECIDAS:
                    self.tokens.append(('FUNC', palavra))
                elif palavra == 'e' and i < len(texto) and texto[i] == '^':
                    # 'e' seguido de '^' → base de exponencial natural (e^x → exp(x))
                    self.tokens.append(('E_BASE', 'e'))
                elif palavra in CONSTANTES:
                    self.tokens.append(('NUM', CONSTANTES[palavra]))
                elif len(palavra) == 1 and palavra in VARIAVEIS_PERMITIDAS:
                    self.tokens.append(('VAR', palavra))
                elif palavra == 'pi':
                    self.tokens.append(('NUM', CONSTANTES['pi']))
                else:
                    # Tentar decompor em variáveis individuais (ex: "xy" → "x", "y")
                    for ch in palavra:
                        if ch in VARIAVEIS_PERMITIDAS:
                            self.tokens.append(('VAR', ch))
                        else:
                            raise ValueError(f"Identificador desconhecido: '{palavra}'")
                continue

            # Operadores
            if c in '+-*/^':
                self.tokens.append(('OP', c))
                i += 1
                continue

            # Parênteses
            if c == '(':
                self.tokens.append(('LPAREN', '('))
                i += 1
                continue
            if c == ')':
                self.tokens.append(('RPAREN', ')'))
                i += 1
                continue

            # Pipe para valor absoluto |...|
            if c == '|':
                self.tokens.append(('PIPE', '|'))
                i += 1
                continue

            raise ValueError(f"Caractere inesperado: '{c}' na posição {i}")

        # Inserir multiplicação implícita
        self.tokens = self._inserir_multiplicacao_implicita(self.tokens)
        self.tokens.append(('EOF', ''))

    def _inserir_multiplicacao_implicita(self, tokens):
        """Insere '*' implícito entre tokens adjacentes que implicam multiplicação."""
        resultado = []
        for i, tok in enumerate(tokens):
            resultado.append(tok)
            if i + 1 < len(tokens):
                prox = tokens[i + 1]
                # NUM VAR, NUM FUNC, NUM (, VAR (, VAR VAR, VAR FUNC,
                # ) NUM, ) VAR, ) FUNC, ) (, NUM E_BASE
                esq_tipo = tok[0]
                dir_tipo = prox[0]

                inserir = False
                if esq_tipo in ('NUM', 'VAR', 'E_BASE') and dir_tipo in ('VAR', 'FUNC', 'LPAREN', 'E_BASE', 'PIPE'):
                    inserir = True
                if esq_tipo == 'NUM' and dir_tipo == 'NUM':
                    # Não inserir entre números (ex: "3.14" já foi tokenizado)
                    inserir = False
                if esq_tipo == 'RPAREN' and dir_tipo in ('NUM', 'VAR', 'FUNC', 'LPAREN', 'E_BASE', 'PIPE'):
                    inserir = True
                if esq_tipo in ('VAR', 'E_BASE') and dir_tipo == 'NUM':
                    inserir = True

                if inserir:
                    resultado.append(('OP', '*'))
        return resultado


class ParserSimbolico:
    """Parser descendente recursivo para expressões simbólicas → NoExpressao."""

    MAX_PROFUNDIDADE = 100

    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0
        self._profundidade = 0

    def _peek(self):
        return self.tokens[self.pos]

    def _consume(self, tipo_esperado=None):
        tok = self.tokens[self.pos]
        if tipo_esperado and tok[0] != tipo_esperado:
            raise ValueError(f"Esperado '{tipo_esperado}', encontrado '{tok[0]}' ('{tok[1]}')")
        self.pos += 1
        return tok

    def _entrar(self):
        self._profundidade += 1
        if self._profundidade > self.MAX_PROFUNDIDADE:
            raise ValueError("Expressão excede profundidade máxima")

    def _sair(self):
        self._profundidade -= 1

    def parse(self) -> NoExpressao:
        resultado = self._expressao()
        if self._peek()[0] != 'EOF':
            raise ValueError(f"Tokens não consumidos: '{self._peek()[1]}'")
        return resultado

    def _expressao(self) -> NoExpressao:
        """expressao := termo (('+' | '-') termo)*"""
        self._entrar()
        try:
            esquerda = self._termo()
            while self._peek()[0] == 'OP' and self._peek()[1] in ('+', '-'):
                operador = self._consume()[1]
                direita = self._termo()
                esquerda = op(operador, esquerda, direita)
            return esquerda
        finally:
            self._sair()

    def _termo(self) -> NoExpressao:
        """termo := unario (('*' | '/') unario)*"""
        self._entrar()
        try:
            esquerda = self._unario()
            while self._peek()[0] == 'OP' and self._peek()[1] in ('*', '/'):
                operador = self._consume()[1]
                direita = self._unario()
                esquerda = op(operador, esquerda, direita)
            return esquerda
        finally:
            self._sair()

    def _unario(self) -> NoExpressao:
        """unario := '-' unario | potencia"""
        self._entrar()
        try:
            if self._peek()[0] == 'OP' and self._peek()[1] == '-':
                self._consume()
                operando = self._unario()
                return op('*', num('-1'), operando)
            return self._potencia()
        finally:
            self._sair()

    def _potencia(self) -> NoExpressao:
        """potencia := atomo ('^' unario)?"""
        self._entrar()
        try:
            # Guardar se a base é E_BASE para converter e^x → exp(x)
            eh_e_base = self._peek()[0] == 'E_BASE'
            base = self._atomo()
            if self._peek()[0] == 'OP' and self._peek()[1] == '^':
                self._consume()
                expoente = self._unario()
                # e^algo → exp(algo)
                if eh_e_base:
                    return func('exp', expoente)
                return op('^', base, expoente)
            return base
        finally:
            self._sair()

    def _atomo(self) -> NoExpressao:
        """atomo := NUM | VAR | E_BASE | FUNC '(' expr ')' | '(' expr ')' | '|' expr '|'"""
        self._entrar()
        try:
            tipo, valor = self._peek()

            if tipo == 'NUM':
                self._consume()
                return num(valor)

            if tipo == 'VAR':
                self._consume()
                return var(valor)

            if tipo == 'E_BASE':
                self._consume()
                # Se seguido de ^, será tratado na regra de potência
                # Aqui retornamos exp(1) como base
                return func('exp', num('1'))

            if tipo == 'FUNC':
                nome_func = valor
                self._consume()

                # Normalizar nomes
                if nome_func == 'asin':
                    nome_func = 'arcsin'
                elif nome_func == 'acos':
                    nome_func = 'arccos'
                elif nome_func == 'atan':
                    nome_func = 'arctan'

                # sec, csc, cot → expressões compostas
                if nome_func == 'sec':
                    self._consume('LPAREN')
                    arg = self._expressao()
                    self._consume('RPAREN')
                    return op('/', num('1'), func('cos', arg))
                if nome_func == 'csc':
                    self._consume('LPAREN')
                    arg = self._expressao()
                    self._consume('RPAREN')
                    return op('/', num('1'), func('sin', arg))
                if nome_func == 'cot':
                    self._consume('LPAREN')
                    arg = self._expressao()
                    self._consume('RPAREN')
                    return op('/', func('cos', arg), func('sin', arg))

                self._consume('LPAREN')
                arg = self._expressao()
                self._consume('RPAREN')
                return func(nome_func, arg)

            if tipo == 'LPAREN':
                self._consume()
                resultado = self._expressao()
                self._consume('RPAREN')
                return resultado

            if tipo == 'PIPE':
                self._consume()
                resultado = self._expressao()
                self._consume('PIPE')
                return func('abs', resultado)

            raise ValueError(f"Token inesperado: '{tipo}' ('{valor}')")
        finally:
            self._sair()


def parsear_simbolico(texto: str) -> NoExpressao:
    """Converte texto em árvore NoExpressao.

    Exemplos:
        >>> parsear_simbolico("x^2 + 3*x + 1")
        op('+', op('+', op('^', var('x'), num('2')), op('*', num('3'), var('x'))), num('1'))

        >>> parsear_simbolico("sin(x)")
        func('sin', var('x'))

        >>> parsear_simbolico("2x")
        op('*', num('2'), var('x'))

        >>> parsear_simbolico("e^x")
        op('^', func('exp', num('1')), var('x'))
    """
    tokenizador = TokenizadorSimbolico(texto)
    parser = ParserSimbolico(tokenizador.tokens)
    return parser.parse()
