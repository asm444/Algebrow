"""Funções elementares: linear, quadrática, exponencial e logarítmica."""

from engine.basic.operacoes_basicas import soma, diff, multi, div, reduz_fracao
from engine.funcoes.funcao_base import FuncaoBase


class FuncaoLinear(FuncaoBase):
    """f(x) = ax + b, onde a e b são strings numéricas."""

    def __init__(self, a: str, b: str, variavel: str = 'x'):
        super().__init__('linear', variavel)
        self.a = str(a)
        self.b = str(b)

    def avaliar(self, x: str) -> str:
        """Retorna f(x) = a*x + b como string exata."""
        x = str(x)
        ax = multi(self.a, x)
        return soma(ax, self.b)

    def dominio(self) -> str:
        return "(-\u221e, +\u221e)"

    def imagem(self) -> str:
        if self.a == '0':
            return "{" + self.b + "}"
        return "(-\u221e, +\u221e)"

    def zeros(self) -> list:
        """Retorna os zeros: x = -b/a. Lista vazia se a=0."""
        if self.a == '0':
            return []
        neg_b = multi('-1', self.b)
        return [reduz_fracao(neg_b + '/' + self.a)]

    def inversa(self):
        """Retorna a função inversa: f⁻¹(x) = (1/a)x + (-b/a)."""
        if self.a == '0':
            raise ValueError("Função constante não possui inversa.")
        novo_a = reduz_fracao('1/' + self.a)
        neg_b = multi('-1', self.b)
        novo_b = reduz_fracao(neg_b + '/' + self.a)
        return FuncaoLinear(novo_a, novo_b, self.variavel)

    def representacao_latex(self) -> str:
        partes = []
        # Termo ax
        if self.a == '0':
            pass
        elif self.a == '1':
            partes.append(self.variavel)
        elif self.a == '-1':
            partes.append(f'-{self.variavel}')
        else:
            if '/' in self.a:
                num, den = self.a.split('/')
                partes.append(f'\\frac{{{num}}}{{{den}}}{self.variavel}')
            else:
                partes.append(f'{self.a}{self.variavel}')

        # Termo b
        if self.b != '0':
            if not partes:
                partes.append(self.b)
            else:
                b_float = float(self.b) if '/' not in self.b else float(self.b.split('/')[0]) / float(self.b.split('/')[1])
                if b_float > 0:
                    partes.append(f' + {self.b}')
                else:
                    # Remover o sinal negativo e usar ' - '
                    b_abs = self.b[1:] if self.b.startswith('-') else self.b
                    partes.append(f' - {b_abs}')
        elif not partes:
            partes.append('0')

        return ''.join(partes)


class FuncaoQuadratica(FuncaoBase):
    """f(x) = ax² + bx + c, onde a, b e c são strings numéricas."""

    def __init__(self, a: str, b: str, c: str, variavel: str = 'x'):
        super().__init__('quadratica', variavel)
        self.a = str(a)
        self.b = str(b)
        self.c = str(c)

    def avaliar(self, x: str) -> str:
        """Retorna f(x) = a*x² + b*x + c como string exata."""
        x = str(x)
        x2 = multi(x, x)
        ax2 = multi(self.a, x2)
        bx = multi(self.b, x)
        return soma(soma(ax2, bx), self.c)

    def dominio(self) -> str:
        return "(-\u221e, +\u221e)"

    def imagem(self) -> str:
        _, yv = self.vertice()
        if float(self.a) > 0:
            return f"[{yv}, +\u221e)"
        else:
            return f"(-\u221e, {yv}]"

    def vertice(self) -> tuple:
        """Retorna (xv, yv) do vértice da parábola."""
        neg_b = multi('-1', self.b)
        dois_a = multi('2', self.a)
        xv = reduz_fracao(neg_b + '/' + dois_a)
        yv = self.avaliar(xv)
        return (xv, yv)

    def zeros(self) -> list:
        """Retorna os zeros usando Equacao2Grau internamente."""
        from engine.algebra.equacao import Equacao2Grau
        eq = Equacao2Grau(self.a, self.b, self.c)
        try:
            solucoes, _ = eq.resolver()
            return [s.representacao_latex() for s in solucoes]
        except ValueError:
            # Discriminante negativo: sem raízes reais
            return []

    @property
    def concavidade(self) -> str:
        a_float = float(self.a) if '/' not in self.a else float(self.a.split('/')[0]) / float(self.a.split('/')[1])
        if a_float > 0:
            return 'cima'
        elif a_float < 0:
            return 'baixo'
        else:
            raise ValueError("Coeficiente 'a' não pode ser zero em função quadrática.")

    def representacao_latex(self) -> str:
        partes = []
        v = self.variavel

        # Termo ax²
        if self.a == '1':
            partes.append(f'{v}^{{2}}')
        elif self.a == '-1':
            partes.append(f'-{v}^{{2}}')
        else:
            partes.append(f'{self.a}{v}^{{2}}')

        # Termo bx
        if self.b != '0':
            b_float = float(self.b) if '/' not in self.b else float(self.b.split('/')[0]) / float(self.b.split('/')[1])
            if b_float > 0:
                if self.b == '1':
                    partes.append(f' + {v}')
                else:
                    partes.append(f' + {self.b}{v}')
            else:
                b_abs = self.b[1:] if self.b.startswith('-') else self.b
                if b_abs == '1':
                    partes.append(f' - {v}')
                else:
                    partes.append(f' - {b_abs}{v}')

        # Termo c
        if self.c != '0':
            c_float = float(self.c) if '/' not in self.c else float(self.c.split('/')[0]) / float(self.c.split('/')[1])
            if c_float > 0:
                partes.append(f' + {self.c}')
            else:
                c_abs = self.c[1:] if self.c.startswith('-') else self.c
                partes.append(f' - {c_abs}')

        return ''.join(partes)


class FuncaoExponencial(FuncaoBase):
    """f(x) = a·bˣ, onde a é o coeficiente e b é a base (strings numéricas)."""

    def __init__(self, a: str, b: str, variavel: str = 'x'):
        super().__init__('exponencial', variavel)
        self.a = str(a)
        self.b = str(b)

        b_float = float(self.b) if '/' not in self.b else float(self.b.split('/')[0]) / float(self.b.split('/')[1])
        if b_float <= 0 or b_float == 1:
            raise ValueError("A base da exponencial deve ser positiva e diferente de 1.")

    def avaliar(self, x: str) -> str:
        """Retorna f(x) = a * b^x como string exata."""
        x = str(x)
        # b^x: para expoentes inteiros, calcular exatamente
        x_float = float(x) if '/' not in x else float(x.split('/')[0]) / float(x.split('/')[1])
        if x_float == int(x_float):
            exp = int(x_float)
            if exp >= 0:
                # b^exp via multiplicação repetida
                resultado = '1'
                for _ in range(exp):
                    resultado = multi(resultado, self.b)
            else:
                # b^(-exp) e depois inverter
                resultado = '1'
                for _ in range(-exp):
                    resultado = multi(resultado, self.b)
                resultado = reduz_fracao('1/' + resultado)
            return multi(self.a, resultado)
        else:
            # Para expoentes não inteiros, usar float como fallback
            from math import pow as mpow
            b_val = float(self.b) if '/' not in self.b else float(self.b.split('/')[0]) / float(self.b.split('/')[1])
            val = float(self.a) * mpow(b_val, x_float)
            if val == int(val):
                return str(int(val))
            return str(val)

    def dominio(self) -> str:
        return "(-\u221e, +\u221e)"

    def imagem(self) -> str:
        a_float = float(self.a) if '/' not in self.a else float(self.a.split('/')[0]) / float(self.a.split('/')[1])
        if a_float > 0:
            return "(0, +\u221e)"
        elif a_float < 0:
            return "(-\u221e, 0)"
        else:
            return "{0}"

    def assintotas(self) -> dict:
        """Retorna as assíntotas da função exponencial."""
        return {'horizontal': 'y = 0'}

    def representacao_latex(self) -> str:
        v = self.variavel
        if self.a == '1':
            return f'{self.b}^{{{v}}}'
        elif self.a == '-1':
            return f'-{self.b}^{{{v}}}'
        else:
            return f'{self.a} \\cdot {self.b}^{{{v}}}'


class FuncaoLogaritmica(FuncaoBase):
    """f(x) = a·log_b(x), onde a é o coeficiente e b é a base (strings numéricas)."""

    def __init__(self, a: str, b: str, variavel: str = 'x'):
        super().__init__('logaritmica', variavel)
        self.a = str(a)
        self.b = str(b)

        b_float = float(self.b) if '/' not in self.b else float(self.b.split('/')[0]) / float(self.b.split('/')[1])
        if b_float <= 0 or b_float == 1:
            raise ValueError("A base do logaritmo deve ser positiva e diferente de 1.")

    def avaliar(self, x: str) -> str:
        """Retorna f(x) = a * log_b(x) como string exata quando possível."""
        x = str(x)
        x_float = float(x) if '/' not in x else float(x.split('/')[0]) / float(x.split('/')[1])
        if x_float <= 0:
            raise ValueError("Logaritmo não definido para valores <= 0.")

        b_float = float(self.b) if '/' not in self.b else float(self.b.split('/')[0]) / float(self.b.split('/')[1])

        # Tentar calcular log exato: verificar se x é potência inteira de b
        if x_float == 1:
            return '0'

        # Verificar potências inteiras de b
        max_iter = 1000
        if b_float > 1:
            potencia = b_float
            exp = 1
            while potencia < x_float and exp < max_iter:
                potencia *= b_float
                exp += 1
            if abs(potencia - x_float) < 1e-12:
                return multi(self.a, str(exp))
        elif 0 < b_float < 1:
            potencia = b_float
            exp = 1
            while potencia > x_float and exp < max_iter:
                potencia *= b_float
                exp += 1
            if abs(potencia - x_float) < 1e-12:
                return multi(self.a, str(exp))

        # Fallback: usar math.log
        from math import log
        val = float(self.a) * log(x_float, b_float)
        if abs(val - round(val)) < 1e-12:
            return str(int(round(val)))
        return str(val)

    def dominio(self) -> str:
        return "(0, +\u221e)"

    def imagem(self) -> str:
        return "(-\u221e, +\u221e)"

    def zeros(self) -> list:
        """log_b(1) = 0, então x=1 é sempre zero."""
        return ['1']

    def representacao_latex(self) -> str:
        v = self.variavel
        if self.a == '1':
            return f'\\log_{{{self.b}}}{{{v}}}'
        elif self.a == '-1':
            return f'-\\log_{{{self.b}}}{{{v}}}'
        else:
            return f'{self.a}\\log_{{{self.b}}}{{{v}}}'
