"""Testes para o módulo de funções especiais."""
import math
import pytest

from engine.funcoes_especiais.gamma import gamma, beta, stirling, gamma_incompleta
from engine.funcoes_especiais.bessel import bessel_j, bessel_zeros, bessel_recorrencia
from engine.funcoes_especiais.legendre import legendre_p, ortogonalidade_legendre
from engine.funcoes_especiais.hermite_laguerre import hermite, laguerre


# ── Gamma ──────────────────────────────────────────────

class TestGamma:
    def test_gamma_5(self):
        valor, hist = gamma(5)
        assert valor == 24.0
        assert len(hist) > 0

    def test_gamma_meio(self):
        valor, hist = gamma(0.5)
        assert abs(valor - math.sqrt(math.pi)) < 1e-8

    def test_gamma_1(self):
        valor, hist = gamma(1)
        assert valor == 1.0


# ── Beta ───────────────────────────────────────────────

class TestBeta:
    def test_beta_2_3(self):
        valor, hist = beta(2, 3)
        esperado = 1.0 / 12.0
        assert abs(valor - esperado) < 1e-10


# ── Stirling ───────────────────────────────────────────

class TestStirling:
    def test_stirling_10(self):
        aprox, hist = stirling(10)
        real = math.factorial(10)
        erro = abs(aprox - real) / real
        assert erro < 0.01  # <1% de erro


# ── Bessel ─────────────────────────────────────────────

class TestBessel:
    def test_j0_zero(self):
        valor, _, hist = bessel_j(0, 0)
        assert abs(valor - 1.0) < 1e-10

    def test_j1_zero(self):
        valor, _, hist = bessel_j(1, 0)
        assert abs(valor - 0.0) < 1e-10

    def test_zeros_j0(self):
        zeros = bessel_zeros(0, n_zeros=2)
        assert abs(zeros[0] - 2.4048) < 0.001
        assert abs(zeros[1] - 5.5201) < 0.001


# ── Legendre ───────────────────────────────────────────

class TestLegendre:
    def test_p0(self):
        coefs, hist = legendre_p(0)
        assert coefs == [1.0]

    def test_p1(self):
        coefs, hist = legendre_p(1)
        assert coefs == [0.0, 1.0]

    def test_p2(self):
        coefs, hist = legendre_p(2)
        # P_2 = (3x²-1)/2 → coefs = [-0.5, 0, 1.5]
        assert abs(coefs[0] - (-0.5)) < 1e-10
        assert abs(coefs[1] - 0.0) < 1e-10
        assert abs(coefs[2] - 1.5) < 1e-10

    def test_ortogonalidade_p1_p2(self):
        resultado, hist = ortogonalidade_legendre(1, 2)
        # ∫ P_1·P_2 dx = 0
        assert "0" in resultado or abs(float(resultado.split("=")[1].split("(")[0].strip())) < 1e-8


# ── Hermite ────────────────────────────────────────────

class TestHermite:
    def test_h0(self):
        coefs, hist = hermite(0)
        assert coefs == [1.0]

    def test_h1(self):
        coefs, hist = hermite(1)
        assert coefs == [0.0, 2.0]

    def test_h2(self):
        coefs, hist = hermite(2)
        # H_2 = 4x² - 2
        assert abs(coefs[0] - (-2.0)) < 1e-10
        assert abs(coefs[1] - 0.0) < 1e-10
        assert abs(coefs[2] - 4.0) < 1e-10


# ── Laguerre ───────────────────────────────────────────

class TestLaguerre:
    def test_l0(self):
        coefs, hist = laguerre(0)
        assert coefs == [1.0]

    def test_l1(self):
        coefs, hist = laguerre(1)
        # L_1 = 1 - x
        assert abs(coefs[0] - 1.0) < 1e-10
        assert abs(coefs[1] - (-1.0)) < 1e-10
