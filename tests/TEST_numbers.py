import unittest, tests.progress_bar as progress_bar

# Adiciona o diretório pai ao path
from basic.numbers import *

class Simplificao(unittest.TestCase):

    #Testando simplificação de raizes
    def test_simplificar_raiz_de_numero_com_potencia_igual_ao_indice(self):

        self.assertEqual(simplificar(Raiz('2','25')).representacao_latex(),  "5")
        self.assertEqual(simplificar(Raiz('3','8')).representacao_latex(),   "2")
        
    def test_simplificar_raiz_de_numeros_mistos_com_potencia_igual_ao_indice(self):

        self.assertEqual(simplificar(Raiz('2','36')).representacao_latex(),   "6")
        self.assertEqual(simplificar(Raiz('3','1728')).representacao_latex(), "12")
        
    def test_simplificar_raiz_de_reduzir_radicando_de_mesmo_multiplo(self):

        self.assertEqual(simplificar(Raiz('2','216')).representacao_latex(),  "6\sqrt{2}{6}")
        self.assertEqual(simplificar(Raiz('7','16777216')).representacao_latex(), "8\sqrt{7}{8}")

    def test_simplificar_raiz_de_reduzir_radicando_composto(self):

        self.assertEqual(simplificar(Raiz('2','2160')).representacao_latex(),  "12\sqrt{2}{15}")
        self.assertEqual(simplificar(Raiz('5','125')).representacao_latex(), "\sqrt{5}{125}")

    def test_simplificar_raiz_reduzir_gigantes(self):

        self.assertEqual(simplificar(Raiz('25','33554432')).representacao_latex(),  "2")
        self.assertEqual(simplificar(Raiz('32','4294967296')).representacao_latex(), "2")

    def test_simplificar_raiz_devolver_irredutivel(self):

        self.assertEqual(simplificar(Raiz('2','3')).representacao_latex(),  "\sqrt{2}{3}")
        self.assertEqual(simplificar(Raiz('3','25')).representacao_latex(), "\sqrt{3}{25}")

    def test_simplificar_exponencial_base_pura(self):

        self.assertEqual(simplificar(Exponencial('4','3')).representacao_latex(),  "2^{6}")
        self.assertEqual(simplificar(Exponencial('1728000','4')).representacao_latex(), "\sqrt{3}{25}")

    def test_simplificar_exponencial_irredutivel(self):

        self.assertEqual(simplificar(Exponencial('2','3')).representacao_latex(),  "2^{3}")
        self.assertEqual(simplificar(Exponencial('3','5')).representacao_latex(), "3^{5}")
           
if __name__ == "__main__":
    progress_bar.progress_bar(Simplificao)
    unittest.main()