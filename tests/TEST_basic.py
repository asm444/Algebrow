import sys, unittest, os, progress_bar

# Adiciona o diretório pai ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from basic.basic_operations import soma, diff, multi, div

class Operacoes_Basicas(unittest.TestCase):

    #Testando soma
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
          
    def test_soma_com_negativos(self):
        self.assertEqual(soma("-2", "3"), "1")
        self.assertEqual(soma("2", "-3"), "-1")

    def test_soma_decimais_com_negativos(self):
        self.assertEqual(soma("-2.45", "3"), "0.55")
        self.assertEqual(soma("2", "-3.45"), "-1.45")

    def test_soma_decimais(self):
        self.assertEqual(soma("2.1", "3"), "5.1")
        self.assertEqual(soma("2.0", "3.002"), "5.002")

    def test_soma_decimais_com_fracoes(self):
        self.assertEqual(soma("2.1", "1/2"), "13/5")
        self.assertEqual(soma("1/2", "2.1"), "13/5")

    def test_soma_fracoes_com_zero(self):    
        self.assertEqual(soma("0", "3/2"), "3/2")
        self.assertEqual(soma("2/3", "0"), "2/3")
        self.assertEqual(soma("0/1", "0/1"), "0")

    def test_soma_fracoes_negativas_com_zero(self):    
        self.assertEqual(soma("0", "-3/2"), "-3/2")
        self.assertEqual(soma("-2/3", "0"), "-2/3")
        self.assertEqual(soma("0/1", "-0/1"), "0")

    def test_soma_fracoes_mesmo_denominador(self):    
        self.assertEqual(soma("2/3", "1/3"), "1")
        self.assertEqual(soma("1/3", "4/3"), "5/3")

    def test_soma_fracoes_negativas_com__mesmo_denominador(self):    
        self.assertEqual(soma("2/3", "-1/3"), "1/3")
        self.assertEqual(soma("-2/3", "1/3"), "-1/3")

    def test_soma_fracoes_denominadores_diferentes(self):    
        self.assertEqual(soma("1/3", "1/2"), "5/6")
        self.assertEqual(soma("1/2", "1/3"), "5/6")

    def test_soma_fracoes_denominadores_diferentes_uma_negativa(self):    
        self.assertEqual(soma("1/3", "-1/2"), "-1/6")
        self.assertEqual(soma("-1/2", "1/3"), "-1/6")

    #Testando diff
    def test_diff_inteiros(self):
        self.assertEqual(diff("2", "3"), "-1")
        self.assertEqual(diff("3", "2"), "1")

    def test_diff_com_zero(self):    
        self.assertEqual(diff("0", "3"), "-3")
        self.assertEqual(diff("2", "0"), "2")
        self.assertEqual(diff("0", "0"), "0")

    def test_diff_com_zero_decimal(self):
        self.assertEqual(diff("0.0", "0.0"), "0")
        self.assertEqual(diff("2", "0.0"), "2")
        self.assertEqual(diff("1.0", "0.0"), "1")
        self.assertEqual(diff("0.0", "0.0"), "0")
          
    def test_diff_com_negativos(self):
        self.assertEqual(diff("-2", "3"), "-5")
        self.assertEqual(diff("2", "-3"), "5")

    def test_diff_decimais_com_negativos(self):
        self.assertEqual(diff("-2.45", "3"), "-5.45")
        self.assertEqual(diff("2", "-3.45"), "5.45")

    def test_diff_decimais(self):
        self.assertEqual(diff("2.1", "3"), "-0.9")
        self.assertEqual(diff("2.0", "3.002"), "-1.002")

    def test_diff_decimais_com_fracoes(self):
        self.assertEqual(diff("2.1", "1/2"), "8/5")
        self.assertEqual(diff("1/2", "2.1"), "-8/5")

    def test_diff_fracoes_com_zero(self):    
        self.assertEqual(diff("0", "3/2"), "-3/2")
        self.assertEqual(diff("2/3", "0"), "2/3")
        self.assertEqual(diff("0/1", "0/1"), "0")

    def test_diff_fracoes_negativas_com_zero(self):    
        self.assertEqual(diff("0", "-3/2"), "3/2")
        self.assertEqual(diff("-2/3", "0"), "-2/3")
        self.assertEqual(diff("0/1", "-0/1"), "0")

    def test_diff_fracoes_mesmo_denominador(self):    
        self.assertEqual(diff("2/3", "1/3"), "1/3")
        self.assertEqual(diff("1/3", "4/3"), "-1")

    def test_diff_fracoes_negativas_com__mesmo_denominador(self):    
        self.assertEqual(diff("2/3", "-1/3"), "1")
        self.assertEqual(diff("-2/3", "1/3"), "-1")

    def test_diff_fracoes_denominadores_diferentes(self):    
        self.assertEqual(diff("1/3", "1/2"), "-1/6")
        self.assertEqual(diff("1/2", "1/3"), "1/6")

    def test_diff_fracoes_denominadores_diferentes_uma_negativa(self):    
        self.assertEqual(diff("1/3", "-1/2"), "5/6")
        self.assertEqual(diff("-1/2", "1/3"), "-5/6")

    #Testando multi
    def test_multi_inteiros(self):
        self.assertEqual(multi("2", "3"), "6")
        self.assertEqual(multi("3", "2"), "6")

    def test_multi_com_zero(self):    
        self.assertEqual(multi("0", "3"), "0")
        self.assertEqual(multi("2", "0"), "0")
        self.assertEqual(multi("0", "0"), "0")

    def test_multi_com_zero_decimal(self):
        self.assertEqual(multi("0.0", "0.0"), "0")
        self.assertEqual(multi("2", "0.0"), "0")
        self.assertEqual(multi("1.0", "0.0"), "0")
        self.assertEqual(multi("0.0", "0.0"), "0")
          
    def test_multi_com_negativos(self):
        self.assertEqual(multi("-2", "3"), "-6")
        self.assertEqual(multi("2", "-3"), "-6")

    def test_multi_decimais_com_negativos(self):
        self.assertEqual(multi("-2.45", "3"), "-7.35")
        self.assertEqual(multi("2", "-3.45"), "-6.9")

    def test_multi_decimais(self):
        self.assertEqual(multi("2.1", "3"), "6.3")
        self.assertEqual(multi("2.0", "3.002"), "6.004")

    def test_multi_decimais_com_fracoes(self):
        self.assertEqual(multi("2.1", "1/2"), "21/20")
        self.assertEqual(multi("1/2", "2.1"), "21/20")

    def test_multi_fracoes_com_zero(self):    
        self.assertEqual(multi("0", "3/2"), "0")
        self.assertEqual(multi("2/3", "0"), "0")
        self.assertEqual(multi("0/1", "0/1"), "0")

    def test_multi_fracoes_negativas_com_zero(self):    
        self.assertEqual(multi("0", "-3/2"), "0")
        self.assertEqual(multi("-2/3", "0"), "0")
        self.assertEqual(multi("0/1", "-0/1"), "0")

    def test_multi_fracoes_mesmo_denominador(self):    
        self.assertEqual(multi("2/3", "1/3"), "2/9")
        self.assertEqual(multi("1/3", "4/3"), "4/9")

    def test_multi_fracoes_negativas_com__mesmo_denominador(self):    
        self.assertEqual(multi("2/3", "-1/3"), "-2/9")
        self.assertEqual(multi("-2/3", "1/3"), "-2/9")

    def test_multi_fracoes_denominadores_diferentes(self):    
        self.assertEqual(multi("1/3", "1/2"), "1/6")
        self.assertEqual(multi("1/2", "1/3"), "1/6")

    def test_multi_fracoes_denominadores_diferentes_uma_negativa(self):    
        self.assertEqual(multi("1/3", "-1/2"), "-1/6")
        self.assertEqual(multi("-1/2", "1/3"), "-1/6")
    
    #Testando div
    def test_div_inteiros(self):
        self.assertEqual(div("2", "3"), "0.(6)")
        self.assertEqual(div("3", "2"), "1.5")

    def test_div_com_zero(self):
        with self.assertRaises(ZeroDivisionError):
            div("2", "0")
        with self.assertRaises(ZeroDivisionError):
            div("0","0")    
    
    def test_div_com_zero_decimal(self):
        with self.assertRaises(ZeroDivisionError):
            div("2", "0.0")
        with self.assertRaises(ZeroDivisionError):
            div("1.0", "0.0")
        with self.assertRaises(ZeroDivisionError):
            div("0.0", "0.0")
          
    def test_div_com_negativos(self):
        self.assertEqual(div("-2", "3"), "-0.(6)")
        self.assertEqual(div("2", "-3"), "-0.(6)")

    def test_div_decimais_com_negativos(self):
        self.assertEqual(div("-2.45", "3"), "-0.81(6)")
        self.assertEqual(div("2", "-3.45"), "-0.(5797101449275362318840)")

    def test_div_decimais(self):
        self.assertEqual(div("2.1", "3"), "0.7")
        self.assertEqual(div("2.0", "3.00"), "0.(6)")

    def test_div_decimais_com_fracoes(self):
        self.assertEqual(div("2.1", "1/2"), "21/5")
        self.assertEqual(div("1/2", "2.1"), "5/21")

    def test_div_fracoes_por_zero(self):    
        self.assertEqual(div("0", "3/2"), "0")

    def test_div_fracoes_negativas_com_zero(self):
        with self.assertRaises(ZeroDivisionError):   
            div("-2/3", "0")
        with self.assertRaises(ZeroDivisionError):
            div("0/1", "-0/1")

    def test_div_fracoes_mesmo_denominador(self):    
        self.assertEqual(div("2/3", "1/3"), "2")
        self.assertEqual(div("1/3", "4/3"), "1/4")

    def test_div_fracoes_negativas_com__mesmo_denominador(self):    
        self.assertEqual(div("2/3", "-1/3"), "-2")
        self.assertEqual(div("-2/3", "1/3"), "-2")

    def test_div_fracoes_denominadores_diferentes(self):    
        self.assertEqual(div("1/3", "1/2"), "2/3")
        self.assertEqual(div("1/2", "1/3"), "3/2")

    def test_div_fracoes_denominadores_diferentes_uma_negativa(self):    
        self.assertEqual(div("1/3", "-1/2"), "-2/3")
        self.assertEqual(div("-1/2", "1/3"), "-3/2")

if __name__ == "__main__":
    progress_bar.progress_bar(Operacoes_Basicas)
    unittest.main()