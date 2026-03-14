import unittest
from tests import progress_bar
from engine.basic.numeros import *

class Simplificao(unittest.TestCase):

    #Testando simplificação de raizes -> OK
    def test_simplificar_raiz_de_numero_com_potencia_igual_ao_indice(self):

        self.assertEqual(simplificar(Raiz('2','25')).representacao_latex(),  "5")
        self.assertEqual(simplificar(Raiz('3','8')).representacao_latex(),   "2")
        
    def test_simplificar_raiz_de_numeros_mistos_com_potencia_igual_ao_indice(self):

        self.assertEqual(simplificar(Raiz('2','36')).representacao_latex(),   "6")
        self.assertEqual(simplificar(Raiz('3','1728')).representacao_latex(), "12")
        
    def test_simplificar_raiz_de_reduzir_radicando_de_mesmo_multiplo(self):

        self.assertEqual(simplificar(Raiz('2','216')).representacao_latex(),  "6\\sqrt{2}{6}")
        self.assertEqual(simplificar(Raiz('7','16777216')).representacao_latex(), "8\\sqrt{7}{8}")

    def test_simplificar_raiz_de_reduzir_radicando_composto(self):

        self.assertEqual(simplificar(Raiz('2','2160')).representacao_latex(),  "12\\sqrt{2}{15}")
        self.assertEqual(simplificar(Raiz('5','125')).representacao_latex(), "\\sqrt{5}{125}")

    def test_simplificar_raiz_reduzir_gigantes(self):

        self.assertEqual(simplificar(Raiz('25','33554432')).representacao_latex(),  "2")
        self.assertEqual(simplificar(Raiz('32','4294967296')).representacao_latex(), "2")

    def test_simplificar_raiz_devolver_irredutivel(self):

        self.assertEqual(simplificar(Raiz('2','3')).representacao_latex(),  "\\sqrt{2}{3}")
        self.assertEqual(simplificar(Raiz('3','25')).representacao_latex(), "\\sqrt{3}{25}")

    def test_simplificar_raiz_um_ou_zero_em_inteiro(self):

        self.assertEqual(simplificar(Raiz('5','0')).representacao_latex(),  "0")
        self.assertEqual(simplificar(Raiz('4','1')).representacao_latex(), "1")
    
    def test_simplificar_raiz_indice_zero(self):

        with self.assertRaises(ZeroDivisionError):
            simplificar(Raiz('0','5'))

    #Testando simplificação de exponenciais -> OK
    def test_simplificar_exponencial_base_pura(self):

        self.assertEqual(simplificar(Exponencial('4','3')).representacao_latex(),  "2^{6}")
        self.assertEqual(simplificar(Exponencial('1728000','4')).representacao_latex(), "120^{12}")

    def test_simplificar_exponencial_irredutivel(self):

        self.assertEqual(simplificar(Exponencial('2','3')).representacao_latex(),  "2^{3}")
        self.assertEqual(simplificar(Exponencial('12','5')).representacao_latex(), "12^{5}")

    def test_simplificar_exponencial_redutivel(self):

        self.assertEqual(simplificar(Exponencial('16','3')).representacao_latex(),  "2^{12}")
        self.assertEqual(simplificar(Exponencial('36','5')).representacao_latex(), "6^{10}")

    def test_simplificar_exponencial_um_ou_zero(self):

        self.assertEqual(simplificar(Exponencial('1','3')).representacao_latex(),  "1")
        self.assertEqual(simplificar(Exponencial('0','25')).representacao_latex(), "0")

    def test_simplificar_exponencial_um_ou_zero(self):

        self.assertEqual(simplificar(Exponencial('151','0')).representacao_latex(),  "1")
    
    ##Testando simplificação de logaritmos
    def test_simplificar_logaritmando_puro(self):

        self.assertEqual(simplificar(Logaritmo('3','9')).representacao_latex(),  "2")
        self.assertEqual(simplificar(Logaritmo('2','2')).representacao_latex(), "1")

    def test_simplificar_logaritmando_irredutivel(self):

        self.assertEqual(simplificar(Logaritmo('2','3')).representacao_latex(),  "\\log_{2}{3}")
        self.assertEqual(simplificar(Logaritmo('12','5')).representacao_latex(), "\\log_{12}{5}")

    def test_simplificar_logaritmando_redutivel(self):

        self.assertEqual(simplificar(Logaritmo('3','144')).representacao_latex(),  "2\\log_{3}{12}")
        self.assertEqual(simplificar(Logaritmo('2','36')).representacao_latex(), "2\\log_{2}{6}")

    def test_simplificar_logaritmando_base_um_ou_zero(self):

        with self.assertRaises(ValueError):
            simplificar(Logaritmo('1','3'))
            simplificar(Logaritmo('0','25'))

    def test_simplificar_logaritmando_um_ou_zero(self):

        with self.assertRaises(ValueError):
            simplificar(Logaritmo('151','0'))

    ##Testando simplificação de logaritmos
    def test_simplificar_racional_sem_fracao(self):

        self.assertEqual(simplificar(Racional('9')).representacao_latex(),  "9")
        self.assertEqual(simplificar(Racional('0')).representacao_latex(), "0")

    def test_simplificar_racional_com_fracao_sem_reducao(self):

        self.assertEqual(simplificar(Racional('2/3')).representacao_latex(),  "\\frac{2}{3}")
        self.assertEqual(simplificar(Racional('19/31')).representacao_latex(), "\\frac{19}{31}")

    def test_simplificar_racional_com_fracao_redutivel(self):

        self.assertEqual(simplificar(Racional('3/9')).representacao_latex(),  "\\frac{1}{3}")
        self.assertEqual(simplificar(Racional('24/36')).representacao_latex(), "\\frac{2}{3}")

    def test_simplificar_logaritmando_um_ou_zero(self):

        with self.assertRaises(ZeroDivisionError):
            simplificar(Racional('5/0'))

    # Testes de edge cases — validações de domínio
    def test_0_elevado_0_indefinido(self):
        with self.assertRaises(ValueError):
            simplificar(Exponencial('0','0'))

    def test_raiz_negativa(self):
        with self.assertRaises(ValueError):
            simplificar(Raiz('2','-4'))

    def test_base_negativa_exponencial(self):
        with self.assertRaises(ValueError):
            simplificar(Exponencial('-2','3'))

    def test_log_base_negativa(self):
        with self.assertRaises(ValueError):
            simplificar(Logaritmo('-2','8'))

    def test_expoente_1(self):
        self.assertEqual(simplificar(Exponencial('5','1')), Racional('5'))


if __name__ == "__main__":
    progress_bar.progress_bar(Simplificao)
    unittest.main()