"""Testes de integração ponta a ponta: LaTeX → Solver → resultado.

Testa o fluxo completo que o frontend usa: o usuário digita LaTeX,
o sistema converte, detecta, roteia e resolve.
"""
import pytest
from engine.solver import Solver


class TestIntegracaoDerivadas:
    """Derivadas via LaTeX."""

    def test_derivada_x3(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\frac{d}{dx} x^3')
        # d/dx(x^3) = 3x^2
        assert r.latex_resultado  # não vazio
        assert r.historico is not None

    def test_derivada_sin(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\frac{d}{dx} \sin(x)')
        assert r.latex_resultado

    def test_derivada_composta(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\frac{d}{dx}\left(x^2 + \sin(x)\right)')
        assert r.latex_resultado

    def test_derivada_segunda(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\frac{d^2}{dx^2} x^4')
        assert r.latex_resultado


class TestIntegracaoIntegrais:
    """Integrais via LaTeX."""

    def test_integral_indefinida_x2(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\int x^2 \, dx')
        assert 'x' in r.latex_resultado
        assert 'C' in r.latex_resultado

    def test_integral_definida_x2(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\int_0^1 x^2 \, dx')
        # 1/3 ≈ 0.333...
        val = float(r.valor_numerico)
        assert abs(val - 1/3) < 1e-6

    def test_integral_sin_0_pi(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\int_0^{\pi} \sin(x) \, dx')
        val = float(r.valor_numerico)
        assert abs(val - 2.0) < 1e-6

    def test_integral_definida_simetrica(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\int_{-1}^{1} x^3 \, dx')
        val = float(r.valor_numerico)
        assert abs(val) < 1e-6  # função ímpar em intervalo simétrico = 0

    def test_integral_indefinida_sin(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\int \sin(x) \, dx')
        assert 'cos' in r.latex_resultado


class TestIntegracaoLimites:
    """Limites via LaTeX."""

    def test_limite_sinx_sobre_x(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\lim_{x \to 0} \frac{\sin(x)}{x}')
        assert r.valor_numerico == '1'

    def test_limite_no_infinito(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\lim_{x \to \infty} \frac{1}{x}')
        assert r.valor_numerico == '0'

    def test_limite_polinomio(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\lim_{x \to 2} x^2')
        assert r.valor_numerico == '4'


class TestIntegracaoBasico:
    """Expressões básicas (regressão)."""

    def test_fracao(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\frac{3}{4} + \frac{1}{4}')
        assert r.latex_resultado == '1'

    def test_raiz(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\sqrt{144}')
        assert '12' in r.latex_resultado

    def test_log(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'\log_{2}{8}')
        assert '3' in r.latex_resultado

    def test_potencia(self):
        s = Solver(verbosidade=0)
        r = s.resolver(r'2^{10}')
        assert r.valor_numerico == '1024'

    def test_sintaxe_simples(self):
        s = Solver(verbosidade=0)
        r = s.resolver('sqrt(216)')
        assert '6' in r.latex_resultado


class TestIntegracaoTrig:
    """Funções trigonométricas no LaTeX."""

    def test_sin_cos_soma(self):
        s = Solver(verbosidade=0)
        # sin(x) + cos(x) é passthrough, não é operação de cálculo
        r = s.resolver(r'\sin(x) + \cos(x)')
        # Deve pelo menos não dar erro
        assert r is not None


class TestIntegracaoVerbosidade:
    """Testa que os passos são gerados."""

    def test_derivada_com_passos(self):
        s = Solver(verbosidade=3)
        r = s.resolver(r'\frac{d}{dx} x^3')
        passos = r.historico.serializar()
        assert len(passos) > 0

    def test_integral_com_passos(self):
        s = Solver(verbosidade=3)
        r = s.resolver(r'\int x^2 \, dx')
        passos = r.historico.serializar()
        assert len(passos) > 0
