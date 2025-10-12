import sys, unittest, os, progress_bar

# Adiciona o diretório pai ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from basic_operations import soma, diff

class Operacoes_Basicas(unittest.TestCase):

    def test_soma_inteiros(self):
        self.assertEqual(soma("2", "3"), "5")
        self.assertEqual(soma("3", "2"), "5")

    def test_soma_com_zero(self):    
        self.assertEqual(soma("0", "3"), "3")
        self.assertEqual(soma("2", "0"), "2")
        self.assertEqual(soma("0", "0"), "0")

    def test_soma_com_zero_decimal(self):
        self.assertEqual(soma("0.0", "0.0"), "0")
        self.assertEqual(soma("2", "0.0"), "2")
        self.assertEqual(soma("1.0", "0.0"), "1")
        self.assertEqual(soma("0.0", "0.0"), "0")
        self.assertEqual(soma("0.0", "0.0"), "0") 
          
    def test_soma_com_negativos(self):
        self.assertEqual(soma("-2", "3"), "1")
        self.assertEqual(soma("2", "-3"), "-1")

    def test_soma_decimais_com_negativos(self):
        self.assertEqual(soma("-2.45", "3"), "0.55")
        self.assertEqual(soma("2", "-3.45"), "-1.45")

    def test_soma_decimais(self):
        self.assertEqual(soma("2.1", "3"), "5.1")
        self.assertEqual(soma("2.0", "3.0"), "5")

    def test_soma_decimais_com_fracoes(self):
        self.assertEqual(soma("2.1", "1/2"), "13/5")
        self.assertEqual(soma("1/2", "2.1"), "13/5")
    def test_soma_fracoes_com_zero(self):    
        self.assertEqual(soma("0", "3/2"), "3/2")
        self.assertEqual(soma("2/3", "0"), "2/3")
        self.assertEqual(soma("0/1", "0/1"), "0")
    

if __name__ == "__main__":
    progress_bar.progress_bar(Operacoes_Basicas)
    unittest.main()