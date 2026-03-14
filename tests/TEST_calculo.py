"""Testes para o modulo de calculo simbolico."""

import math
import pytest
from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.derivada import derivar, derivar_ordem, derivada_implicita, simplificar_no
from engine.calculo.integral import integrar
from engine.calculo.limite import limite, limite_lateral, limite_infinito
from engine.calculo.aplicacoes import (
    taxa_variacao, encontrar_criticos, encontrar_inflexao,
    teorema_valor_medio, esboco_curva, comprimento_arco,
    volume_disco,
)
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


# ============================================================
# Testes de derivada — funcoes inversas trigonometricas
# ============================================================

class TestDerivadaInversas:
    def test_derivada_arcsin(self):
        # d/dx(arcsin(x)) = 1/sqrt(1-x^2)
        expr = func('arcsin', var('x'))
        result = derivar(expr, 'x')
        for val in [0.0, 0.3, 0.5, -0.3]:
            expected = 1.0 / math.sqrt(1 - val**2)
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-8, f"x={val}: esperado {expected}, obteve {got}"

    def test_derivada_arccos(self):
        # d/dx(arccos(x)) = -1/sqrt(1-x^2)
        expr = func('arccos', var('x'))
        result = derivar(expr, 'x')
        for val in [0.0, 0.3, 0.5, -0.3]:
            expected = -1.0 / math.sqrt(1 - val**2)
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-8, f"x={val}: esperado {expected}, obteve {got}"

    def test_derivada_arctan(self):
        # d/dx(arctan(x)) = 1/(1+x^2)
        expr = func('arctan', var('x'))
        result = derivar(expr, 'x')
        for val in [0.0, 1.0, 2.0, -1.0]:
            expected = 1.0 / (1 + val**2)
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-8, f"x={val}: esperado {expected}, obteve {got}"


# ============================================================
# Testes de derivada de ordem superior
# ============================================================

class TestDerivadaOrdemSuperior:
    def test_segunda_derivada_x_cubo(self):
        # d²/dx²(x³) = 6x
        expr = op('^', var('x'), num('3'))
        result = derivar_ordem(expr, 'x', 2)
        for val in [1, 2, -1, 0.5]:
            expected = 6 * val
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-8, f"x={val}: esperado {expected}, obteve {got}"

    def test_terceira_derivada_x_cubo(self):
        # d³/dx³(x³) = 6
        expr = op('^', var('x'), num('3'))
        result = derivar_ordem(expr, 'x', 3)
        got = result.avaliar({'x': 7})
        assert abs(got - 6.0) < 1e-8

    def test_segunda_derivada_sin(self):
        # d²/dx²(sin(x)) = -sin(x)
        expr = func('sin', var('x'))
        result = derivar_ordem(expr, 'x', 2)
        for val in [0, 1, math.pi / 4]:
            expected = -math.sin(val)
            got = result.avaliar({'x': val})
            assert abs(got - expected) < 1e-8


# ============================================================
# Testes de derivada implicita
# ============================================================

class TestDerivadaImplicita:
    def test_circulo(self):
        # x² + y² - 1 = 0 => dy/dx = -x/y
        F = op('+', op('+', op('^', var('x'), num('2')), op('^', var('y'), num('2'))), num('-1'))
        result = derivada_implicita(F, 'x', 'y')
        # Em (x=0.6, y=0.8): dy/dx = -0.6/0.8 = -0.75
        got = result.avaliar({'x': 0.6, 'y': 0.8})
        assert abs(got - (-0.75)) < 1e-8


# ============================================================
# Testes de integracao por substituicao
# ============================================================

class TestIntegracaoSubstituicao:
    def test_2x_cos_x2(self):
        # ∫ 2x·cos(x²) dx = sin(x²) + C
        expr = op('*', op('*', num('2'), var('x')), func('cos', op('^', var('x'), num('2'))))
        result = integrar(expr, 'x')
        # Avaliar: sin(x²) em x=1 => sin(1) ≈ 0.8414...
        got = result.avaliar({'x': 1, 'C': 0})
        expected = math.sin(1)
        assert abs(got - expected) < 1e-6, f"esperado {expected}, obteve {got}"


# ============================================================
# Testes de integracao por partes
# ============================================================

class TestIntegracaoPartes:
    def test_x_exp_x(self):
        # ∫ x·e^x dx = x·e^x - e^x + C = e^x(x-1) + C
        expr = op('*', var('x'), func('exp', var('x')))
        result = integrar(expr, 'x')
        # Em x=1: e^1(1-1) = 0, em x=2: e^2(2-1) = e^2
        got = result.avaliar({'x': 1, 'C': 0})
        expected = 1 * math.exp(1) - math.exp(1)  # = 0
        assert abs(got - expected) < 1e-6, f"x=1: esperado {expected}, obteve {got}"

        got2 = result.avaliar({'x': 2, 'C': 0})
        expected2 = 2 * math.exp(2) - math.exp(2)  # = e^2
        assert abs(got2 - expected2) < 1e-6, f"x=2: esperado {expected2}, obteve {got2}"


# ============================================================
# Testes de limite lateral
# ============================================================

class TestLimiteLateral:
    def test_limite_lateral_1_sobre_x_direita(self):
        # lim x->0+ (1/x) = inf
        expr = op('/', num('1'), var('x'))
        result = limite_lateral(expr, 'x', '0', 'direita')
        assert result == 'inf'

    def test_limite_lateral_1_sobre_x_esquerda(self):
        # lim x->0- (1/x) = -inf
        expr = op('/', num('1'), var('x'))
        result = limite_lateral(expr, 'x', '0', 'esquerda')
        assert result == '-inf'

    def test_limite_lateral_convergente(self):
        # lim x->1+ (x^2) = 1
        expr = op('^', var('x'), num('2'))
        result = limite_lateral(expr, 'x', '1', 'direita')
        assert result == '1'


# ============================================================
# Testes de limite no infinito
# ============================================================

class TestLimiteInfinito:
    def test_limite_1_sobre_x_infinito(self):
        # lim x->+inf (1/x) = 0
        expr = op('/', num('1'), var('x'))
        result = limite_infinito(expr, 'x', '+inf')
        assert result == '0'

    def test_limite_1_sobre_x_menos_infinito(self):
        # lim x->-inf (1/x) = 0
        expr = op('/', num('1'), var('x'))
        result = limite_infinito(expr, 'x', '-inf')
        assert result == '0'

    def test_limite_x2_infinito(self):
        # lim x->+inf (x^2) = inf
        expr = op('^', var('x'), num('2'))
        result = limite_infinito(expr, 'x', '+inf')
        assert result == 'inf'

    def test_limite_via_funcao_principal(self):
        # limite() com valor='inf' deve redirecionar
        expr = op('/', num('1'), var('x'))
        result = limite(expr, 'x', 'inf')
        assert result == '0'


# ============================================================
# Testes de maximos e minimos
# ============================================================

class TestMaximosMinimos:
    def test_x3_menos_3x(self):
        # f(x) = x³ - 3x
        # f'(x) = 3x² - 3 = 0 => x = ±1
        # f''(1) = 6 > 0 => minimo em x=1, f(1) = -2
        # f''(-1) = -6 < 0 => maximo em x=-1, f(-1) = 2
        expr = op('-', op('^', var('x'), num('3')), op('*', num('3'), var('x')))
        criticos = encontrar_criticos(expr, 'x', (-5, 5))

        tipos = {c['tipo'] for c in criticos}
        assert 'maximo' in tipos
        assert 'minimo' in tipos

        for c in criticos:
            if c['tipo'] == 'minimo':
                assert abs(c['x'] - 1.0) < 1e-4
                assert abs(c['fx'] - (-2.0)) < 1e-4
            if c['tipo'] == 'maximo':
                assert abs(c['x'] - (-1.0)) < 1e-4
                assert abs(c['fx'] - 2.0) < 1e-4


# ============================================================
# Testes de pontos de inflexao
# ============================================================

class TestInflexao:
    def test_x3_menos_3x(self):
        # f(x) = x³ - 3x
        # f''(x) = 6x = 0 => x = 0
        # f(0) = 0
        expr = op('-', op('^', var('x'), num('3')), op('*', num('3'), var('x')))
        inflexoes = encontrar_inflexao(expr, 'x', (-5, 5))

        assert len(inflexoes) >= 1
        # Deve ter inflexao em x = 0
        encontrou = False
        for inf in inflexoes:
            if abs(inf['x']) < 1e-4:
                encontrou = True
                assert abs(inf['fx']) < 1e-4
        assert encontrou, f"Nao encontrou inflexao em x=0. Inflexoes: {inflexoes}"

    def test_x4(self):
        # f(x) = x^4 => f''(x) = 12x^2 = 0 em x=0
        # Mas f''(x) >= 0 sempre, entao NAO eh inflexao (nao muda concavidade)
        expr = op('^', var('x'), num('4'))
        inflexoes = encontrar_inflexao(expr, 'x', (-5, 5))
        # x=0 nao deve ser inflexao
        for inf in inflexoes:
            assert abs(inf['x']) > 1e-4, "x^4 nao deve ter inflexao em x=0"


# ============================================================
# Testes do teorema do valor medio
# ============================================================

class TestTeoremaValorMedio:
    def test_x2_em_0_2(self):
        # f(x) = x², [0, 2]
        # f(2)-f(0) / (2-0) = 4/2 = 2
        # f'(x) = 2x = 2 => x = 1
        expr = op('^', var('x'), num('2'))
        cs = teorema_valor_medio(expr, 'x', 0, 2)
        assert len(cs) >= 1
        assert any(abs(c - 1.0) < 1e-4 for c in cs)


# ============================================================
# Testes de esboco de curva
# ============================================================

class TestEsbocoCurva:
    def test_x3_menos_3x(self):
        expr = op('-', op('^', var('x'), num('3')), op('*', num('3'), var('x')))
        esboco = esboco_curva(expr, 'x', (-5, 5))

        assert 'zeros' in esboco
        assert 'criticos' in esboco
        assert 'inflexao' in esboco

        # Deve ter zeros em aproximadamente -sqrt(3), 0, sqrt(3)
        assert len(esboco['zeros']) >= 3


# ============================================================
# Testes de volume e comprimento de arco
# ============================================================

class TestVolumeComprimento:
    def test_volume_disco_x(self):
        # V = pi * ∫_0^1 x^2 dx = pi * 1/3 ≈ 1.0472
        expr = var('x')
        vol = volume_disco(expr, 'x', 0, 1)
        expected = math.pi / 3
        assert abs(vol - expected) < 1e-3, f"esperado {expected}, obteve {vol}"

    def test_comprimento_arco_reta(self):
        # f(x) = x em [0, 1] => L = sqrt(2)
        expr = var('x')
        comp = comprimento_arco(expr, 'x', 0, 1)
        expected = math.sqrt(2)
        assert abs(comp - expected) < 1e-3, f"esperado {expected}, obteve {comp}"
