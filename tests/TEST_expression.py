import unittest
from tests import progress_bar
from engine.basic.numeros import Racional, Raiz, Exponencial, Logaritmo
from engine.basic.expressao import soma, subtracao, multiplicacao, Expressao


class TestSoma(unittest.TestCase):

    # Racional + Racional
    def test_soma_racional_racional(self):
        r = soma(Racional('2'), Racional('3'))
        self.assertEqual(r.representacao_latex(), '5')

    def test_soma_racional_fracao(self):
        r = soma(Racional('1/3'), Racional('1/6'))
        self.assertEqual(r.representacao_latex(), '\\frac{1}{2}')

    # Raiz + Raiz (mesma parte irracional)
    def test_soma_raiz_mesma(self):
        r = soma(Raiz('2', '3', '2'), Raiz('2', '3', '5'))
        self.assertEqual(r.representacao_latex(), '7\\sqrt{2}{3}')

    # Raiz + Raiz (diferente)
    def test_soma_raiz_diferente(self):
        r = soma(Raiz('2', '3'), Raiz('2', '5'))
        self.assertIsInstance(r, Expressao)

    # Raiz + Raiz = 0
    def test_soma_raiz_resulta_zero(self):
        r = soma(Raiz('2', '3', '3'), Raiz('2', '3', '-3'))
        self.assertEqual(r.representacao_latex(), '0')

    # Exponencial + Exponencial (mesma)
    def test_soma_exponencial_mesma(self):
        r = soma(Exponencial('2', '3', '2'), Exponencial('2', '3', '5'))
        self.assertIsInstance(r, Exponencial)
        self.assertEqual(r.coeficiente, '7')
        self.assertEqual(r.return_base(), '2')
        self.assertEqual(r.return_expoente(), '3')

    # Exponencial + Exponencial (diferente)
    def test_soma_exponencial_diferente(self):
        r = soma(Exponencial('2', '3'), Exponencial('3', '2'))
        self.assertIsInstance(r, Expressao)

    # Logaritmo + Logaritmo (mesma)
    def test_soma_logaritmo_mesmo(self):
        r = soma(Logaritmo('2', '3', '2'), Logaritmo('2', '3', '5'))
        self.assertIsInstance(r, Logaritmo)
        self.assertEqual(r.coeficiente, '7')

    # Logaritmo + Logaritmo (diferente base)
    def test_soma_logaritmo_diferente(self):
        r = soma(Logaritmo('2', '3'), Logaritmo('3', '5'))
        self.assertIsInstance(r, Expressao)

    # Tipos mistos
    def test_soma_racional_raiz(self):
        r = soma(Racional('3'), Raiz('2', '5'))
        self.assertIsInstance(r, Expressao)

    def test_soma_racional_exponencial(self):
        r = soma(Racional('2'), Exponencial('3', '4'))
        self.assertIsInstance(r, Expressao)

    def test_soma_raiz_logaritmo(self):
        r = soma(Raiz('2', '3'), Logaritmo('2', '5'))
        self.assertIsInstance(r, Expressao)


class TestSubtracao(unittest.TestCase):

    def test_subtracao_racional(self):
        r = subtracao(Racional('5'), Racional('3'))
        self.assertEqual(r.representacao_latex(), '2')

    def test_subtracao_raiz_mesma(self):
        r = subtracao(Raiz('2', '3', '5'), Raiz('2', '3', '2'))
        self.assertEqual(r.representacao_latex(), '3\\sqrt{2}{3}')

    def test_subtracao_raiz_diferente(self):
        r = subtracao(Raiz('2', '3'), Raiz('2', '5'))
        self.assertIsInstance(r, Expressao)

    def test_subtracao_resulta_zero(self):
        r = subtracao(Racional('7'), Racional('7'))
        self.assertEqual(r.representacao_latex(), '0')


class TestMultiplicacao(unittest.TestCase):

    # Racional × Racional
    def test_multi_racional_racional(self):
        r = multiplicacao(Racional('3'), Racional('4'))
        self.assertEqual(r.representacao_latex(), '12')

    def test_multi_racional_fracao(self):
        r = multiplicacao(Racional('2/3'), Racional('3/4'))
        self.assertEqual(r.representacao_latex(), '\\frac{1}{2}')

    # Racional × Irracional
    def test_multi_racional_raiz(self):
        r = multiplicacao(Racional('3'), Raiz('2', '5'))
        self.assertIsInstance(r, Raiz)
        self.assertEqual(r.coeficiente, '3')

    def test_multi_racional_exponencial(self):
        r = multiplicacao(Racional('2'), Exponencial('3', '4'))
        self.assertIsInstance(r, Exponencial)
        self.assertEqual(r.coeficiente, '2')

    def test_multi_racional_logaritmo(self):
        r = multiplicacao(Racional('5'), Logaritmo('2', '3'))
        self.assertIsInstance(r, Logaritmo)
        self.assertEqual(r.coeficiente, '5')

    # Irracional × Racional (comutativo)
    def test_multi_raiz_racional(self):
        r = multiplicacao(Raiz('2', '5'), Racional('3'))
        self.assertIsInstance(r, Raiz)
        self.assertEqual(r.coeficiente, '3')

    # Exponencial × Exponencial (mesma base)
    def test_multi_exponencial_mesma_base(self):
        r = multiplicacao(Exponencial('2', '3'), Exponencial('2', '5'))
        self.assertIsInstance(r, Exponencial)
        self.assertEqual(r.return_base(), '2')
        self.assertEqual(r.return_expoente(), '8')

    # Raiz × Raiz (mesmo índice)
    def test_multi_raiz_mesmo_indice(self):
        r = multiplicacao(Raiz('2', '3'), Raiz('2', '12'))
        # √3 × √12 = √36 = 6
        self.assertEqual(r.representacao_latex(), '6')

    def test_multi_raiz_mesmo_indice_nao_simplifica_total(self):
        r = multiplicacao(Raiz('2', '2'), Raiz('2', '3'))
        # √2 × √3 = √6
        self.assertIsInstance(r, Raiz)
        self.assertEqual(r.return_radicando(), '6')

    # Racional × zero
    def test_multi_racional_zero(self):
        r = multiplicacao(Racional('0'), Raiz('2', '5'))
        self.assertEqual(r.coeficiente, '0')


class TestExpressao(unittest.TestCase):

    def test_representacao_latex(self):
        e = Expressao(termos=[Racional('3'), Raiz('2', '5')])
        latex = e.representacao_latex()
        self.assertIn('3', latex)
        self.assertIn('\\sqrt', latex)

    def test_simplificar_agrupa_termos(self):
        e = Expressao(termos=[
            Raiz('2', '3', '2'),
            Racional('5'),
            Raiz('2', '3', '3'),
        ])
        r = e.simplificar()
        # Deve agrupar as duas raízes: 2√3 + 3√3 = 5√3, fica 5 + 5√3
        self.assertIsInstance(r, Expressao)

    def test_simplificar_todos_iguais(self):
        e = Expressao(termos=[Racional('2'), Racional('3')])
        r = e.simplificar()
        self.assertIsInstance(r, Racional)
        self.assertEqual(r.representacao_latex(), '5')

    def test_simplificar_com_zero(self):
        e = Expressao(termos=[Racional('0'), Raiz('2', '5')])
        r = e.simplificar()
        self.assertIsInstance(r, Raiz)

    def test_organizar_ordem(self):
        e = Expressao(termos=[Raiz('2', '3'), Racional('5'), Logaritmo('2', '3')])
        e.organizar()
        self.assertEqual(e.termos[0].tipo_de_numero, 'racional')
        self.assertEqual(e.termos[1].tipo_de_numero, 'raiz')
        self.assertEqual(e.termos[2].tipo_de_numero, 'logaritmo')


if __name__ == "__main__":
    progress_bar.progress_bar(TestSoma)
    progress_bar.progress_bar(TestSubtracao)
    progress_bar.progress_bar(TestMultiplicacao)
    progress_bar.progress_bar(TestExpressao)
    unittest.main()
