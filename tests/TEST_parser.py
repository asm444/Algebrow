import unittest
from engine.parser import parsear, tokenizar, ParserError, TokenizadorError
from engine.basic.numeros import Racional, Raiz, Exponencial, Logaritmo
from engine.basic.expressao import Expressao


class TestTokenizador(unittest.TestCase):

    def test_tokenizar_numero(self):
        tokens = tokenizar('42')
        self.assertEqual(tokens[0], ('NUM', '42'))

    def test_tokenizar_operadores(self):
        tokens = tokenizar('3 + 4 * 2')
        tipos = [t[0] for t in tokens]
        self.assertEqual(tipos, ['NUM', '+', 'NUM', '*', 'NUM', 'EOF'])

    def test_tokenizar_sqrt(self):
        tokens = tokenizar('sqrt(216)')
        self.assertEqual(tokens[0], ('SQRT', 'sqrt'))

    def test_tokenizar_log(self):
        tokens = tokenizar('log_3(9)')
        tipos = [t[0] for t in tokens]
        self.assertEqual(tipos, ['LOG', '_', 'NUM', '(', 'NUM', ')', 'EOF'])

    def test_tokenizar_erro_caractere(self):
        with self.assertRaises(TokenizadorError):
            tokenizar('3 & 4')

    def test_tokenizar_erro_identificador(self):
        with self.assertRaises(TokenizadorError):
            tokenizar('sin(3)')


class TestParserBasico(unittest.TestCase):

    def test_inteiro(self):
        r = parsear('42')
        self.assertIsInstance(r, Racional)
        self.assertEqual(r.return_number(), '42')

    def test_decimal(self):
        r = parsear('3.14')
        self.assertIsInstance(r, Racional)
        self.assertEqual(r.return_number(), '3.14')

    def test_fracao(self):
        r = parsear('3/4')
        self.assertIsInstance(r, Racional)
        self.assertEqual(r.return_number(), '3/4')

    def test_negativo(self):
        r = parsear('-5')
        self.assertIsInstance(r, Racional)
        self.assertEqual(r.return_number(), '-5')


class TestParserOperacoes(unittest.TestCase):

    def test_soma_inteiros(self):
        r = parsear('3 + 4')
        self.assertEqual(r.representacao_latex(), '7')

    def test_subtracao(self):
        r = parsear('10 - 3')
        self.assertEqual(r.representacao_latex(), '7')

    def test_multiplicacao(self):
        r = parsear('3 * 4')
        self.assertEqual(r.representacao_latex(), '12')

    def test_precedencia_mult_sobre_soma(self):
        r = parsear('2 + 3 * 4')
        # 3*4=12, 2+12=14
        self.assertEqual(r.representacao_latex(), '14')

    def test_parenteses(self):
        r = parsear('(2 + 3) * 4')
        # (2+3)=5, 5*4=20
        self.assertEqual(r.representacao_latex(), '20')


class TestParserFuncoes(unittest.TestCase):

    def test_sqrt_simples(self):
        r = parsear('sqrt(25)')
        self.assertIsInstance(r, Raiz)

    def test_sqrt_simplifica(self):
        r = parsear('sqrt(216)')
        resultado = r.simplificar()
        self.assertEqual(resultado.representacao_latex(), '6\\sqrt{2}{6}')

    def test_sqrt_com_indice(self):
        r = parsear('sqrt_3(8)')
        self.assertIsInstance(r, Raiz)
        self.assertEqual(r.return_indice(), '3')

    def test_exponencial(self):
        r = parsear('2^3')
        self.assertIsInstance(r, Exponencial)
        self.assertEqual(r.return_base(), '2')
        self.assertEqual(r.return_expoente(), '3')

    def test_logaritmo_com_base(self):
        r = parsear('log_3(9)')
        self.assertIsInstance(r, Logaritmo)
        self.assertEqual(r.return_base(), '3')

    def test_logaritmo_sem_base(self):
        r = parsear('log(100)')
        self.assertIsInstance(r, Logaritmo)
        self.assertEqual(r.return_base(), '10')


class TestParserExpressaoComposta(unittest.TestCase):

    def test_fracao_mais_raiz(self):
        r = parsear('3/4 + sqrt(2)')
        self.assertIsInstance(r, Expressao)

    def test_multiplicacao_raiz(self):
        r = parsear('3 * sqrt(2)')
        self.assertIsInstance(r, Raiz)
        self.assertEqual(r.coeficiente, '3')

    def test_soma_fracoes(self):
        r = parsear('1/3 + 1/6')
        self.assertEqual(r.representacao_latex(), '\\frac{1}{2}')


class TestParserErros(unittest.TestCase):

    def test_expressao_vazia(self):
        with self.assertRaises(ParserError):
            parsear('')

    def test_operador_sem_operando(self):
        with self.assertRaises(ParserError):
            parsear('+ 3')

    def test_parentese_sem_fechar(self):
        with self.assertRaises(ParserError):
            parsear('(3 + 4')


class TestSolver(unittest.TestCase):

    def test_solver_sqrt(self):
        from engine.solver import Solver
        s = Solver(verbosidade=3)
        r = s.resolver('sqrt(216)')
        self.assertEqual(r.latex_resultado, '6\\sqrt{2}{6}')
        self.assertGreater(len(r.historico.todos()), 0)

    def test_solver_log(self):
        from engine.solver import Solver
        s = Solver(verbosidade=3)
        r = s.resolver('log_3(9)')
        self.assertEqual(r.latex_resultado, '2')

    def test_solver_verbosidade_0(self):
        from engine.solver import Solver
        s = Solver(verbosidade=0)
        r = s.resolver('sqrt(216)')
        passos_visiveis = r.historico.filtrar()
        self.assertEqual(len(passos_visiveis), 1)  # só resultado final

    def test_solver_verbosidade_4(self):
        from engine.solver import Solver
        s = Solver(verbosidade=4)
        r = s.resolver('sqrt(216)')
        passos_visiveis = r.historico.filtrar()
        self.assertGreater(len(passos_visiveis), 3)

    def test_solver_serializar(self):
        from engine.solver import Solver
        s = Solver()
        r = s.resolver('2^3')
        dados = r.serializar()
        self.assertIn('latex_entrada', dados)
        self.assertIn('latex_resultado', dados)
        self.assertIn('passos', dados)
        self.assertIsInstance(dados['passos'], list)

    def test_solver_entrada_vazia(self):
        from engine.solver import Solver
        s = Solver()
        with self.assertRaises(ValueError):
            s.resolver('')

    def test_solver_valor_numerico(self):
        from engine.solver import Solver
        s = Solver()
        r = s.resolver('sqrt(216)')
        self.assertNotEqual(r.valor_numerico, '')
        self.assertAlmostEqual(float(r.valor_numerico), 14.6969, places=3)


class TestParserVariaveis(unittest.TestCase):
    def test_variavel_simples(self):
        r = parsear('x')
        self.assertEqual(r.tipo_de_numero, 'variavel')

    def test_equacao_simples(self):
        r = parsear('2*x + 3 = 7')
        self.assertEqual(r.tipo_de_numero, 'sentenca')
        self.assertEqual(r.operador, '=')

    def test_multiplicacao_implicita(self):
        r = parsear('2x')
        # Deve multiplicar 2 * x
        self.assertIsNotNone(r)

    def test_inequacao(self):
        r = parsear('x > 5')
        self.assertEqual(r.tipo_de_numero, 'sentenca')
        self.assertEqual(r.operador, '>')


if __name__ == "__main__":
    unittest.main()
