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


# ============================================================
# Testes para SistemaLinear e Inequacao1Grau
# ============================================================

from engine.algebra.sistema import SistemaLinear
from engine.algebra.inequacao import Inequacao1Grau


class TestSistemaLinear:
    def test_sistema_2x2_determinado(self):
        # x + y = 5, x - y = 1 → x=3, y=2
        sistema = SistemaLinear(
            coeficientes=[['1', '1'], ['1', '-1']],
            constantes=['5', '1']
        )
        solucoes, classificacao, historico = sistema.resolver()
        assert classificacao == 'determinado'
        assert solucoes['x'] == '3'
        assert solucoes['y'] == '2'
        assert len(historico) > 0

    def test_sistema_2x2_impossivel(self):
        # x + y = 1, x + y = 2 → impossível
        sistema = SistemaLinear(
            coeficientes=[['1', '1'], ['1', '1']],
            constantes=['1', '2']
        )
        solucoes, classificacao, historico = sistema.resolver()
        assert classificacao == 'impossivel'
        assert solucoes == {}

    def test_sistema_2x2_indeterminado(self):
        # x + y = 2, 2x + 2y = 4 → indeterminado
        sistema = SistemaLinear(
            coeficientes=[['1', '1'], ['2', '2']],
            constantes=['2', '4']
        )
        solucoes, classificacao, historico = sistema.resolver()
        assert classificacao == 'indeterminado'
        assert solucoes == {}

    def test_sistema_3x3(self):
        # x + y + z = 6, 2x + y - z = 1, x - y + z = 2
        sistema = SistemaLinear(
            coeficientes=[['1', '1', '1'], ['2', '1', '-1'], ['1', '-1', '1']],
            constantes=['6', '1', '2']
        )
        solucoes, classificacao, historico = sistema.resolver()
        assert classificacao == 'determinado'
        # Verificar que as soluções satisfazem o sistema
        x, y, z = solucoes['x'], solucoes['y'], solucoes['z']
        # x + y + z = 6
        from engine.basic.operacoes_basicas import soma
        assert soma(soma(x, y), z) == '6'
        # 2x + y - z = 1
        from engine.basic.operacoes_basicas import diff, multi
        assert diff(soma(multi('2', x), y), z) == '1'
        # x - y + z = 2
        assert soma(diff(x, y), z) == '2'

    def test_sistema_2x2_com_fracoes(self):
        # 2x + 3y = 7, x - y = 1 → x=2, y=1
        sistema = SistemaLinear(
            coeficientes=[['2', '3'], ['1', '-1']],
            constantes=['7', '1']
        )
        solucoes, classificacao, historico = sistema.resolver()
        assert classificacao == 'determinado'
        assert solucoes['x'] == '2'
        assert solucoes['y'] == '1'


class TestInequacao1Grau:
    def test_2x_mais_6_maior_0(self):
        # 2x + 6 > 0 → x > -3
        ineq = Inequacao1Grau('2', '6', '>')
        resultado, historico = ineq.resolver()
        assert resultado == 'x > -3'
        assert len(historico) > 0

    def test_inverter_sinal(self):
        # -2x + 6 > 0 → x < 3
        ineq = Inequacao1Grau('-2', '6', '>')
        resultado, historico = ineq.resolver()
        assert resultado == 'x < 3'

    def test_menor_igual(self):
        # 3x - 9 <= 0 → x <= 3
        ineq = Inequacao1Grau('3', '-9', '<=')
        resultado, historico = ineq.resolver()
        assert resultado == 'x <= 3'

    def test_resultado_fracao(self):
        # 3x + 2 > 0 → x > -2/3
        ineq = Inequacao1Grau('3', '2', '>')
        resultado, historico = ineq.resolver()
        assert resultado == 'x > -2/3'

    def test_operador_invalido(self):
        with pytest.raises(ValueError):
            Inequacao1Grau('1', '2', '==')


# ==================== Testes de Equações 1º e 2º Grau ====================

from engine.algebra.equacao import Equacao1Grau, Equacao2Grau
from engine.basic.numeros import Racional
from engine.basic.passo import Historico


class TestEquacao1Grau:
    def test_2x_mais_6_igual_0(self):
        """2x + 6 = 0 -> x = -3"""
        eq = Equacao1Grau('2', '6')
        solucao, historico = eq.resolver()
        assert isinstance(solucao, Racional)
        assert solucao.return_number() == '-3'
        assert solucao.representacao_latex() == '-3'

    def test_3x_menos_9_igual_0(self):
        """3x - 9 = 0 -> x = 3"""
        eq = Equacao1Grau('3', '-9')
        solucao, historico = eq.resolver()
        assert isinstance(solucao, Racional)
        assert solucao.return_number() == '3'

    def test_fracao_resultado(self):
        """3x + 2 = 0 -> x = -2/3"""
        eq = Equacao1Grau('3', '2')
        solucao, historico = eq.resolver()
        assert isinstance(solucao, Racional)
        assert solucao.return_number() == '-2/3'
        assert '\\frac' in solucao.representacao_latex()

    def test_a_zero_levanta_erro(self):
        """a = 0 não é equação de 1º grau."""
        eq = Equacao1Grau('0', '5')
        with pytest.raises(ValueError):
            eq.resolver()

    def test_historico_tem_passos(self):
        """Verificar que o histórico contém passos."""
        eq = Equacao1Grau('2', '6')
        solucao, historico = eq.resolver()
        assert isinstance(historico, Historico)
        assert len(historico) >= 3


class TestEquacao2Grau:
    def test_x2_menos_5x_mais_6(self):
        """x² - 5x + 6 = 0 -> x1 = 3, x2 = 2"""
        eq = Equacao2Grau('1', '-5', '6')
        solucoes, historico = eq.resolver()
        assert len(solucoes) == 2
        valores = {s.return_number() for s in solucoes}
        assert '3' in valores
        assert '2' in valores

    def test_raiz_dupla(self):
        """x² - 4x + 4 = 0 -> x = 2 (raiz dupla)"""
        eq = Equacao2Grau('1', '-4', '4')
        solucoes, historico = eq.resolver()
        assert len(solucoes) == 1
        assert isinstance(solucoes[0], Racional)
        assert solucoes[0].return_number() == '2'

    def test_discriminante_negativo(self):
        """x² + x + 1 = 0 -> ValueError (delta < 0)"""
        eq = Equacao2Grau('1', '1', '1')
        with pytest.raises(ValueError, match='[Dd]iscriminante'):
            eq.resolver()

    def test_com_passos(self):
        """Verificar que o histórico tem passos preenchidos."""
        eq = Equacao2Grau('1', '-5', '6')
        solucoes, historico = eq.resolver()
        assert isinstance(historico, Historico)
        assert len(historico) >= 3
        for passo in historico.todos():
            assert passo.justificativa != ''
            assert passo.metodo != ''

    def test_coeficientes_maiores(self):
        """2x² - 8x + 6 = 0 -> x1 = 3, x2 = 1"""
        eq = Equacao2Grau('2', '-8', '6')
        solucoes, historico = eq.resolver()
        assert len(solucoes) == 2
        valores = {s.return_number() for s in solucoes}
        assert '3' in valores
        assert '1' in valores

    def test_representacao_latex_solucoes(self):
        """Soluções devem ter representacao_latex()."""
        eq = Equacao2Grau('1', '-5', '6')
        solucoes, historico = eq.resolver()
        for s in solucoes:
            latex = s.representacao_latex()
            assert isinstance(latex, str)
            assert len(latex) > 0
