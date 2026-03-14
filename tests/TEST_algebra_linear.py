"""Testes do módulo de Álgebra Linear."""

import pytest
from engine.algebra_linear.matriz import Matriz
from engine.algebra_linear.determinante import determinante
from engine.algebra_linear.gauss import eliminacao_gaussiana
from engine.algebra_linear.autovalor import autovalores_2x2


# ==================== Criação e LaTeX ====================

class TestMatrizCriacao:
    def test_criacao_basica(self):
        m = Matriz([['1', '2'], ['3', '4']])
        assert m.linhas == 2
        assert m.colunas == 2
        assert m.elemento(0, 0) == '1'
        assert m.elemento(1, 1) == '4'

    def test_criacao_3x3(self):
        m = Matriz([['1', '0', '0'], ['0', '1', '0'], ['0', '0', '1']])
        assert m.linhas == 3
        assert m.colunas == 3

    def test_latex_inteiros(self):
        m = Matriz([['1', '2'], ['3', '4']])
        latex = m.representacao_latex()
        assert '\\begin{pmatrix}' in latex
        assert '\\end{pmatrix}' in latex
        assert '1 & 2' in latex
        assert '3 & 4' in latex

    def test_latex_fracoes(self):
        m = Matriz([['1/2', '3'], ['4', '5/6']])
        latex = m.representacao_latex()
        assert '\\frac{1}{2}' in latex
        assert '\\frac{5}{6}' in latex


# ==================== Transposta ====================

class TestTransposta:
    def test_transposta_2x2(self):
        m = Matriz([['1', '2'], ['3', '4']])
        t = m.transposta()
        assert t.dados == [['1', '3'], ['2', '4']]

    def test_transposta_2x3(self):
        m = Matriz([['1', '2', '3'], ['4', '5', '6']])
        t = m.transposta()
        assert t.linhas == 3
        assert t.colunas == 2
        assert t.dados == [['1', '4'], ['2', '5'], ['3', '6']]


# ==================== Soma e Subtração ====================

class TestSomaSubtracao:
    def test_soma_2x2(self):
        a = Matriz([['1', '2'], ['3', '4']])
        b = Matriz([['5', '6'], ['7', '8']])
        c = a.somar(b)
        assert c.dados == [['6', '8'], ['10', '12']]

    def test_subtracao_2x2(self):
        a = Matriz([['5', '6'], ['7', '8']])
        b = Matriz([['1', '2'], ['3', '4']])
        c = a.subtrair(b)
        assert c.dados == [['4', '4'], ['4', '4']]

    def test_soma_dimensoes_incompativeis(self):
        a = Matriz([['1', '2'], ['3', '4']])
        b = Matriz([['1', '2', '3']])
        with pytest.raises(ValueError):
            a.somar(b)

    def test_soma_fracoes(self):
        a = Matriz([['1/2', '1/3']])
        b = Matriz([['1/2', '2/3']])
        c = a.somar(b)
        assert c.dados == [['1', '1']]


# ==================== Multiplicação ====================

class TestMultiplicacao:
    def test_escalar(self):
        m = Matriz([['1', '2'], ['3', '4']])
        r = m.multiplicar_escalar('2')
        assert r.dados == [['2', '4'], ['6', '8']]

    def test_multiplicacao_2x2(self):
        a = Matriz([['1', '2'], ['3', '4']])
        b = Matriz([['5', '6'], ['7', '8']])
        c = a.multiplicar(b)
        # [1*5+2*7, 1*6+2*8] = [19, 22]
        # [3*5+4*7, 3*6+4*8] = [43, 50]
        assert c.dados == [['19', '22'], ['43', '50']]

    def test_multiplicacao_identidade(self):
        a = Matriz([['1', '2'], ['3', '4']])
        i = Matriz([['1', '0'], ['0', '1']])
        c = a.multiplicar(i)
        assert c == a

    def test_multiplicacao_dimensoes_incompativeis(self):
        a = Matriz([['1', '2']])
        b = Matriz([['1', '2']])
        with pytest.raises(ValueError):
            a.multiplicar(b)

    def test_multiplicacao_retangular(self):
        # 2x3 * 3x1 = 2x1
        a = Matriz([['1', '2', '3'], ['4', '5', '6']])
        b = Matriz([['1'], ['2'], ['3']])
        c = a.multiplicar(b)
        assert c.linhas == 2
        assert c.colunas == 1
        # [1*1+2*2+3*3] = [14]
        # [4*1+5*2+6*3] = [32]
        assert c.dados == [['14'], ['32']]


# ==================== Igualdade ====================

class TestIgualdade:
    def test_iguais(self):
        a = Matriz([['1', '2'], ['3', '4']])
        b = Matriz([['1', '2'], ['3', '4']])
        assert a == b

    def test_diferentes(self):
        a = Matriz([['1', '2'], ['3', '4']])
        b = Matriz([['1', '2'], ['3', '5']])
        assert a != b


# ==================== Determinante ====================

class TestDeterminante:
    def test_det_2x2(self):
        m = Matriz([['1', '2'], ['3', '4']])
        valor, hist = determinante(m)
        # det = 1*4 - 2*3 = 4 - 6 = -2
        assert valor == '-2'

    def test_det_2x2_identidade(self):
        m = Matriz([['1', '0'], ['0', '1']])
        valor, hist = determinante(m)
        assert valor == '1'

    def test_det_3x3(self):
        m = Matriz([['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']])
        valor, hist = determinante(m)
        # Matriz singular, det = 0
        assert valor == '0'

    def test_det_3x3_nao_singular(self):
        m = Matriz([['2', '1', '3'], ['1', '0', '1'], ['0', '1', '2']])
        valor, hist = determinante(m)
        # det = 2*(0*2 - 1*1) - 1*(1*2 - 1*0) + 3*(1*1 - 0*0)
        #     = 2*(-1) - 1*(2) + 3*(1) = -2 - 2 + 3 = -1
        assert valor == '-1'

    def test_det_nao_quadrada_erro(self):
        m = Matriz([['1', '2', '3'], ['4', '5', '6']])
        with pytest.raises(ValueError):
            determinante(m)

    def test_det_historico(self):
        m = Matriz([['1', '2'], ['3', '4']])
        _, hist = determinante(m)
        assert len(hist) > 0


# ==================== Eliminação de Gauss ====================

class TestGauss:
    def test_sistema_determinado_2x2(self):
        # x + y = 3
        # 2x - y = 0
        # Solução: x = 1, y = 2
        m = Matriz([['1', '1'], ['2', '-1']])
        b = ['3', '0']
        solucoes, classificacao, hist = eliminacao_gaussiana(m, b)
        assert classificacao == 'determinado'
        assert solucoes[0] == '1'
        assert solucoes[1] == '2'

    def test_sistema_determinado_3x3(self):
        # x + y + z = 6
        # 2x + y - z = 1
        # x - y + z = 2
        # Solução: x = 1, y = 2, z = 3
        m = Matriz([['1', '1', '1'], ['2', '1', '-1'], ['1', '-1', '1']])
        b = ['6', '1', '2']
        solucoes, classificacao, hist = eliminacao_gaussiana(m, b)
        assert classificacao == 'determinado'
        assert solucoes[0] == '1'
        assert solucoes[1] == '2'
        assert solucoes[2] == '3'

    def test_sistema_impossivel(self):
        # x + y = 1
        # x + y = 2  (contradição)
        m = Matriz([['1', '1'], ['1', '1']])
        b = ['1', '2']
        solucoes, classificacao, hist = eliminacao_gaussiana(m, b)
        assert classificacao == 'impossivel'
        assert solucoes == []

    def test_sistema_indeterminado(self):
        # x + y = 1
        # 2x + 2y = 2  (mesma equação)
        m = Matriz([['1', '1'], ['2', '2']])
        b = ['1', '2']
        solucoes, classificacao, hist = eliminacao_gaussiana(m, b)
        assert classificacao == 'indeterminado'

    def test_gauss_historico(self):
        m = Matriz([['1', '1'], ['2', '-1']])
        b = ['3', '0']
        _, _, hist = eliminacao_gaussiana(m, b)
        assert len(hist) > 0


# ==================== Autovalores ====================

class TestAutovalores:
    def test_autovalores_identidade(self):
        m = Matriz([['1', '0'], ['0', '1']])
        autovalores, hist = autovalores_2x2(m)
        # Autovalor duplo: lambda = 1
        assert len(autovalores) == 1
        assert autovalores[0].representacao_latex() == '1'

    def test_autovalores_diagonal(self):
        m = Matriz([['3', '0'], ['0', '5']])
        autovalores, hist = autovalores_2x2(m)
        # Autovalores: 3 e 5
        latex_vals = sorted([av.representacao_latex() for av in autovalores])
        assert '3' in latex_vals
        assert '5' in latex_vals

    def test_autovalores_2x2_geral(self):
        # A = [[4, 1], [2, 3]]
        # Polinômio: lambda^2 - 7*lambda + 10 = 0
        # delta = 49 - 40 = 9, raiz = 3
        # lambda = (7 +/- 3) / 2 => 5 e 2
        m = Matriz([['4', '1'], ['2', '3']])
        autovalores, hist = autovalores_2x2(m)
        latex_vals = sorted([av.representacao_latex() for av in autovalores])
        assert '2' in latex_vals
        assert '5' in latex_vals

    def test_autovalores_dimensao_errada(self):
        m = Matriz([['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']])
        with pytest.raises(ValueError):
            autovalores_2x2(m)

    def test_autovalores_historico(self):
        m = Matriz([['4', '1'], ['2', '3']])
        _, hist = autovalores_2x2(m)
        assert len(hist) > 0
