import unittest
from engine.calculo.edo import (
    edo_linear_2ordem_coef_cte, metodo_euler
)


class TestEDO2OrdemCoefConstante(unittest.TestCase):

    def test_raizes_reais_distintas(self):
        # y'' - 3y' + 2y = 0 → r=1,2 → y = C1*e^x + C2*e^(2x)
        sol, tipo, hist = edo_linear_2ordem_coef_cte('1', '-3', '2')
        self.assertEqual(tipo, 'raizes_reais_distintas')
        self.assertIn('e^', sol)
        self.assertGreater(len(hist.todos()), 0)

    def test_raiz_dupla(self):
        # y'' - 2y' + y = 0 → r=1 (dupla) → y = (C1+C2*x)*e^x
        sol, tipo, hist = edo_linear_2ordem_coef_cte('1', '-2', '1')
        self.assertEqual(tipo, 'raiz_dupla')
        self.assertIn('e^', sol)

    def test_raizes_complexas(self):
        # y'' + y = 0 → r=±i → y = C1*cos(x) + C2*sin(x)
        sol, tipo, hist = edo_linear_2ordem_coef_cte('1', '0', '1')
        self.assertEqual(tipo, 'raizes_complexas')
        self.assertIn('cos', sol)
        self.assertIn('sin', sol)

    def test_raizes_complexas_com_parte_real(self):
        # y'' - 2y' + 2y = 0 → r=1±i → y = e^x(C1*cos(x) + C2*sin(x))
        sol, tipo, hist = edo_linear_2ordem_coef_cte('1', '-2', '2')
        self.assertEqual(tipo, 'raizes_complexas')
        self.assertIn('e^', sol)

    def test_passos_explicativos(self):
        sol, tipo, hist = edo_linear_2ordem_coef_cte('1', '-3', '2')
        self.assertGreater(len(hist.todos()), 2)


class TestMetodoEuler(unittest.TestCase):

    def test_euler_exponencial(self):
        # y' = y, y(0) = 1 → y = e^x ≈ 2.718 em x=1
        pontos, hist = metodo_euler("y", 0.0, 1.0, 0.01, 100)
        x_final, y_final = pontos[-1]
        self.assertAlmostEqual(x_final, 1.0, places=5)
        self.assertAlmostEqual(y_final, 2.718, delta=0.05)

    def test_euler_com_callable(self):
        pontos, hist = metodo_euler(lambda x, y: y, 0.0, 1.0, 0.1, 10)
        self.assertEqual(len(pontos), 11)  # 10 passos + ponto inicial

    def test_euler_passos(self):
        pontos, hist = metodo_euler("y", 0.0, 1.0, 0.5, 2)
        self.assertGreater(len(hist.todos()), 0)


if __name__ == "__main__":
    unittest.main()
