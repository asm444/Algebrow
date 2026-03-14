"""Testes para módulos de Fourier, Cálculo Variacional e Equações Integrais."""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.fourier.serie_fourier import (
    coeficientes_fourier, serie_fourier_latex, serie_fourier_senos,
    serie_fourier_cossenos, parseval,
)
from engine.fourier.transformada_fourier import (
    transformada_fourier, transformada_inversa,
    prop_linearidade, prop_deslocamento, prop_convolucao,
)
from engine.variacional.euler_lagrange import (
    euler_lagrange, braquisticrona, geodesica_plano,
    geodesica_esfera, principio_hamilton,
)
from engine.integral_eq.fredholm_volterra import (
    fredholm_2especie, volterra_2especie, serie_neumann,
)
from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.basic.passo import Historico


# ==================== Fourier ====================

class TestOndaQuadrada:
    """Série de Fourier de onda quadrada: f(x) = 1 para 0<x<pi, -1 para -pi<x<0.

    Coeficientes conhecidos:
    - a0 = 0
    - an = 0 para todo n
    - bn = 4/(n*pi) para n ímpar, 0 para n par
    """

    def test_coeficientes_onda_quadrada(self):
        # Extensão ímpar de f(x) = 1 em [0, pi]:
        # bn = 2/pi * integral_0^pi sin(n*x) dx = 4/(n*pi) para n ímpar, 0 para n par
        bn, hist = serie_fourier_senos('1', math.pi, n_termos=10)

        for n in range(1, 11):
            esperado = 4 / (n * math.pi) if n % 2 != 0 else 0.0
            assert abs(bn[n - 1] - esperado) < 1e-4, (
                f'b_{n}: esperado {esperado:.6f}, obtido {bn[n - 1]:.6f}'
            )

    def test_coeficientes_completos_funcao_par(self):
        # f(x) = x^2 em [-pi, pi] -> a0 = pi^2/3, an = 4*(-1)^n/n^2, bn = 0
        a0, an, bn, hist = coeficientes_fourier('x^2', math.pi, n_termos=5)

        esperado_a0 = math.pi ** 2 / 3
        assert abs(a0 - esperado_a0) < 1e-3, f'a0: esperado {esperado_a0}, obtido {a0}'

        # bn devem ser ~0 (função par)
        for n in range(5):
            assert abs(bn[n]) < 1e-6, f'b_{n + 1} deveria ser ~0, obtido {bn[n]}'

        assert isinstance(hist, Historico)

    def test_historico_retornado(self):
        _, _, _, hist = coeficientes_fourier('x', math.pi, n_termos=3)
        assert len(hist) > 0


class TestSerieFourierLatex:
    def test_gera_latex(self):
        a0, an, bn, _ = coeficientes_fourier('x', math.pi, n_termos=3)
        latex = serie_fourier_latex(a0, an, bn, math.pi)
        assert 'f(x)' in latex
        assert '\\approx' in latex


class TestSerieFourierCossenos:
    def test_cossenos_funcao_par(self):
        # f(x) = 1 em [0, L] -> a0 = 2, an = 0 para n >= 1
        an, hist = serie_fourier_cossenos('1', math.pi, n_termos=5)
        assert abs(an[0] - 2.0) < 1e-4
        for n in range(1, 6):
            assert abs(an[n]) < 1e-6


class TestParseval:
    def test_parseval_onda_quadrada(self):
        bn, _ = serie_fourier_senos('1', math.pi, n_termos=50)
        an = [0.0] * 50
        a0 = 0.0
        valor, hist = parseval(a0, an, bn)

        # sum(bn^2) = 16/pi^2 * pi^2/8 = 2
        assert abs(valor - 2.0) < 0.05, f'Parseval: esperado ~2.0, obtido {valor}'
        assert isinstance(hist, Historico)


# ==================== Transformada de Fourier ====================

class TestTransformadaFourier:
    def test_transformada_retorna_valores(self):
        # Gaussiana: f(x) = exp(-x^2), F(0) = sqrt(pi)
        omegas = [0.0, 1.0, 2.0]
        valores, hist = transformada_fourier('exp(-x^2)', omegas)
        assert len(valores) == 3
        assert abs(valores[0].real - math.sqrt(math.pi)) < 0.1
        assert abs(valores[0].imag) < 0.1

    def test_propriedades_retornam_string(self):
        assert len(prop_linearidade()) > 0
        assert len(prop_deslocamento()) > 0
        assert len(prop_convolucao()) > 0


# ==================== Euler-Lagrange ====================

class TestEulerLagrange:
    def test_geodesica_plano_y_linha_linha_zero(self):
        """F = sqrt(1 + y'^2) -> Euler-Lagrange implica y'' = 0."""
        yp = var("y'")
        F = func('sqrt', op('+', num('1'), op('^', yp, num('2'))))

        equacao, hist = euler_lagrange(F, y_var='y', yp_var="y'", x_var='x')

        # dF/dy = 0 pois F não contém y. d/dx(dF/dy') = 0 pois não depende de x.
        # Resultado: 0 - 0 = 0
        assert equacao.tipo == 'numero' and float(equacao.valor) == 0.0, (
            f'Esperado 0, obtido {equacao.representacao_latex()}'
        )
        assert isinstance(hist, Historico)
        assert len(hist) > 0

    def test_geodesica_plano_funcao(self):
        """geodesica_plano() retorna descricao com reta."""
        latex, hist = geodesica_plano()
        assert 'reta' in latex.lower() or 'y = ax + b' in latex
        assert isinstance(hist, Historico)


class TestBraquisticrona:
    def test_retorna_cicloide(self):
        latex, hist = braquisticrona()
        assert 'cicl' in latex.lower() or 'sin' in latex
        assert isinstance(hist, Historico)
        assert len(hist) > 0


class TestGeodesicaEsfera:
    def test_retorna_grande_circulo(self):
        latex, hist = geodesica_esfera()
        assert 'rculo' in latex.lower() or 'cos' in latex
        assert isinstance(hist, Historico)


class TestPrincipioHamilton:
    def test_retorna_euler_lagrange(self):
        latex, hist = principio_hamilton()
        assert 'Euler-Lagrange' in latex or 'frac' in latex
        assert isinstance(hist, Historico)


# ==================== Equações Integrais ====================

class TestFredholm:
    def test_kernel_separavel(self):
        """Fredholm com kernel K(x,t) = x*t, f(x) = 1, lambda = 0.5, em [0, 1].
        Solução: phi(x) = 1 + 0.3*x
        """
        solucao, hist = fredholm_2especie('x*t', '1', 0.5, 0.0, 1.0, n_pontos=30)

        for x_val, phi_val in solucao:
            esperado = 1.0 + 0.3 * x_val
            assert abs(phi_val - esperado) < 0.05, (
                f'x={x_val:.3f}: esperado {esperado:.4f}, obtido {phi_val:.4f}'
            )
        assert isinstance(hist, Historico)

    def test_kernel_constante(self):
        """K(x,t) = 1, f(x) = 1, lambda = 0.1, [0, 1].
        phi(x) = 10/9
        """
        solucao, hist = fredholm_2especie('1', '1', 0.1, 0.0, 1.0, n_pontos=20)
        esperado = 10.0 / 9.0
        for _, phi_val in solucao:
            assert abs(phi_val - esperado) < 0.05


class TestVolterra:
    def test_volterra_simples(self):
        """phi(x) = 1 + integral_0^x phi(t)dt -> phi(x) = e^x."""
        solucao, hist = volterra_2especie('1', '1', 1.0, 0.0, 1.0, n_pontos=100)

        for x_val, phi_val in solucao:
            esperado = math.exp(x_val)
            assert abs(phi_val - esperado) < 0.1, (
                f'x={x_val:.3f}: esperado {esperado:.4f}, obtido {phi_val:.4f}'
            )


class TestSerieNeumann:
    def test_retorna_iteracoes(self):
        iteracoes, hist = serie_neumann('x*t', '1', 0.5, 0.0, 1.0, n_iter=3)
        assert len(iteracoes) == 4  # phi_0 + 3 termos
        assert '\\phi_0' in iteracoes[0]
        assert isinstance(hist, Historico)
