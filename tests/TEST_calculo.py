"""Testes para o modulo de calculo simbolico."""

import math
import pytest
from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.derivada import derivar, simplificar_no
from engine.calculo.integral import integrar
from engine.calculo.limite import limite
from engine.basic.passo import Historico


# ============================================================
# Testes de simplificacao
# ============================================================

class TestSimplificacao:
    def test_zero_mais_x(self):
        # 0 + x -> x
        expr = op('+', num('0'), var('x'))
        result = simplificar_no(expr)
        assert result == var('x')

    def test_x_mais_zero(self):
        # x + 0 -> x
        expr = op('+', var('x'), num('0'))
        result = simplificar_no(expr)
        assert result == var('x')

    def test_um_vezes_x(self):
        # 1 * x -> x
        expr = op('*', num('1'), var('x'))
        result = simplificar_no(expr)
        assert result == var('x')

    def test_x_vezes_um(self):
        # x * 1 -> x
        expr = op('*', var('x'), num('1'))
        result = simplificar_no(expr)
        assert result == var('x')

    def test_zero_vezes_x(self):
        # 0 * x -> 0
        expr = op('*', num('0'), var('x'))
        result = simplificar_no(expr)
        assert result == num('0')

    def test_x_vezes_zero(self):
        # x * 0 -> 0
        expr = op('*', var('x'), num('0'))
        result = simplificar_no(expr)
        assert result == num('0')

    def test_x_elevado_zero(self):
        # x^0 -> 1
        expr = op('^', var('x'), num('0'))
        result = simplificar_no(expr)
        assert result == num('1')

    def test_x_elevado_um(self):
        # x^1 -> x
        expr = op('^', var('x'), num('1'))
        result = simplificar_no(expr)
        assert result == var('x')


# ============================================================
# Testes de derivada
# ============================================================

class TestDerivada:
    def test_derivada_constante(self):
        # d/dx(5) = 0
        expr = num('5')
        result = derivar(expr, 'x')
        assert result == num('0')

    def test_derivada_x(self):
        # d/dx(x) = 1
        expr = var('x')
        result = derivar(expr, 'x')
        assert result == num('1')

    def test_derivada_outra_variavel(self):
        # d/dx(y) = 0
        expr = var('y')
        result = derivar(expr, 'x')
        assert result == num('0')

    def test_derivada_x_quadrado(self):
        # d/dx(x^2) = 2x
        expr = op('^', var('x'), num('2'))
        result = derivar(expr, 'x')
        # Deve avaliar como 2x para qualquer x
        for val in [1, 2, 3, -1, 0.5]:
            expected = 2 * val
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-10, f"x={val}: esperado {expected}, obteve {got}"

    def test_derivada_x_cubo(self):
        # d/dx(x^3) = 3x^2
        expr = op('^', var('x'), num('3'))
        result = derivar(expr, 'x')
        for val in [1, 2, -1, 0.5]:
            expected = 3 * val ** 2
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-10

    def test_derivada_soma(self):
        # d/dx(x + 5) = 1
        expr = op('+', var('x'), num('5'))
        result = derivar(expr, 'x')
        assert result.avaliar({'x': 10}) == 1.0

    def test_derivada_produto(self):
        # d/dx(x * x) = 2x (via regra do produto)
        expr = op('*', var('x'), var('x'))
        result = derivar(expr, 'x')
        for val in [1, 2, 3]:
            expected = 2 * val
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-10

    def test_derivada_sin(self):
        # d/dx(sin(x)) = cos(x)
        expr = func('sin', var('x'))
        result = derivar(expr, 'x')
        for val in [0, 1, math.pi / 4]:
            expected = math.cos(val)
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-10

    def test_derivada_cos(self):
        # d/dx(cos(x)) = -sin(x)
        expr = func('cos', var('x'))
        result = derivar(expr, 'x')
        for val in [0, 1, math.pi / 4]:
            expected = -math.sin(val)
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-10

    def test_derivada_exp(self):
        # d/dx(e^x) = e^x
        expr = func('exp', var('x'))
        result = derivar(expr, 'x')
        for val in [0, 1, 2]:
            expected = math.exp(val)
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-10

    def test_derivada_ln(self):
        # d/dx(ln(x)) = 1/x
        expr = func('ln', var('x'))
        result = derivar(expr, 'x')
        for val in [1, 2, 0.5]:
            expected = 1.0 / val
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-10

    def test_derivada_com_historico(self):
        hist = Historico(verbosidade=4)
        expr = op('+', var('x'), num('3'))
        derivar(expr, 'x', historico=hist)
        assert len(hist) > 0


# ============================================================
# Testes de integral
# ============================================================

class TestIntegral:
    def test_integral_constante(self):
        # integral(5 dx) = 5x + C
        expr = num('5')
        result = integrar(expr, 'x')
        # result deve ser 5*x + C
        # Avaliar com C=0 -> 5*x
        val = result.avaliar({'x': 3, 'C': 0})
        assert abs(val - 15.0) < 1e-10

    def test_integral_x(self):
        # integral(x dx) = x^2/2 + C
        expr = var('x')
        result = integrar(expr, 'x')
        val = result.avaliar({'x': 4, 'C': 0})
        assert abs(val - 8.0) < 1e-10

    def test_integral_x_quadrado(self):
        # integral(x^2 dx) = x^3/3 + C
        expr = op('^', var('x'), num('2'))
        result = integrar(expr, 'x')
        val = result.avaliar({'x': 3, 'C': 0})
        assert abs(val - 9.0) < 1e-10  # 3^3/3 = 9

    def test_integral_x_cubo(self):
        # integral(x^3 dx) = x^4/4 + C
        expr = op('^', var('x'), num('3'))
        result = integrar(expr, 'x')
        val = result.avaliar({'x': 2, 'C': 0})
        assert abs(val - 4.0) < 1e-10  # 2^4/4 = 4

    def test_integral_soma(self):
        # integral(x + 1 dx) = x^2/2 + x + C
        expr = op('+', var('x'), num('1'))
        result = integrar(expr, 'x')
        val = result.avaliar({'x': 2, 'C': 0})
        assert abs(val - 4.0) < 1e-10  # 2^2/2 + 1*2 = 2 + 2 = 4

    def test_integral_constante_vezes_x(self):
        # integral(3*x dx) = 3 * x^2/2 + C
        expr = op('*', num('3'), var('x'))
        result = integrar(expr, 'x')
        val = result.avaliar({'x': 2, 'C': 0})
        assert abs(val - 6.0) < 1e-10  # 3 * 4/2 = 6


# ============================================================
# Testes de limite
# ============================================================

class TestLimite:
    def test_limite_substituicao_direta(self):
        # lim x->2 (x^2) = 4
        expr = op('^', var('x'), num('2'))
        result = limite(expr, 'x', '2')
        assert result == '4'

    def test_limite_substituicao_direta_soma(self):
        # lim x->3 (x + 1) = 4
        expr = op('+', var('x'), num('1'))
        result = limite(expr, 'x', '3')
        assert result == '4'

    def test_limite_sinx_sobre_x(self):
        # lim x->0 (sin(x)/x) = 1 via L'Hopital
        expr = op('/', func('sin', var('x')), var('x'))
        result = limite(expr, 'x', '0')
        assert result == '1'

    def test_limite_constante(self):
        # lim x->5 (7) = 7
        expr = num('7')
        result = limite(expr, 'x', '5')
        assert result == '7'

    def test_limite_polinomio(self):
        # lim x->1 (x^2 + x) = 2
        expr = op('+', op('^', var('x'), num('2')), var('x'))
        result = limite(expr, 'x', '1')
        assert result == '2'


# ============================================================
# Testes de representacao LaTeX
# ============================================================

class TestLatex:
    def test_latex_numero(self):
        assert num('3').representacao_latex() == '3'

    def test_latex_variavel(self):
        assert var('x').representacao_latex() == 'x'

    def test_latex_soma(self):
        expr = op('+', var('x'), num('1'))
        assert expr.representacao_latex() == 'x + 1'

    def test_latex_fracao(self):
        expr = op('/', var('x'), num('2'))
        assert expr.representacao_latex() == '\\frac{x}{2}'

    def test_latex_potencia(self):
        expr = op('^', var('x'), num('2'))
        assert expr.representacao_latex() == '{x}^{2}'

    def test_latex_sin(self):
        expr = func('sin', var('x'))
        assert '\\sin' in expr.representacao_latex()

    def test_latex_exp(self):
        expr = func('exp', var('x'))
        assert 'e^' in expr.representacao_latex()


# ============================================================
# Testes de avaliacao
# ============================================================

class TestAvaliacao:
    def test_avaliar_numero(self):
        assert num('3').avaliar({}) == 3.0

    def test_avaliar_variavel(self):
        assert var('x').avaliar({'x': 5}) == 5.0

    def test_avaliar_soma(self):
        expr = op('+', var('x'), num('2'))
        assert expr.avaliar({'x': 3}) == 5.0

    def test_avaliar_produto(self):
        expr = op('*', var('x'), num('3'))
        assert expr.avaliar({'x': 4}) == 12.0

    def test_avaliar_potencia(self):
        expr = op('^', var('x'), num('2'))
        assert expr.avaliar({'x': 5}) == 25.0

    def test_avaliar_sin(self):
        expr = func('sin', num('0'))
        assert abs(expr.avaliar({}) - 0.0) < 1e-10

    def test_avaliar_exp(self):
        expr = func('exp', num('0'))
        assert abs(expr.avaliar({}) - 1.0) < 1e-10
