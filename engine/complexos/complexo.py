"""Numero complexo com aritmetica exata: z = real + imag*i.

Usa engine.basic.operacoes_basicas para todas as operacoes aritmeticas,
garantindo precisao racional (fracionaria) sempre que possivel.
"""

from engine.basic import operacoes_basicas as ops
from engine.basic.passo import Passo, Historico
import math


class Complexo:
    """Numero complexo z = real + imag*i com aritmetica exata."""

    def __init__(self, real: str = '0', imag: str = '0'):
        self.real = str(real)
        self.imag = str(imag)
        self.tipo_de_numero = 'complexo'

    # ------------------------------------------------------------------
    # Aritmetica
    # ------------------------------------------------------------------

    def somar(self, outro: 'Complexo') -> 'Complexo':
        """z1 + z2 = (a+c) + (b+d)i"""
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Soma de numeros complexos',
            latex_antes=f'({self.representacao_latex()}) + ({outro.representacao_latex()})',
            regra='Soma de complexos',
        ))
        r = ops.soma(self.real, outro.real)
        i = ops.soma(self.imag, outro.imag)
        resultado = Complexo(r, i)
        historico.adicionar(Passo(
            nivel=2,
            descricao='Somar partes reais e imaginarias separadamente',
            latex_depois=resultado.representacao_latex(),
            regra='Soma de complexos',
        ))
        return resultado

    def subtrair(self, outro: 'Complexo') -> 'Complexo':
        """z1 - z2 = (a-c) + (b-d)i"""
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Subtracao de numeros complexos',
            latex_antes=f'({self.representacao_latex()}) - ({outro.representacao_latex()})',
            regra='Subtracao de complexos',
        ))
        r = ops.diff(self.real, outro.real)
        i = ops.diff(self.imag, outro.imag)
        resultado = Complexo(r, i)
        historico.adicionar(Passo(
            nivel=2,
            descricao='Subtrair partes reais e imaginarias separadamente',
            latex_depois=resultado.representacao_latex(),
            regra='Subtracao de complexos',
        ))
        return resultado

    def multiplicar(self, outro: 'Complexo') -> 'Complexo':
        """(a+bi)(c+di) = (ac-bd) + (ad+bc)i"""
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Multiplicacao de numeros complexos',
            latex_antes=f'({self.representacao_latex()}) \\cdot ({outro.representacao_latex()})',
            regra='Multiplicacao de complexos',
        ))
        ac = ops.multi(self.real, outro.real)
        bd = ops.multi(self.imag, outro.imag)
        ad = ops.multi(self.real, outro.imag)
        bc = ops.multi(self.imag, outro.real)

        historico.adicionar(Passo(
            nivel=3,
            descricao=f'ac={ac}, bd={bd}, ad={ad}, bc={bc}',
            regra='Produtos parciais',
        ))

        r = ops.diff(ac, bd)
        i = ops.soma(ad, bc)
        resultado = Complexo(r, i)
        historico.adicionar(Passo(
            nivel=2,
            descricao='Aplicar formula (ac-bd) + (ad+bc)i',
            latex_depois=resultado.representacao_latex(),
            regra='Multiplicacao de complexos',
        ))
        return resultado

    def dividir(self, outro: 'Complexo') -> 'Complexo':
        """z1/z2 = z1 * conj(z2) / |z2|^2"""
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Divisao de numeros complexos',
            latex_antes=f'\\frac{{{self.representacao_latex()}}}{{{outro.representacao_latex()}}}',
            regra='Divisao de complexos',
        ))

        # |z2|^2 = c^2 + d^2
        c2 = ops.multi(outro.real, outro.real)
        d2 = ops.multi(outro.imag, outro.imag)
        mod2 = ops.soma(c2, d2)

        if mod2 == '0':
            raise ZeroDivisionError("Divisao por zero complexo")

        historico.adicionar(Passo(
            nivel=2,
            descricao='Multiplicar numerador e denominador pelo conjugado do denominador',
            regra='Divisao de complexos',
        ))

        # Numerador = z1 * conj(z2)
        conj = outro.conjugado()
        numerador = self.multiplicar(conj)

        r = ops.reduz_fracao(numerador.real + '/' + mod2)
        i = ops.reduz_fracao(numerador.imag + '/' + mod2)
        resultado = Complexo(r, i)
        historico.adicionar(Passo(
            nivel=2,
            descricao='Dividir pelo modulo ao quadrado do denominador',
            latex_depois=resultado.representacao_latex(),
            regra='Divisao de complexos',
        ))
        return resultado

    # ------------------------------------------------------------------
    # Propriedades
    # ------------------------------------------------------------------

    def conjugado(self) -> 'Complexo':
        """conj(a+bi) = a - bi"""
        if self.imag == '0':
            return Complexo(self.real, '0')
        if self.imag.startswith('-'):
            return Complexo(self.real, self.imag[1:])
        return Complexo(self.real, '-' + self.imag)

    def modulo(self) -> str:
        """|z| = sqrt(a^2 + b^2) — retorna valor como string."""
        a2 = ops.multi(self.real, self.real)
        b2 = ops.multi(self.imag, self.imag)
        soma = ops.soma(a2, b2)
        # Converter para float para sqrt
        val = float(soma) if '/' not in soma else float(soma.split('/')[0]) / float(soma.split('/')[1])
        return str(math.sqrt(val))

    def argumento(self) -> str:
        """arg(z) = atan2(b, a) em radianos — retorna valor como string."""
        a = float(self.real) if '/' not in self.real else float(self.real.split('/')[0]) / float(self.real.split('/')[1])
        b = float(self.imag) if '/' not in self.imag else float(self.imag.split('/')[0]) / float(self.imag.split('/')[1])
        return str(math.atan2(b, a))

    def forma_polar(self) -> tuple:
        """Retorna (r, theta) onde z = r*e^(i*theta)."""
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Converter para forma polar',
            latex_antes=self.representacao_latex(),
            regra='Forma polar',
        ))
        r = self.modulo()
        theta = self.argumento()
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'r = {r}, theta = {theta}',
            latex_depois=f'{r} \\cdot e^{{i \\cdot {theta}}}',
            regra='Forma polar',
        ))
        return (r, theta)

    def raizes_nesimas(self, n: int) -> list:
        """n raizes de z: r^(1/n) * e^(i(theta+2k*pi)/n), k=0..n-1."""
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Calcular as {n} raizes {n}-esimas',
            latex_antes=self.representacao_latex(),
            regra='Raizes n-esimas',
        ))

        r_float = float(self.modulo())
        theta_float = float(self.argumento())
        r_n = r_float ** (1.0 / n)

        raizes = []
        for k in range(n):
            angulo = (theta_float + 2 * math.pi * k) / n
            re = r_n * math.cos(angulo)
            im = r_n * math.sin(angulo)
            # Arredondar valores muito proximos de zero ou inteiros
            re = _arredondar_proximo(re)
            im = _arredondar_proximo(im)
            raizes.append(Complexo(str(re), str(im)))
            historico.adicionar(Passo(
                nivel=3,
                descricao=f'k={k}: angulo={(theta_float + 2 * math.pi * k) / n:.6f}',
                latex_depois=f'{re} + {im}i',
                regra='Raizes n-esimas',
            ))

        return raizes

    def potencia(self, n) -> 'Complexo':
        """z^n via De Moivre: (r*e^(i*theta))^n = r^n * e^(i*n*theta)."""
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Calcular potencia z^{n} via De Moivre',
            latex_antes=f'({self.representacao_latex()})^{{{n}}}',
            regra='Teorema de De Moivre',
        ))

        r_float = float(self.modulo())
        theta_float = float(self.argumento())
        n_int = int(n)

        r_n = r_float ** n_int
        angulo = theta_float * n_int
        re = r_n * math.cos(angulo)
        im = r_n * math.sin(angulo)
        re = _arredondar_proximo(re)
        im = _arredondar_proximo(im)

        resultado = Complexo(str(re), str(im))
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'r^n = {r_n}, n*theta = {angulo}',
            latex_depois=resultado.representacao_latex(),
            regra='Teorema de De Moivre',
        ))
        return resultado

    # ------------------------------------------------------------------
    # Representacao
    # ------------------------------------------------------------------

    def representacao_latex(self) -> str:
        """Retorna string LaTeX formatada: a + bi."""
        r = self.real
        i = self.imag

        if i == '0':
            return r
        if r == '0':
            if i == '1':
                return 'i'
            if i == '-1':
                return '-i'
            return f'{i}i'

        if i == '1':
            parte_imag = '+ i'
        elif i == '-1':
            parte_imag = '- i'
        elif i.startswith('-'):
            parte_imag = f'- {i[1:]}i'
        else:
            parte_imag = f'+ {i}i'

        return f'{r} {parte_imag}'

    def __eq__(self, other):
        if not isinstance(other, Complexo):
            return NotImplemented
        return self.real == other.real and self.imag == other.imag

    def __hash__(self):
        return hash(('complexo', self.real, self.imag))

    def __repr__(self):
        return f'Complexo({self.real}, {self.imag})'


# ======================================================================
# Funcoes auxiliares
# ======================================================================

def _arredondar_proximo(valor: float, tolerancia: float = 1e-10) -> float:
    """Arredonda valores muito proximos de inteiros ou zero."""
    arredondado = round(valor)
    if abs(valor - arredondado) < tolerancia:
        return float(arredondado)
    return round(valor, 10)


def euler(theta: str) -> Complexo:
    """e^(i*theta) = cos(theta) + i*sin(theta).

    theta em radianos (string numerica).
    """
    t = float(theta)
    re = math.cos(t)
    im = math.sin(t)
    re = _arredondar_proximo(re)
    im = _arredondar_proximo(im)
    return Complexo(str(re), str(im))


def de_moivre(r: str, theta: str, n: int) -> Complexo:
    """(r*e^(i*theta))^n = r^n * e^(i*n*theta).

    Aplica o Teorema de De Moivre.
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Aplicar De Moivre: ({r} * e^(i*{theta}))^{n}',
        regra='Teorema de De Moivre',
    ))

    r_float = float(r)
    t_float = float(theta)
    n_int = int(n)

    r_n = r_float ** n_int
    angulo = t_float * n_int
    re = r_n * math.cos(angulo)
    im = r_n * math.sin(angulo)
    re = _arredondar_proximo(re)
    im = _arredondar_proximo(im)

    resultado = Complexo(str(re), str(im))
    historico.adicionar(Passo(
        nivel=2,
        descricao=f'r^n = {r_n}, n*theta = {angulo}',
        latex_depois=resultado.representacao_latex(),
        regra='Teorema de De Moivre',
    ))
    return resultado
