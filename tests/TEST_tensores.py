import unittest
import math
from engine.tensores.tensor_metrico import (
    TensorMetrico, metrica_plana_2d, metrica_polar, metrica_esferica
)
from engine.tensores.christoffel import christoffel_2especie
from engine.calculo.arvore import num, var, op


class TestTensorMetrico(unittest.TestCase):

    def test_metrica_plana_2d(self):
        m = metrica_plana_2d()
        self.assertEqual(m.dim, 2)
        self.assertIn('dx', m.representacao_latex())

    def test_metrica_polar(self):
        m = metrica_polar()
        self.assertEqual(m.dim, 2)
        self.assertIn('dr', m.representacao_latex())

    def test_metrica_esferica(self):
        m = metrica_esferica()
        self.assertEqual(m.dim, 3)

    def test_determinante_plana(self):
        m = metrica_plana_2d()
        det = m.determinante()
        # det(diag(1,1)) = 1
        val = det.avaliar({'x': 1, 'y': 1})
        self.assertAlmostEqual(val, 1.0)

    def test_determinante_polar(self):
        m = metrica_polar()
        det = m.determinante()
        # det = r²
        val = det.avaliar({'r': 3, 'theta': 0})
        self.assertAlmostEqual(val, 9.0)


class TestChristoffel(unittest.TestCase):

    def test_christoffel_plana_zero(self):
        m = metrica_plana_2d()
        componentes, hist = christoffel_2especie(m)
        # Todos Christoffel devem ser 0 em espaço plano
        for key, val in componentes.items():
            v = val.avaliar({'x': 1, 'y': 1})
            self.assertAlmostEqual(v, 0.0, places=5,
                                   msg=f"Christoffel {key} não é zero: {v}")

    def test_christoffel_polar(self):
        m = metrica_polar()
        componentes, hist = christoffel_2especie(m)
        # Γ^r_θθ = -r, Γ^θ_rθ = 1/r
        ponto = {'r': 2.0, 'theta': 1.0}
        # Verificar que pelo menos um Christoffel é não-zero
        algum_nao_zero = False
        for key, val in componentes.items():
            v = val.avaliar(ponto)
            if abs(v) > 0.01:
                algum_nao_zero = True
        self.assertTrue(algum_nao_zero, "Christoffel em polar deve ter termos não-zero")

    def test_historico_gerado(self):
        m = metrica_plana_2d()
        _, hist = christoffel_2especie(m)
        self.assertGreater(len(hist.todos()), 0)


if __name__ == "__main__":
    unittest.main()
