"""Testes para o modulo de geometria diferencial."""

import math
import pytest

from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.derivada import simplificar_no
from engine.geometria_diferencial.auxiliares import (
    produto_escalar, produto_vetorial, norma,
)
from engine.geometria_diferencial.curvas import CurvaParametrica
from engine.geometria_diferencial.superficies import SuperficieParametrica


# ======================================================================
# Helpers
# ======================================================================

def avaliar_no(no: NoExpressao, variaveis: dict) -> float:
    return no.avaliar(variaveis)


def avaliar_vetor(v: list[NoExpressao], variaveis: dict) -> list[float]:
    return [avaliar_no(c, variaveis) for c in v]


# ======================================================================
# Produto escalar simbolico
# ======================================================================

class TestProdutoEscalar:
    def test_basico(self):
        """(1,2,3) . (4,5,6) = 32"""
        a = [num('1'), num('2'), num('3')]
        b = [num('4'), num('5'), num('6')]
        resultado = produto_escalar(a, b)
        assert abs(avaliar_no(resultado, {}) - 32.0) < 1e-9

    def test_ortogonal(self):
        """(1,0,0) . (0,1,0) = 0"""
        a = [num('1'), num('0'), num('0')]
        b = [num('0'), num('1'), num('0')]
        resultado = produto_escalar(a, b)
        assert abs(avaliar_no(resultado, {})) < 1e-9

    def test_simbolico(self):
        """(t, 0) . (0, t) = 0"""
        t = var('t')
        a = [t, num('0')]
        b = [num('0'), t]
        resultado = produto_escalar(a, b)
        assert abs(avaliar_no(resultado, {'t': 3.0})) < 1e-9


# ======================================================================
# Produto vetorial simbolico
# ======================================================================

class TestProdutoVetorial:
    def test_basico(self):
        """(1,0,0) x (0,1,0) = (0,0,1)"""
        a = [num('1'), num('0'), num('0')]
        b = [num('0'), num('1'), num('0')]
        resultado = produto_vetorial(a, b)
        vals = avaliar_vetor(resultado, {})
        assert abs(vals[0]) < 1e-9
        assert abs(vals[1]) < 1e-9
        assert abs(vals[2] - 1.0) < 1e-9

    def test_anticomutatividade(self):
        """a x b = -(b x a)"""
        a = [num('1'), num('2'), num('3')]
        b = [num('4'), num('5'), num('6')]
        ab = produto_vetorial(a, b)
        ba = produto_vetorial(b, a)
        vals_ab = avaliar_vetor(ab, {})
        vals_ba = avaliar_vetor(ba, {})
        for i in range(3):
            assert abs(vals_ab[i] + vals_ba[i]) < 1e-9

    def test_simbolico(self):
        """(t, 0, 1) x (0, t, 0) avaliado em t=2"""
        t = var('t')
        a = [t, num('0'), num('1')]
        b = [num('0'), t, num('0')]
        resultado = produto_vetorial(a, b)
        # (0*0 - 1*t, 1*0 - t*0, t*t - 0*0) = (-t, 0, t^2)
        vals = avaliar_vetor(resultado, {'t': 2.0})
        assert abs(vals[0] - (-2.0)) < 1e-9
        assert abs(vals[1]) < 1e-9
        assert abs(vals[2] - 4.0) < 1e-9


# ======================================================================
# Curva: circulo unitario alpha(t) = (cos(t), sin(t))
# ======================================================================

class TestCirculoUnitario:
    @pytest.fixture
    def circulo(self):
        t = var('t')
        return CurvaParametrica([func('cos', t), func('sin', t)], 't')

    def test_curvatura_circulo(self, circulo):
        """Curvatura do circulo unitario deve ser 1."""
        kappa, hist = circulo.curvatura()
        # Avaliar em varios pontos
        for t_val in [0.0, 0.5, 1.0, 2.0, math.pi]:
            val = avaliar_no(kappa, {'t': t_val})
            assert abs(val - 1.0) < 1e-6, f'kappa({t_val}) = {val}, esperado 1.0'

    def test_vetor_tangente(self, circulo):
        """T do circulo unitario em t=0 deve ser (0, 1)."""
        T = circulo.vetor_tangente()
        vals = avaliar_vetor(T, {'t': 0.0})
        # alpha'(0) = (-sin(0), cos(0)) = (0, 1), normalizado = (0, 1)
        assert abs(vals[0] - 0.0) < 1e-6
        assert abs(vals[1] - 1.0) < 1e-6

    def test_comprimento_arco(self, circulo):
        """|alpha'(t)| do circulo unitario deve ser 1."""
        integrando = circulo.comprimento_arco_formula()
        for t_val in [0.0, 1.0, math.pi]:
            val = avaliar_no(integrando, {'t': t_val})
            assert abs(val - 1.0) < 1e-6

    def test_representacao_latex(self, circulo):
        latex = circulo.representacao_latex()
        assert '\\alpha' in latex
        assert 't' in latex


# ======================================================================
# Curva: parabola alpha(t) = (t, t^2)
# ======================================================================

class TestParabola:
    @pytest.fixture
    def parabola(self):
        t = var('t')
        return CurvaParametrica([t, op('^', t, num('2'))], 't')

    def test_curvatura_em_t0(self, parabola):
        """Curvatura de (t, t^2) em t=0 deve ser 2."""
        # alpha' = (1, 2t), alpha'' = (0, 2)
        # kappa = |1*2 - 2t*0| / (1 + 4t^2)^(3/2) = 2 / 1 = 2 em t=0
        kappa, hist = parabola.curvatura()
        val = avaliar_no(kappa, {'t': 0.0})
        assert abs(val - 2.0) < 1e-6


# ======================================================================
# Curva: reta alpha(t) = (t, 0)
# ======================================================================

class TestReta:
    def test_comprimento_arco_reta(self):
        """Integrando de alpha(t) = (t, 0) deve ser 1."""
        t = var('t')
        reta = CurvaParametrica([t, num('0')], 't')
        integrando = reta.comprimento_arco_formula()
        val = avaliar_no(integrando, {'t': 5.0})
        assert abs(val - 1.0) < 1e-6


# ======================================================================
# Helice alpha(t) = (cos(t), sin(t), t)
# ======================================================================

class TestHelice:
    @pytest.fixture
    def helice(self):
        t = var('t')
        return CurvaParametrica([func('cos', t), func('sin', t), t], 't')

    def test_curvatura_helice(self, helice):
        """Curvatura da helice (cos t, sin t, t): kappa = 1/2."""
        # alpha' = (-sin t, cos t, 1), alpha'' = (-cos t, -sin t, 0)
        # |alpha' x alpha''| = |(sin t, -cos t, ...) | -> kappa = 1/2
        kappa, hist = helice.curvatura()
        for t_val in [0.0, 1.0, 2.0]:
            val = avaliar_no(kappa, {'t': t_val})
            assert abs(val - 0.5) < 1e-5, f'kappa({t_val}) = {val}, esperado 0.5'

    def test_torcao_helice(self, helice):
        """Torcao da helice (cos t, sin t, t): tau = 1/2."""
        tau, hist = helice.torcao()
        for t_val in [0.0, 1.0, 2.0]:
            val = avaliar_no(tau, {'t': t_val})
            assert abs(val - 0.5) < 1e-5, f'tau({t_val}) = {val}, esperado 0.5'

    def test_frenet_serret(self, helice):
        """Frenet-Serret da helice retorna T, N, B, kappa, tau."""
        T, N, B, kappa, tau, hist = helice.frenet_serret()
        assert len(T) == 3
        assert len(N) == 3
        assert B is not None
        assert len(B) == 3


# ======================================================================
# Superficie: esfera unitaria
# sigma(u,v) = (sin(u)cos(v), sin(u)sin(v), cos(u))
# ======================================================================

class TestEsfera:
    @pytest.fixture
    def esfera(self):
        u = var('u')
        v = var('v')
        x = op('*', func('sin', u), func('cos', v))
        y = op('*', func('sin', u), func('sin', v))
        z = func('cos', u)
        return SuperficieParametrica([x, y, z], ['u', 'v'])

    def test_primeira_forma_fundamental(self, esfera):
        """Para a esfera unitaria: E = 1, F = 0, G = sin^2(u)."""
        E, F, G, hist = esfera.primeira_forma_fundamental()

        # Testar em u=pi/4, v=pi/3
        env = {'u': math.pi / 4, 'v': math.pi / 3}
        E_val = avaliar_no(E, env)
        F_val = avaliar_no(F, env)
        G_val = avaliar_no(G, env)

        assert abs(E_val - 1.0) < 1e-5, f'E = {E_val}, esperado 1.0'
        assert abs(F_val) < 1e-5, f'F = {F_val}, esperado 0.0'
        assert abs(G_val - math.sin(math.pi / 4) ** 2) < 1e-5, \
            f'G = {G_val}, esperado {math.sin(math.pi / 4) ** 2}'

    def test_curvatura_gaussiana(self, esfera):
        """Curvatura gaussiana da esfera unitaria: K = 1."""
        K, hist = esfera.curvatura_gaussiana()

        # Testar em varios pontos (evitar polos onde sin(u)=0)
        for u_val, v_val in [(math.pi / 4, 0.5), (math.pi / 3, 1.0),
                              (math.pi / 6, 2.0)]:
            env = {'u': u_val, 'v': v_val}
            K_val = avaliar_no(K, env)
            assert abs(K_val - 1.0) < 1e-3, \
                f'K(u={u_val}, v={v_val}) = {K_val}, esperado 1.0'

    def test_representacao_latex(self, esfera):
        latex = esfera.representacao_latex()
        assert '\\sigma' in latex


# ======================================================================
# Norma
# ======================================================================

class TestNorma:
    def test_norma_basica(self):
        """|(3, 4)| = 5"""
        v = [num('3'), num('4')]
        resultado = norma(v)
        assert abs(avaliar_no(resultado, {}) - 5.0) < 1e-9

    def test_norma_unitaria(self):
        """|(1, 0, 0)| = 1"""
        v = [num('1'), num('0'), num('0')]
        resultado = norma(v)
        assert abs(avaliar_no(resultado, {}) - 1.0) < 1e-9
