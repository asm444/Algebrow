"""Testes para o módulo de Polinômios."""

import pytest
from engine.algebra.polinomio import Polinomio


class TestCriacaoELatex:
    def test_polinomio_grau2(self):
        p = Polinomio({'2': '3', '1': '2', '0': '-1'})
        assert p.grau() == 2
        assert p.coeficiente('2') == '3'
        assert p.coeficiente('1') == '2'
        assert p.coeficiente('0') == '-1'

    def test_latex_grau2(self):
        p = Polinomio({'2': '3', '1': '2', '0': '-1'})
        assert p.representacao_latex() == '3x^{2} + 2x - 1'

    def test_latex_coeficiente_1(self):
        p = Polinomio({'2': '1', '1': '1', '0': '1'})
        assert p.representacao_latex() == 'x^{2} + x + 1'

    def test_latex_coeficiente_negativo_1(self):
        p = Polinomio({'2': '-1', '0': '1'})
        assert p.representacao_latex() == '-x^{2} + 1'

    def test_polinomio_zero(self):
        p = Polinomio({'0': '0'})
        assert p.representacao_latex() == '0'
        assert p.grau() == 0

    def test_coeficiente_ausente_retorna_zero(self):
        p = Polinomio({'2': '1'})
        assert p.coeficiente('1') == '0'
        assert p.coeficiente('0') == '0'

    def test_repr(self):
        p = Polinomio({'1': '2', '0': '3'})
        assert 'Polinomio' in repr(p)


class TestSomaSubtracaoMultiplicacao:
    def test_soma_polinomios(self):
        p1 = Polinomio({'2': '1', '1': '2', '0': '3'})
        p2 = Polinomio({'2': '2', '1': '-1', '0': '1'})
        resultado = p1.somar(p2)
        assert resultado.coeficiente('2') == '3'
        assert resultado.coeficiente('1') == '1'
        assert resultado.coeficiente('0') == '4'

    def test_subtracao_polinomios(self):
        p1 = Polinomio({'2': '3', '1': '2', '0': '1'})
        p2 = Polinomio({'2': '1', '1': '2', '0': '1'})
        resultado = p1.subtrair(p2)
        assert resultado.coeficiente('2') == '2'
        assert resultado.coeficiente('1') == '0'
        assert resultado.coeficiente('0') == '0'

    def test_multiplicacao_polinomios(self):
        # (x + 1)(x - 1) = x² - 1
        p1 = Polinomio({'1': '1', '0': '1'})
        p2 = Polinomio({'1': '1', '0': '-1'})
        resultado = p1.multiplicar(p2)
        assert resultado.coeficiente('2') == '1'
        assert resultado.coeficiente('1') == '0'
        assert resultado.coeficiente('0') == '-1'

    def test_multiplicacao_por_escalar(self):
        p1 = Polinomio({'2': '1', '1': '2', '0': '3'})
        p2 = Polinomio({'0': '2'})
        resultado = p1.multiplicar(p2)
        assert resultado.coeficiente('2') == '2'
        assert resultado.coeficiente('1') == '4'
        assert resultado.coeficiente('0') == '6'


class TestAvaliar:
    def test_avaliar_inteiro(self):
        # 2x² + 3x + 1, x=2 -> 2*4 + 3*2 + 1 = 15
        p = Polinomio({'2': '2', '1': '3', '0': '1'})
        assert p.avaliar('2') == '15'

    def test_avaliar_zero(self):
        p = Polinomio({'2': '1', '1': '-3', '0': '2'})
        # x² - 3x + 2 em x=1 -> 1 - 3 + 2 = 0
        assert p.avaliar('1') == '0'

    def test_avaliar_negativo(self):
        # x + 3 em x=-3 -> 0
        p = Polinomio({'1': '1', '0': '3'})
        assert p.avaliar('-3') == '0'


class TestDivisaoLonga:
    def test_divisao_exata(self):
        # (x² - 1) / (x - 1) = (x + 1), resto 0
        dividendo = Polinomio({'2': '1', '0': '-1'})
        divisor = Polinomio({'1': '1', '0': '-1'})
        quociente, resto = dividendo.dividir(divisor)
        assert quociente.coeficiente('1') == '1'
        assert quociente.coeficiente('0') == '1'
        assert resto._eh_zero()

    def test_divisao_com_resto(self):
        # (x² + 1) / (x - 1) = (x + 1), resto 2
        dividendo = Polinomio({'2': '1', '0': '1'})
        divisor = Polinomio({'1': '1', '0': '-1'})
        quociente, resto = dividendo.dividir(divisor)
        assert quociente.coeficiente('1') == '1'
        assert quociente.coeficiente('0') == '1'
        assert resto.coeficiente('0') == '2'

    def test_divisao_grau3(self):
        # (x³ - 6x² + 11x - 6) / (x - 1) = (x² - 5x + 6), resto 0
        dividendo = Polinomio({'3': '1', '2': '-6', '1': '11', '0': '-6'})
        divisor = Polinomio({'1': '1', '0': '-1'})
        quociente, resto = dividendo.dividir(divisor)
        assert quociente.coeficiente('2') == '1'
        assert quociente.coeficiente('1') == '-5'
        assert quociente.coeficiente('0') == '6'
        assert resto._eh_zero()

    def test_divisao_por_zero_levanta_excecao(self):
        p = Polinomio({'1': '1'})
        zero = Polinomio({'0': '0'})
        with pytest.raises(ZeroDivisionError):
            p.dividir(zero)


class TestRaizesRacionais:
    def test_raizes_grau2(self):
        # x² - 3x + 2 = (x-1)(x-2), raízes 1 e 2
        p = Polinomio({'2': '1', '1': '-3', '0': '2'})
        raizes = p.raizes_racionais()
        assert '1' in raizes
        assert '2' in raizes

    def test_raizes_grau3(self):
        # x³ - 6x² + 11x - 6 = (x-1)(x-2)(x-3)
        p = Polinomio({'3': '1', '2': '-6', '1': '11', '0': '-6'})
        raizes = p.raizes_racionais()
        assert '1' in raizes
        assert '2' in raizes
        assert '3' in raizes

    def test_raiz_zero(self):
        # x² - x = x(x-1), raízes 0 e 1
        p = Polinomio({'2': '1', '1': '-1'})
        raizes = p.raizes_racionais()
        assert '0' in raizes
        assert '1' in raizes


class TestFatoracao:
    def test_fatorar_grau2_bhaskara(self):
        # x² - 5x + 6 = (x-2)(x-3)
        p = Polinomio({'2': '1', '1': '-5', '0': '6'})
        fatores = p.fatorar()
        # Deve ter 2 fatores lineares
        assert len(fatores) == 2
        # Multiplicando os fatores deve dar o polinômio original
        produto = fatores[0].multiplicar(fatores[1])
        assert produto == p

    def test_fatorar_grau2_raiz_dupla(self):
        # x² - 2x + 1 = (x-1)²
        p = Polinomio({'2': '1', '1': '-2', '0': '1'})
        fatores = p.fatorar()
        assert len(fatores) == 2
        produto = fatores[0].multiplicar(fatores[1])
        assert produto == p

    def test_fatorar_grau2_irredutivel(self):
        # x² + 1 (sem raízes reais)
        p = Polinomio({'2': '1', '0': '1'})
        fatores = p.fatorar()
        assert len(fatores) == 1
        assert fatores[0] == p

    def test_fatorar_grau3(self):
        # x³ - 6x² + 11x - 6 = (x-1)(x-2)(x-3)
        p = Polinomio({'3': '1', '2': '-6', '1': '11', '0': '-6'})
        fatores = p.fatorar()
        assert len(fatores) == 3
        produto = fatores[0].multiplicar(fatores[1]).multiplicar(fatores[2])
        assert produto == p

    def test_fatorar_grau1(self):
        p = Polinomio({'1': '2', '0': '-3'})
        fatores = p.fatorar()
        assert len(fatores) == 1
        assert fatores[0] == p


class TestIgualdade:
    def test_polinomios_iguais(self):
        p1 = Polinomio({'2': '1', '1': '2', '0': '3'})
        p2 = Polinomio({'2': '1', '1': '2', '0': '3'})
        assert p1 == p2

    def test_polinomios_diferentes(self):
        p1 = Polinomio({'2': '1', '0': '1'})
        p2 = Polinomio({'2': '1', '0': '-1'})
        assert p1 != p2

    def test_igualdade_com_outro_tipo(self):
        p = Polinomio({'1': '1'})
        assert p != 42
