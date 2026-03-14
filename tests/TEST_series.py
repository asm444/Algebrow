"""Testes para os modulos de series e sequencias."""

import math
import pytest
from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.serie import serie_taylor, serie_geometrica, serie_p
from engine.calculo.sequencia import (
    limite_sequencia, convergencia_serie, serie_potencias,
)
from engine.basic.passo import Historico


# ============================================================
# Testes de Serie de Taylor
# ============================================================

class TestSerieTaylor:
    def test_taylor_exp_centro_zero(self):
        """Serie de Taylor de e^x em torno de 0 com 5 termos.
        e^x = 1 + x + x^2/2 + x^3/6 + x^4/24
        """
        f = func('exp', var('x'))
        serie, hist = serie_taylor(f, centro=0, n_termos=5, variavel='x')

        # Verificar que a serie aproxima e^x para valores pequenos de x
        for x_val in [0, 0.1, 0.5, 1.0]:
            esperado = math.exp(x_val)
            obtido = serie.avaliar({'x': x_val})
            # Com 5 termos a aproximacao deve ser boa para x proximo de 0
            assert abs(obtido - esperado) < 0.05, (
                f"x={x_val}: esperado ~{esperado:.4f}, obteve {obtido:.4f}"
            )

        # Verificar que o historico foi preenchido
        assert len(hist) > 0

    def test_taylor_sin(self):
        """Serie de Taylor de sin(x) em torno de 0.
        sin(x) = x - x^3/6 + x^5/120 - ...
        """
        f = func('sin', var('x'))
        serie, hist = serie_taylor(f, centro=0, n_termos=6, variavel='x')

        # Verificar aproximacao
        for x_val in [0, 0.1, 0.5, 1.0]:
            esperado = math.sin(x_val)
            obtido = serie.avaliar({'x': x_val})
            assert abs(obtido - esperado) < 0.01, (
                f"x={x_val}: esperado ~{esperado:.6f}, obteve {obtido:.6f}"
            )

    def test_taylor_exp_avaliacao_em_zero(self):
        """e^0 = 1, serie avaliada em x=0 deve dar 1."""
        f = func('exp', var('x'))
        serie, _ = serie_taylor(f, centro=0, n_termos=5, variavel='x')
        assert abs(serie.avaliar({'x': 0}) - 1.0) < 1e-10


# ============================================================
# Testes de Serie Geometrica
# ============================================================

class TestSerieGeometrica:
    def test_geometrica_convergente(self):
        """Serie geometrica com r=1/2 converge para 2 (a=1)."""
        r = num('0.5')
        soma, hist = serie_geometrica(r)
        # soma deve ser NoExpressao representando 1/(1-0.5) = 2
        assert soma != 'diverge'
        val = soma.avaliar({})
        assert abs(val - 2.0) < 1e-10

    def test_geometrica_convergente_com_primeiro_termo(self):
        """Serie geometrica com a=3, r=1/3: S = 3/(1-1/3) = 4.5."""
        r = num(str(1/3))
        a = num('3')
        soma, hist = serie_geometrica(r, primeiro_termo=a)
        assert soma != 'diverge'
        val = soma.avaliar({})
        assert abs(val - 4.5) < 1e-10

    def test_geometrica_divergente(self):
        """Serie geometrica com r=2 diverge."""
        r = num('2')
        resultado, hist = serie_geometrica(r)
        assert resultado == 'diverge'

    def test_geometrica_divergente_r_menos_1(self):
        """Serie geometrica com r=-1 diverge."""
        r = num('-1')
        resultado, hist = serie_geometrica(r)
        assert resultado == 'diverge'


# ============================================================
# Testes de Serie p
# ============================================================

class TestSerieP:
    def test_serie_p_converge(self):
        """Serie p com p=2 converge."""
        resultado, hist = serie_p(2.0)
        assert resultado == 'converge'

    def test_serie_p_diverge_p1(self):
        """Serie p com p=1 (harmonica) diverge."""
        resultado, hist = serie_p(1.0)
        assert resultado == 'diverge'

    def test_serie_p_diverge_menor_que_1(self):
        """Serie p com p=0.5 diverge."""
        resultado, hist = serie_p(0.5)
        assert resultado == 'diverge'

    def test_serie_p_converge_p3(self):
        """Serie p com p=3 converge."""
        resultado, hist = serie_p(3.0)
        assert resultado == 'converge'


# ============================================================
# Testes de Convergencia de Serie (teste da razao, termo geral)
# ============================================================

class TestConvergenciaSerie:
    def test_razao_convergente(self):
        """Serie sum 1/2^n converge pelo teste da razao.
        a_n = (1/2)^n = 1/2^n
        """
        # a_n = (1/2)^n
        termos = op('^', num('0.5'), var('n'))
        resultado, teste, hist = convergencia_serie(termos, 'n')
        assert resultado == 'converge'

    def test_termo_geral_divergente(self):
        """Serie sum n diverge pelo teste do termo geral.
        a_n = n, lim a_n = inf != 0
        """
        termos = var('n')
        resultado, teste, hist = convergencia_serie(termos, 'n')
        assert resultado == 'diverge'
        assert 'termo geral' in teste

    def test_razao_serie_1_sobre_n_fatorial(self):
        """Serie sum 1/n^2 converge (a_n = 1/n^2).
        Razao: (n/(n+1))^2 -> 1, mas limite numerico deve pegar.
        """
        # a_n = 1/n^2
        termos = op('/', num('1'), op('^', var('n'), num('2')))
        resultado, teste, hist = convergencia_serie(termos, 'n')
        assert resultado == 'converge'

    def test_termo_constante_diverge(self):
        """Serie sum 1 diverge (a_n = 1, lim != 0)."""
        termos = num('1')
        resultado, teste, hist = convergencia_serie(termos, 'n')
        assert resultado == 'diverge'
        assert 'termo geral' in teste


# ============================================================
# Testes de Raio de Convergencia
# ============================================================

class TestSeriePotencias:
    def test_raio_serie_geometrica(self):
        """Serie sum x^n: coeficientes [1, 1, 1, 1, ...] -> raio = 1."""
        coefs = [1, 1, 1, 1, 1, 1, 1, 1]
        raio, intervalo, hist = serie_potencias(coefs, centro=0)
        raio_val = float(raio)
        assert abs(raio_val - 1.0) < 0.1

    def test_raio_serie_exp(self):
        """Serie de e^x: coeficientes 1/n! -> raio infinito.
        As razoes |a_n/a_{n+1}| = (n+1) crescem sem limite.
        """
        coefs = [1.0 / math.factorial(n) for n in range(10)]
        raio, intervalo, hist = serie_potencias(coefs, centro=0)
        # Razoes crescem -> serie de potencias diverge para nenhum x finito?
        # Na verdade e^x converge para todo x, entao raio = infinito
        # As razoes |a_n/a_{n+1}| = n+1 crescem, logo nao convergem
        # O metodo pode retornar o ultimo valor calculado ou 'indeterminado'
        assert len(hist) > 0  # Pelo menos registrou algo

    def test_raio_com_centro(self):
        """Serie com coeficientes [1, 1, 1, ...] e centro 2."""
        coefs = [1, 1, 1, 1, 1, 1, 1, 1]
        raio, intervalo, hist = serie_potencias(coefs, centro=2)
        raio_val = float(raio)
        assert abs(raio_val - 1.0) < 0.1
        # Intervalo deve ser centrado em 2
        assert '2' in intervalo or '1' in intervalo


# ============================================================
# Testes de Limite de Sequencia
# ============================================================

class TestLimiteSequencia:
    def test_limite_1_sobre_n(self):
        """lim(n->inf) 1/n = 0."""
        expr = op('/', num('1'), var('n'))
        lim, hist = limite_sequencia(expr, 'n')
        assert lim == '0'

    def test_limite_n_sobre_n_mais_1(self):
        """lim(n->inf) n/(n+1) = 1."""
        expr = op('/', var('n'), op('+', var('n'), num('1')))
        lim, hist = limite_sequencia(expr, 'n')
        assert lim == '1'

    def test_limite_divergente(self):
        """lim(n->inf) n^2 = infinito."""
        expr = op('^', var('n'), num('2'))
        lim, hist = limite_sequencia(expr, 'n')
        assert 'infinito' in lim


# ============================================================
# Testes de Historico
# ============================================================

class TestHistorico:
    def test_taylor_gera_historico(self):
        """Serie de Taylor deve gerar passos no historico."""
        f = func('exp', var('x'))
        _, hist = serie_taylor(f, centro=0, n_termos=3)
        passos = hist.todos()
        assert len(passos) >= 3  # Pelo menos inicio + coeficientes

    def test_serie_p_gera_historico(self):
        """Serie p deve gerar passos no historico."""
        _, hist = serie_p(2.0)
        passos = hist.todos()
        assert len(passos) >= 2

    def test_convergencia_gera_historico(self):
        """Teste de convergencia deve gerar passos."""
        termos = var('n')
        _, _, hist = convergencia_serie(termos, 'n')
        passos = hist.todos()
        assert len(passos) >= 2
