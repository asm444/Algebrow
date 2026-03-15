"""Testes para o conversor de LaTeX puro → sintaxe interna do engine."""

import pytest
from engine.latex_converter import converter_latex, _eh_latex


class TestDeteccaoLatex:
    """Testes para _eh_latex()."""

    def test_detecta_frac(self):
        assert _eh_latex(r'\frac{3}{4}')

    def test_detecta_sqrt(self):
        assert _eh_latex(r'\sqrt{216}')

    def test_detecta_log(self):
        assert _eh_latex(r'\log_{2}{8}')

    def test_detecta_cdot(self):
        assert _eh_latex(r'3 \cdot 4')

    def test_nao_detecta_sintaxe_interna(self):
        assert not _eh_latex('sqrt(216)')

    def test_nao_detecta_texto_simples(self):
        assert not _eh_latex('3 + 4')


class TestFracoes:
    """Testes para conversão de \\frac."""

    def test_frac_simples(self):
        assert converter_latex(r'\frac{3}{4}') == '3/4'

    def test_frac_com_soma(self):
        resultado = converter_latex(r'\frac{3}{4} + \frac{1}{6}')
        assert resultado == '3/4 + 1/6'

    def test_dfrac(self):
        assert converter_latex(r'\dfrac{2}{5}') == '2/5'

    def test_tfrac(self):
        assert converter_latex(r'\tfrac{7}{3}') == '7/3'


class TestRaizes:
    """Testes para conversão de \\sqrt."""

    def test_sqrt_simples(self):
        assert converter_latex(r'\sqrt{216}') == 'sqrt(216)'

    def test_sqrt_cubica(self):
        assert converter_latex(r'\sqrt[3]{8}') == 'sqrt_3(8)'

    def test_sqrt_quarta(self):
        assert converter_latex(r'\sqrt[4]{81}') == 'sqrt_4(81)'

    def test_sqrt_com_expressao(self):
        assert converter_latex(r'\sqrt{50}') == 'sqrt(50)'


class TestPotencias:
    """Testes para conversão de potências."""

    def test_potencia_com_chaves(self):
        assert converter_latex(r'2^{10}') == '2^10'

    def test_potencia_simples(self):
        # Sem chaves, sem backslash → não é LaTeX, retorna sem alterar
        assert converter_latex('2^3') == '2^3'

    def test_potencia_com_expressao(self):
        resultado = converter_latex(r'2^{3} + 3^{2}')
        assert '2^3' in resultado
        assert '3^2' in resultado


class TestLogaritmos:
    """Testes para conversão de \\log."""

    def test_log_com_base_e_argumento(self):
        assert converter_latex(r'\log_{2}{8}') == 'log_2(8)'

    def test_log_base_10(self):
        assert converter_latex(r'\log_{10}{1000}') == 'log_10(1000)'

    def test_log_sem_base(self):
        assert converter_latex(r'\log{100}') == 'log(100)'


class TestOperadores:
    """Testes para conversão de operadores LaTeX."""

    def test_cdot(self):
        assert converter_latex(r'3 \cdot 4') == '3 * 4'

    def test_times(self):
        assert converter_latex(r'6 \times 7') == '6 * 7'

    def test_geq(self):
        resultado = converter_latex(r'x \geq 5')
        assert '>=' in resultado

    def test_leq(self):
        resultado = converter_latex(r'x \leq 10')
        assert '<=' in resultado


class TestDelimitadores:
    """Testes para \\left e \\right."""

    def test_left_right_parenteses(self):
        resultado = converter_latex(r'\left( 3 + 4 \right)')
        assert '(' in resultado
        assert ')' in resultado


class TestExpressoesMistas:
    """Testes para expressões combinadas."""

    def test_frac_mais_sqrt(self):
        resultado = converter_latex(r'\frac{3}{4} + \sqrt{2}')
        assert '3/4' in resultado
        assert 'sqrt(2)' in resultado

    def test_potencia_mais_log(self):
        resultado = converter_latex(r'2^{3} + \log_{2}{16}')
        assert '2^3' in resultado
        assert 'log_2(16)' in resultado

    def test_produto_raizes(self):
        resultado = converter_latex(r'\sqrt{3} \cdot \sqrt{12}')
        assert 'sqrt(3)' in resultado
        assert 'sqrt(12)' in resultado


class TestPassthrough:
    """Testes para expressões que não são LaTeX (devem passar sem alteração)."""

    def test_sintaxe_interna_preservada(self):
        assert converter_latex('sqrt(216)') == 'sqrt(216)'

    def test_aritmetica_simples(self):
        assert converter_latex('3 + 4') == '3 + 4'

    def test_equacao_simples(self):
        assert converter_latex('2x + 3 = 7') == '2x + 3 = 7'


class TestIntegracaoSolver:
    """Testes de integração: LaTeX → Solver → resultado correto."""

    def test_frac_via_solver(self):
        from engine.solver import Solver
        s = Solver(verbosidade=0)
        r = s.resolver(r'\frac{3}{4} + \frac{1}{4}')
        assert r.latex_resultado == '1'

    def test_sqrt_via_solver(self):
        from engine.solver import Solver
        s = Solver(verbosidade=0)
        r = s.resolver(r'\sqrt{144}')
        assert '12' in r.latex_resultado

    def test_potencia_via_solver(self):
        from engine.solver import Solver
        s = Solver(verbosidade=0)
        r = s.resolver(r'2^{10}')
        # Engine mantém forma exponencial; verifica valor numérico
        assert r.valor_numerico == '1024'

    def test_log_via_solver(self):
        from engine.solver import Solver
        s = Solver(verbosidade=0)
        r = s.resolver(r'\log_{2}{8}')
        assert '3' in r.latex_resultado

    def test_expressao_mista_via_solver(self):
        from engine.solver import Solver
        s = Solver(verbosidade=0)
        r = s.resolver(r'\sqrt[3]{27}')
        assert '3' in r.latex_resultado
