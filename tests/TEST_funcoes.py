"""Testes para o módulo de funções elementares."""

import pytest
from engine.funcoes.elementares import (
    FuncaoLinear,
    FuncaoQuadratica,
    FuncaoExponencial,
    FuncaoLogaritmica,
)


# ========== FuncaoLinear ==========

class TestFuncaoLinear:

    def test_avaliar_inteiros(self):
        f = FuncaoLinear('2', '3')
        assert f.avaliar('4') == '11'  # 2*4 + 3 = 11

    def test_avaliar_zero(self):
        f = FuncaoLinear('5', '-10')
        assert f.avaliar('2') == '0'  # 5*2 + (-10) = 0

    def test_avaliar_fracao(self):
        f = FuncaoLinear('1/2', '1')
        resultado = f.avaliar('4')
        assert resultado == '3'  # (1/2)*4 + 1 = 3

    def test_zeros(self):
        f = FuncaoLinear('2', '-6')
        assert f.zeros() == ['3']  # x = 6/2 = 3

    def test_zeros_fracao(self):
        f = FuncaoLinear('3', '1')
        zeros = f.zeros()
        # f(x) = 3x + 1 = 0 => x = -1/3
        assert zeros == ['-1/3']

    def test_zeros_constante(self):
        f = FuncaoLinear('0', '5')
        assert f.zeros() == []

    def test_inversa(self):
        f = FuncaoLinear('2', '4')
        inv = f.inversa()
        # f(x) = 2x + 4 => f⁻¹(x) = (1/2)x - 2
        assert inv.a == '1/2'
        assert inv.b == '-2'

    def test_inversa_constante_erro(self):
        f = FuncaoLinear('0', '5')
        with pytest.raises(ValueError):
            f.inversa()

    def test_latex(self):
        f = FuncaoLinear('2', '3')
        assert f.representacao_latex() == '2x + 3'

    def test_latex_negativo(self):
        f = FuncaoLinear('1', '-5')
        assert f.representacao_latex() == 'x - 5'

    def test_latex_coeficiente_1(self):
        f = FuncaoLinear('1', '0')
        assert f.representacao_latex() == 'x'

    def test_dominio(self):
        f = FuncaoLinear('2', '3')
        assert f.dominio() == '(-\u221e, +\u221e)'

    def test_imagem_constante(self):
        f = FuncaoLinear('0', '7')
        assert f.imagem() == '{7}'

    def test_imagem_nao_constante(self):
        f = FuncaoLinear('3', '1')
        assert f.imagem() == '(-\u221e, +\u221e)'


# ========== FuncaoQuadratica ==========

class TestFuncaoQuadratica:

    def test_avaliar(self):
        f = FuncaoQuadratica('1', '-5', '6')
        assert f.avaliar('2') == '0'  # 4 - 10 + 6 = 0
        assert f.avaliar('3') == '0'  # 9 - 15 + 6 = 0

    def test_avaliar_coeficientes(self):
        f = FuncaoQuadratica('2', '0', '-8')
        assert f.avaliar('2') == '0'  # 2*4 + 0 - 8 = 0

    def test_vertice(self):
        f = FuncaoQuadratica('1', '-4', '3')
        xv, yv = f.vertice()
        assert xv == '2'  # -(-4)/(2*1) = 2
        assert yv == '-1'  # 4 - 8 + 3 = -1

    def test_vertice_fracao(self):
        f = FuncaoQuadratica('2', '-2', '0')
        xv, yv = f.vertice()
        assert xv == '1/2'
        assert yv == '-1/2'  # 2*(1/4) - 2*(1/2) + 0 = 1/2 - 1 = -1/2

    def test_zeros_duas_raizes(self):
        f = FuncaoQuadratica('1', '-5', '6')
        z = f.zeros()
        assert len(z) == 2

    def test_zeros_raiz_dupla(self):
        f = FuncaoQuadratica('1', '-2', '1')
        z = f.zeros()
        assert len(z) == 1  # (x-1)² = 0

    def test_zeros_sem_raiz_real(self):
        f = FuncaoQuadratica('1', '0', '1')
        z = f.zeros()
        assert z == []  # x² + 1 = 0 sem raiz real

    def test_concavidade_cima(self):
        f = FuncaoQuadratica('2', '0', '0')
        assert f.concavidade == 'cima'

    def test_concavidade_baixo(self):
        f = FuncaoQuadratica('-3', '0', '0')
        assert f.concavidade == 'baixo'

    def test_dominio(self):
        f = FuncaoQuadratica('1', '0', '0')
        assert f.dominio() == '(-\u221e, +\u221e)'

    def test_latex(self):
        f = FuncaoQuadratica('1', '-3', '2')
        assert f.representacao_latex() == 'x^{2} - 3x + 2'

    def test_latex_coeficientes_unitarios(self):
        f = FuncaoQuadratica('-1', '1', '-1')
        latex = f.representacao_latex()
        assert latex == '-x^{2} + x - 1'


# ========== FuncaoExponencial ==========

class TestFuncaoExponencial:

    def test_avaliar_inteiro(self):
        f = FuncaoExponencial('1', '2')
        assert f.avaliar('3') == '8'  # 1 * 2^3 = 8

    def test_avaliar_com_coeficiente(self):
        f = FuncaoExponencial('3', '2')
        assert f.avaliar('2') == '12'  # 3 * 2^2 = 12

    def test_avaliar_expoente_zero(self):
        f = FuncaoExponencial('5', '3')
        assert f.avaliar('0') == '5'  # 5 * 3^0 = 5

    def test_avaliar_expoente_negativo(self):
        f = FuncaoExponencial('1', '2')
        resultado = f.avaliar('-1')
        assert resultado == '1/2'  # 1 * 2^(-1) = 1/2

    def test_dominio(self):
        f = FuncaoExponencial('1', '2')
        assert f.dominio() == '(-\u221e, +\u221e)'

    def test_imagem_positiva(self):
        f = FuncaoExponencial('1', '2')
        assert f.imagem() == '(0, +\u221e)'

    def test_imagem_negativa(self):
        f = FuncaoExponencial('-1', '2')
        assert f.imagem() == '(-\u221e, 0)'

    def test_assintotas(self):
        f = FuncaoExponencial('1', '2')
        assert f.assintotas() == {'horizontal': 'y = 0'}

    def test_base_invalida(self):
        with pytest.raises(ValueError):
            FuncaoExponencial('1', '1')  # base = 1 inválida
        with pytest.raises(ValueError):
            FuncaoExponencial('1', '-2')  # base negativa

    def test_latex(self):
        f = FuncaoExponencial('1', '2')
        assert f.representacao_latex() == '2^{x}'

    def test_latex_com_coeficiente(self):
        f = FuncaoExponencial('3', '2')
        assert f.representacao_latex() == '3 \\cdot 2^{x}'


# ========== FuncaoLogaritmica ==========

class TestFuncaoLogaritmica:

    def test_avaliar_base_potencia(self):
        f = FuncaoLogaritmica('1', '2')
        assert f.avaliar('8') == '3'  # log_2(8) = 3

    def test_avaliar_um(self):
        f = FuncaoLogaritmica('1', '10')
        assert f.avaliar('1') == '0'  # log(1) = 0

    def test_avaliar_com_coeficiente(self):
        f = FuncaoLogaritmica('2', '3')
        assert f.avaliar('9') == '4'  # 2 * log_3(9) = 2 * 2 = 4

    def test_avaliar_valor_negativo_erro(self):
        f = FuncaoLogaritmica('1', '2')
        with pytest.raises(ValueError):
            f.avaliar('-1')

    def test_zeros(self):
        f = FuncaoLogaritmica('1', '10')
        assert f.zeros() == ['1']

    def test_dominio(self):
        f = FuncaoLogaritmica('1', '2')
        assert f.dominio() == '(0, +\u221e)'

    def test_imagem(self):
        f = FuncaoLogaritmica('1', '2')
        assert f.imagem() == '(-\u221e, +\u221e)'

    def test_base_invalida(self):
        with pytest.raises(ValueError):
            FuncaoLogaritmica('1', '1')
        with pytest.raises(ValueError):
            FuncaoLogaritmica('1', '0')

    def test_latex(self):
        f = FuncaoLogaritmica('1', '2')
        assert f.representacao_latex() == '\\log_{2}{x}'

    def test_latex_com_coeficiente(self):
        f = FuncaoLogaritmica('3', '10')
        assert f.representacao_latex() == '3\\log_{10}{x}'
