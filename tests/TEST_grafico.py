import unittest
from engine.funcoes.grafico import gerar_pontos, detectar_assintotas_verticais


class TestGerarPontos(unittest.TestCase):

    def test_funcao_linear(self):
        dados = gerar_pontos("x", -5.0, 5.0, 11)
        self.assertEqual(len(dados["x"]), 11)
        self.assertEqual(len(dados["y"]), 11)
        # Todos os pontos devem existir
        self.assertTrue(all(y is not None for y in dados["y"]))

    def test_funcao_quadratica(self):
        dados = gerar_pontos("x**2", -5.0, 5.0, 21)
        self.assertEqual(len(dados["x"]), 21)
        # Todos os y devem ser >= 0
        for y in dados["y"]:
            if y is not None:
                self.assertGreaterEqual(y, 0)

    def test_funcao_1_sobre_x(self):
        dados = gerar_pontos("1/x", -5.0, 5.0, 201)
        # Deve ter None perto de x=0
        nones = [i for i, y in enumerate(dados["y"]) if y is None]
        self.assertGreater(len(nones), 0)

    def test_constante(self):
        dados = gerar_pontos("5", -10.0, 10.0, 50)
        for y in dados["y"]:
            if y is not None:
                self.assertAlmostEqual(y, 5.0)

    def test_num_pontos_respeitado(self):
        dados = gerar_pontos("x", 0.0, 10.0, 100)
        self.assertEqual(len(dados["x"]), 100)

    def test_x_min_maior_x_max_erro(self):
        with self.assertRaises(ValueError):
            gerar_pontos("x", 10.0, 5.0, 50)

    def test_multiplicacao_implicita(self):
        dados = gerar_pontos("2x", 0.0, 5.0, 11)
        # x=0 → y=0, x=5 → y=10
        self.assertAlmostEqual(dados["y"][0], 0.0)
        self.assertAlmostEqual(dados["y"][-1], 10.0)

    def test_com_callable(self):
        dados = gerar_pontos(lambda x: x * x, -5.0, 5.0, 11)
        self.assertAlmostEqual(dados["y"][0], 25.0)
        self.assertAlmostEqual(dados["y"][-1], 25.0)


class TestAssintotas(unittest.TestCase):

    def test_1_sobre_x(self):
        # gerar_pontos detecta descontinuidades
        dados = gerar_pontos("1/x", -5.0, 5.0, 201)
        self.assertGreater(len(dados["assintotas_verticais"]), 0)

    def test_funcao_linear_sem_assintotas(self):
        assintotas = detectar_assintotas_verticais("x + 1", -10.0, 10.0)
        self.assertEqual(len(assintotas), 0)


if __name__ == "__main__":
    unittest.main()
