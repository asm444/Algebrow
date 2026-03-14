"""Testes para o modulo de numeros complexos e analise complexa."""

import math
import pytest
from engine.complexos.complexo import Complexo, euler, de_moivre
from engine.complexos.funcao_complexa import cauchy_riemann
from engine.complexos.transformada_laplace import (
    transformada_laplace, transformada_inversa, TABELA_LAPLACE,
)


# ======================================================================
# Aritmetica de complexos
# ======================================================================

class TestAritmeticaComplexa:

    def test_soma(self):
        z1 = Complexo('3', '4')
        z2 = Complexo('1', '2')
        r = z1.somar(z2)
        assert r == Complexo('4', '6')

    def test_soma_com_negativos(self):
        z1 = Complexo('3', '-1')
        z2 = Complexo('-2', '5')
        r = z1.somar(z2)
        assert r == Complexo('1', '4')

    def test_subtracao(self):
        z1 = Complexo('5', '3')
        z2 = Complexo('2', '1')
        r = z1.subtrair(z2)
        assert r == Complexo('3', '2')

    def test_multiplicacao(self):
        # (3+2i)(1+4i) = 3+12i+2i+8i^2 = 3+14i-8 = -5+14i
        z1 = Complexo('3', '2')
        z2 = Complexo('1', '4')
        r = z1.multiplicar(z2)
        assert r == Complexo('-5', '14')

    def test_multiplicacao_por_zero(self):
        z1 = Complexo('3', '4')
        z2 = Complexo('0', '0')
        r = z1.multiplicar(z2)
        assert r == Complexo('0', '0')

    def test_multiplicacao_i_vezes_i(self):
        # i * i = -1
        z1 = Complexo('0', '1')
        r = z1.multiplicar(z1)
        assert r == Complexo('-1', '0')

    def test_divisao(self):
        # (4+2i)/(1+i) = (4+2i)(1-i)/(1+1) = (4-4i+2i-2i^2)/2 = (6-2i)/2 = 3-i
        z1 = Complexo('4', '2')
        z2 = Complexo('1', '1')
        r = z1.dividir(z2)
        assert r == Complexo('3', '-1')

    def test_divisao_por_zero(self):
        z1 = Complexo('1', '0')
        z2 = Complexo('0', '0')
        with pytest.raises(ZeroDivisionError):
            z1.dividir(z2)


# ======================================================================
# Conjugado, modulo, argumento
# ======================================================================

class TestPropriedades:

    def test_conjugado(self):
        z = Complexo('3', '4')
        c = z.conjugado()
        assert c == Complexo('3', '-4')

    def test_conjugado_de_real(self):
        z = Complexo('5', '0')
        c = z.conjugado()
        assert c == Complexo('5', '0')

    def test_conjugado_de_imaginario_negativo(self):
        z = Complexo('0', '-3')
        c = z.conjugado()
        assert c == Complexo('0', '3')

    def test_modulo(self):
        z = Complexo('3', '4')
        m = float(z.modulo())
        assert abs(m - 5.0) < 1e-10

    def test_modulo_unitario(self):
        z = Complexo('1', '0')
        m = float(z.modulo())
        assert abs(m - 1.0) < 1e-10

    def test_argumento_eixo_real_positivo(self):
        z = Complexo('1', '0')
        arg = float(z.argumento())
        assert abs(arg - 0.0) < 1e-10

    def test_argumento_eixo_imaginario_positivo(self):
        z = Complexo('0', '1')
        arg = float(z.argumento())
        assert abs(arg - math.pi / 2) < 1e-10

    def test_argumento_eixo_real_negativo(self):
        z = Complexo('-1', '0')
        arg = float(z.argumento())
        assert abs(arg - math.pi) < 1e-10


# ======================================================================
# Forma polar
# ======================================================================

class TestFormaPolar:

    def test_forma_polar_3_4(self):
        z = Complexo('3', '4')
        r, theta = z.forma_polar()
        assert abs(float(r) - 5.0) < 1e-10
        assert abs(float(theta) - math.atan2(4, 3)) < 1e-10

    def test_forma_polar_unitario(self):
        z = Complexo('1', '0')
        r, theta = z.forma_polar()
        assert abs(float(r) - 1.0) < 1e-10
        assert abs(float(theta)) < 1e-10


# ======================================================================
# Raizes n-esimas
# ======================================================================

class TestRaizesNesimas:

    def test_raizes_cubicas_de_1(self):
        """As 3 raizes cubicas de 1 sao: 1, e^(2pi*i/3), e^(4pi*i/3)."""
        z = Complexo('1', '0')
        raizes = z.raizes_nesimas(3)
        assert len(raizes) == 3

        # Raiz 0 deve ser 1 + 0i
        assert abs(float(raizes[0].real) - 1.0) < 1e-9
        assert abs(float(raizes[0].imag)) < 1e-9

        # Verificar que z^3 = 1 para todas as raizes
        for raiz in raizes:
            z3 = raiz.potencia(3)
            assert abs(float(z3.real) - 1.0) < 1e-8
            assert abs(float(z3.imag)) < 1e-8

    def test_raizes_quadradas_de_menos_1(self):
        """As raizes quadradas de -1 sao i e -i."""
        z = Complexo('-1', '0')
        raizes = z.raizes_nesimas(2)
        assert len(raizes) == 2

        # Uma deve ser i, a outra -i
        reais = sorted([float(r.imag) for r in raizes])
        assert abs(reais[0] - (-1.0)) < 1e-9
        assert abs(reais[1] - 1.0) < 1e-9


# ======================================================================
# Euler
# ======================================================================

class TestEuler:

    def test_euler_i_pi(self):
        """e^(i*pi) = -1 + 0i (identidade de Euler)."""
        z = euler(str(math.pi))
        assert abs(float(z.real) - (-1.0)) < 1e-10
        assert abs(float(z.imag)) < 1e-10

    def test_euler_zero(self):
        """e^(i*0) = 1."""
        z = euler('0')
        assert abs(float(z.real) - 1.0) < 1e-10
        assert abs(float(z.imag)) < 1e-10

    def test_euler_pi_sobre_2(self):
        """e^(i*pi/2) = i."""
        z = euler(str(math.pi / 2))
        assert abs(float(z.real)) < 1e-10
        assert abs(float(z.imag) - 1.0) < 1e-10


# ======================================================================
# De Moivre
# ======================================================================

class TestDeMoivre:

    def test_de_moivre_cubo(self):
        """(1 * e^(i*pi/3))^3 = 1 * e^(i*pi) = -1."""
        resultado = de_moivre('1', str(math.pi / 3), 3)
        assert abs(float(resultado.real) - (-1.0)) < 1e-10
        assert abs(float(resultado.imag)) < 1e-10

    def test_de_moivre_quadrado(self):
        """(2 * e^(i*pi/4))^2 = 4 * e^(i*pi/2) = 4i."""
        resultado = de_moivre('2', str(math.pi / 4), 2)
        assert abs(float(resultado.real)) < 1e-9
        assert abs(float(resultado.imag) - 4.0) < 1e-9


# ======================================================================
# Cauchy-Riemann
# ======================================================================

class TestCauchyRiemann:

    def test_holomorfa_u_x2_y2_v_2xy(self):
        """u = x^2 - y^2, v = 2xy e holomorfa (f(z) = z^2).
        du/dx = 2x, dv/dy = 2x ✓
        du/dy = -2y, -dv/dx = -2y ✓
        """
        from engine.calculo.arvore import num, var, op

        x = var('x')
        y = var('y')
        # u = x^2 - y^2
        u = op('-', op('^', x, num('2')), op('^', y, num('2')))
        # v = 2*x*y
        v = op('*', op('*', num('2'), x), y)

        satisfaz, detalhes, historico = cauchy_riemann(u, v)
        assert satisfaz is True
        assert detalhes['condicao_1'] is True
        assert detalhes['condicao_2'] is True

    def test_nao_holomorfa(self):
        """u = x^2 + y^2, v = 0 nao e holomorfa.
        du/dx = 2x, dv/dy = 0 — diferentes!
        """
        from engine.calculo.arvore import num, var, op

        x = var('x')
        y = var('y')
        # u = x^2 + y^2
        u = op('+', op('^', x, num('2')), op('^', y, num('2')))
        # v = 0
        v = num('0')

        satisfaz, detalhes, historico = cauchy_riemann(u, v)
        assert satisfaz is False


# ======================================================================
# Transformada de Laplace
# ======================================================================

class TestTransformadaLaplace:

    def test_laplace_sin_wt(self):
        resultado, hist = transformada_laplace('sin(3t)')
        assert '3' in resultado
        assert 's^2' in resultado or 's^2+9' in resultado

    def test_laplace_cos_wt(self):
        resultado, hist = transformada_laplace('cos(2t)')
        assert 's' in resultado
        assert '4' in resultado  # w^2 = 4

    def test_laplace_exp(self):
        resultado, hist = transformada_laplace('e^(5t)')
        assert 's' in resultado
        assert '5' in resultado

    def test_laplace_1(self):
        resultado, hist = transformada_laplace('1')
        assert resultado == '1/s'

    def test_laplace_t(self):
        resultado, hist = transformada_laplace('t')
        assert resultado == '1/s^2'

    def test_laplace_t_cubo(self):
        resultado, hist = transformada_laplace('t^3')
        # L{t^3} = 3!/s^4 = 6/s^4
        assert '6' in resultado
        assert 's^4' in resultado


# ======================================================================
# Transformada inversa
# ======================================================================

class TestTransformadaInversa:

    def test_inversa_1_sobre_s(self):
        resultado, hist = transformada_inversa('1/s')
        assert resultado == '1'

    def test_inversa_1_sobre_s2(self):
        resultado, hist = transformada_inversa('1/s^2')
        assert resultado == 't'

    def test_inversa_exponencial(self):
        resultado, hist = transformada_inversa('1/(s-3)')
        assert 'e^' in resultado
        assert '3' in resultado

    def test_inversa_seno(self):
        resultado, hist = transformada_inversa('5/(s^2+25)')
        assert 'sin' in resultado
        assert '5' in resultado

    def test_inversa_cosseno(self):
        resultado, hist = transformada_inversa('s/(s^2+9)')
        assert 'cos' in resultado
        assert '3' in resultado


# ======================================================================
# Representacao
# ======================================================================

class TestRepresentacao:

    def test_latex_puro_real(self):
        z = Complexo('5', '0')
        assert z.representacao_latex() == '5'

    def test_latex_puro_imaginario(self):
        z = Complexo('0', '3')
        assert z.representacao_latex() == '3i'

    def test_latex_completo(self):
        z = Complexo('2', '3')
        latex = z.representacao_latex()
        assert '2' in latex
        assert '3' in latex
        assert 'i' in latex

    def test_repr(self):
        z = Complexo('1', '2')
        assert 'Complexo' in repr(z)

    def test_eq_e_hash(self):
        z1 = Complexo('3', '4')
        z2 = Complexo('3', '4')
        assert z1 == z2
        assert hash(z1) == hash(z2)

    def test_neq(self):
        z1 = Complexo('3', '4')
        z2 = Complexo('3', '5')
        assert z1 != z2
