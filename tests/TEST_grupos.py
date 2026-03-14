import unittest
import math
from engine.algebra_abstrata.grupo import (
    grupo_ciclico, grupo_simetrico, grupo_diedral, grupo_klein, Grupo
)
from engine.algebra_abstrata.lie import (
    comutador, so3_geradores, rotacao_2d, exponencial_matricial, gram_schmidt
)
from engine.algebra_linear.matriz import Matriz


class TestGruposCiclicos(unittest.TestCase):

    def test_z4_ordem(self):
        g = grupo_ciclico(4)
        self.assertEqual(g.ordem(), 4)

    def test_z4_abeliano(self):
        g = grupo_ciclico(4)
        self.assertTrue(g.eh_abeliano())

    def test_z4_identidade(self):
        g = grupo_ciclico(4)
        self.assertEqual(g.identidade(), 0)

    def test_z6_ordem_elemento(self):
        g = grupo_ciclico(6)
        self.assertEqual(g.ordem_elemento(2), 3)

    def test_z6_inverso(self):
        g = grupo_ciclico(6)
        self.assertEqual(g.inverso(2), 4)  # 2 + 4 = 6 ≡ 0 mod 6


class TestGrupoSimetrico(unittest.TestCase):

    def test_s3_ordem(self):
        s3 = grupo_simetrico(3)
        self.assertEqual(s3.ordem(), 6)

    def test_s3_nao_abeliano(self):
        s3 = grupo_simetrico(3)
        self.assertFalse(s3.eh_abeliano())

    def test_s2_abeliano(self):
        s2 = grupo_simetrico(2)
        self.assertTrue(s2.eh_abeliano())


class TestGrupoKlein(unittest.TestCase):

    def test_v4_ordem(self):
        v4 = grupo_klein()
        self.assertEqual(v4.ordem(), 4)

    def test_v4_abeliano(self):
        v4 = grupo_klein()
        self.assertTrue(v4.eh_abeliano())


class TestGrupoDiedral(unittest.TestCase):

    def test_d3_ordem(self):
        d3 = grupo_diedral(3)
        self.assertEqual(d3.ordem(), 6)


class TestLie(unittest.TestCase):

    def test_comutador_zero(self):
        # [A, A] = 0
        A = Matriz([['1', '2'], ['3', '4']])
        resultado, hist = comutador(A, A)
        for i in range(2):
            for j in range(2):
                self.assertEqual(float(resultado.elemento(i, j)), 0.0)

    def test_so3_geradores(self):
        Lx, Ly, Lz, hist = so3_geradores()
        self.assertEqual(Lx.linhas, 3)
        self.assertEqual(Ly.linhas, 3)
        self.assertEqual(Lz.linhas, 3)

    def test_so3_comutador_lx_ly(self):
        # [Lx, Ly] = Lz
        Lx, Ly, Lz, _ = so3_geradores()
        resultado, _ = comutador(Lx, Ly)
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(
                    float(resultado.elemento(i, j)),
                    float(Lz.elemento(i, j)),
                    places=5
                )

    def test_rotacao_2d_pi_2(self):
        R = rotacao_2d(math.pi / 2)
        # cos(π/2) ≈ 0, sin(π/2) ≈ 1
        self.assertAlmostEqual(float(R.elemento(0, 0)), 0.0, places=5)
        self.assertAlmostEqual(float(R.elemento(1, 0)), 1.0, places=5)

    def test_exponencial_matriz_nula(self):
        # exp(0) = I
        zero = Matriz([['0', '0'], ['0', '0']])
        resultado, hist = exponencial_matricial(zero, n_termos=5)
        self.assertAlmostEqual(float(resultado.elemento(0, 0)), 1.0)
        self.assertAlmostEqual(float(resultado.elemento(1, 1)), 1.0)
        self.assertAlmostEqual(float(resultado.elemento(0, 1)), 0.0)

    def test_gram_schmidt(self):
        vetores = [['1', '1'], ['1', '0']]
        ortonormais, hist = gram_schmidt(vetores)
        self.assertEqual(len(ortonormais), 2)
        # Verificar ortogonalidade: dot product ≈ 0
        dot = sum(float(a) * float(b) for a, b in zip(ortonormais[0], ortonormais[1]))
        self.assertAlmostEqual(dot, 0.0, places=5)


if __name__ == "__main__":
    unittest.main()
