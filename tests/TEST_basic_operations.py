import sys
import os

# Adiciona o diretório pai ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from basic_operations import soma

import unittest

import unittest
from basic_operations import soma

import unittest
from basic_operations import soma

class TestSomaRacional(unittest.TestCase):
    
    def test_soma_inteiros(self):
        self.assertEqual(soma("2", "3"), "5.0")

    def test_primeiro_inteiro_segundo_fracao(self):
        self.assertEqual(soma("2", "3/4"), "11/4")

    def test_primeiro_inteiro_segundo_fracao_simplificada(self):
        self.assertEqual(soma("1", "1/2"), "3/2")

    def test_primeiro_fracao_segundo_inteiro(self):
        self.assertEqual(soma("3/5", "2"), "13/5")

    def test_primeiro_fracao_segundo_inteiro_simplificado(self):
        self.assertEqual(soma("1/2", "1"), "3/2")

    def test_fracoes_mesmo_denominador(self):
        self.assertEqual(soma("2/3", "1/3"), "1")

    def test_fracoes_diferentes_denominadores(self):
        self.assertEqual(soma("1/2", "1/3"), "5/6")

    def test_fracao_com_zero(self):
        self.assertEqual(soma("0/1", "2/3"), "2/3")

    def test_negativos(self):
        self.assertEqual(soma("-1", "3/2"), "1/2")
        self.assertEqual(soma("1", "-3/2"), "-1/2")
        self.assertEqual(soma("-2/3", "1/3"), "-1/3")
        self.assertEqual(soma("-1/2", "-1/3"), "-5/6")

    def test_resultado_zero(self):
        self.assertEqual(soma("-2/3", "2/3"), "0")

    def test_numeros_grandes(self):
        self.assertEqual(soma("123456789", "1/1"), "123456790")

if __name__ == "__main__":
    unittest.main()