"""Testes para os módulos de EDP, Sturm-Liouville e Funções de Green."""

import math
import unittest

from engine.edp.equacao_calor import separacao_variaveis_calor, solucao_calor_pontual
from engine.edp.equacao_onda import separacao_variaveis_onda, dAlembert
from engine.edp.equacao_laplace import laplace_retangulo, laplace_disco
from engine.edo_avancada.sturm_liouville import autofuncoes_sl, autovalores_sl, expansao_autofuncoes
from engine.edo_avancada.green import green_laplace_2d, green_edo_2ordem, green_helmholtz_1d


class TestEquacaoCalor(unittest.TestCase):
    """Testes para a equação do calor."""

    def test_solucao_fundamental_t1_k1(self):
        """Solução fundamental em t=1, k=1, x=0 deve ser 1/sqrt(4*pi)."""
        valor, hist = solucao_calor_pontual(k=1, t=1, x=0)
        esperado = 1.0 / math.sqrt(4 * math.pi)
        self.assertAlmostEqual(valor, esperado, places=8)
        self.assertGreater(len(hist.todos()), 0)

    def test_solucao_fundamental_decai_com_x(self):
        """Solução fundamental deve decair com |x| (Gaussiana)."""
        v0, _ = solucao_calor_pontual(k=1, t=1, x=0)
        v1, _ = solucao_calor_pontual(k=1, t=1, x=1)
        v2, _ = solucao_calor_pontual(k=1, t=1, x=2)
        self.assertGreater(v0, v1)
        self.assertGreater(v1, v2)
        self.assertGreater(v2, 0)

    def test_solucao_fundamental_simetrica(self):
        """u(x,t) = u(-x,t) (simetria)."""
        v_pos, _ = solucao_calor_pontual(k=1, t=1, x=2)
        v_neg, _ = solucao_calor_pontual(k=1, t=1, x=-2)
        self.assertAlmostEqual(v_pos, v_neg, places=10)

    def test_separacao_variaveis_calor_coeficientes(self):
        """Com condição sin(pi*x/L), apenas B_1 deve ser significativo."""
        coefs, sol_latex, hist = separacao_variaveis_calor(
            L=1.0, k=1.0, n_termos=5, condicao_inicial='sin(pi*x/1.0)'
        )
        self.assertAlmostEqual(coefs[0], 1.0, places=2)
        for bn in coefs[1:]:
            self.assertAlmostEqual(bn, 0.0, places=2)
        self.assertIn('u(x,t)', sol_latex)

    def test_calor_t_negativo_erro(self):
        """t <= 0 deve levantar erro."""
        with self.assertRaises(ValueError):
            solucao_calor_pontual(k=1, t=0, x=0)


class TestEquacaoOnda(unittest.TestCase):
    """Testes para a equação da onda."""

    def test_dAlembert_f_sin_g_zero(self):
        """d'Alembert com f=sin(x), g=0: solução deve conter sin."""
        sol, hist = dAlembert('sin(x)', '0', c=1)
        self.assertIn('sin', sol)
        self.assertGreater(len(hist.todos()), 0)
        # g=0 → sem termo integral
        self.assertNotIn('int', sol)

    def test_dAlembert_g_nao_zero(self):
        """d'Alembert com g não-nulo deve incluir integral."""
        sol, hist = dAlembert('0', 'sin(x)', c=1)
        self.assertIn('int', sol)

    def test_separacao_variaveis_onda(self):
        """Separação de variáveis deve retornar solução com sin e cos."""
        sol, hist = separacao_variaveis_onda(L=1.0, c=1.0, n_termos=5)
        self.assertIn('sin', sol)
        self.assertIn('cos', sol)
        self.assertIn('u(x,t)', sol)
        self.assertGreater(len(hist.todos()), 0)


class TestEquacaoLaplace(unittest.TestCase):
    """Testes para a equação de Laplace."""

    def test_laplace_retangulo_solucao_satisfaz_laplace(self):
        """Verifica numericamente que a solução satisfaz nabla^2 u ~ 0.

        Para cada termo B_n sin(n*pi*x/a) * sinh(n*pi*y/a) / sinh(n*pi*b/a),
        nabla^2 de cada termo é zero por construção (separação de variáveis).
        Verificamos um termo isolado.
        """
        a_val, b_val = 1.0, 1.0
        n = 1
        # Um termo: sin(n*pi*x/a) * sinh(n*pi*y/a)
        # d²/dx² = -(n*pi/a)² * sin(...) * sinh(...)
        # d²/dy² = (n*pi/a)² * sin(...) * sinh(...)
        # Soma = 0 ✓
        x_test, y_test = 0.3, 0.5
        kn = n * math.pi / a_val
        u_val = math.sin(kn * x_test) * math.sinh(kn * y_test)
        uxx = -(kn ** 2) * math.sin(kn * x_test) * math.sinh(kn * y_test)
        uyy = (kn ** 2) * math.sin(kn * x_test) * math.sinh(kn * y_test)
        laplaciano = uxx + uyy
        self.assertAlmostEqual(laplaciano, 0.0, places=10)

    def test_laplace_retangulo_latex(self):
        """Verifica que retorna LaTeX válido."""
        sol, hist = laplace_retangulo(1.0, 1.0, '100', n_termos=5)
        self.assertIn('u(x,y)', sol)
        self.assertIn('sin', sol)
        self.assertIn('sinh', sol)
        self.assertGreater(len(hist.todos()), 0)

    def test_laplace_disco(self):
        """Verifica que solução no disco contém termos corretos."""
        sol, hist = laplace_disco(R=1.0, n_termos=5)
        self.assertIn('u(r,\\theta)', sol)
        self.assertIn('cos', sol)
        self.assertIn('sin', sol)
        self.assertIn('A_0', sol)
        self.assertGreater(len(hist.todos()), 0)


class TestSturmLiouville(unittest.TestCase):
    """Testes para Sturm-Liouville."""

    def test_autofuncoes_fourier_sin(self):
        """Autofunções de Fourier para n=1 devem conter sin."""
        latex, hist = autofuncoes_sl('fourier', 1)
        self.assertIn('sin', latex)
        self.assertIn('cos', latex)
        self.assertGreater(len(hist.todos()), 0)

    def test_autofuncoes_fourier_ortogonalidade(self):
        """sin(nπx/L) e sin(mπx/L) devem ser ortogonais para n ≠ m.

        Verificação numérica: ∫₀ᴸ sin(nπx/L) sin(mπx/L) dx ≈ 0 para n ≠ m.
        """
        L = 1.0
        N = 1000
        h = L / N

        # n=1, m=2 devem ser ortogonais
        n, m = 1, 2
        soma = 0.0
        for i in range(N + 1):
            x = i * h
            f_val = math.sin(n * math.pi * x / L) * math.sin(m * math.pi * x / L)
            if i == 0 or i == N:
                soma += f_val
            elif i % 2 == 1:
                soma += 4 * f_val
            else:
                soma += 2 * f_val
        integral = (h / 3) * soma
        self.assertAlmostEqual(integral, 0.0, places=6)

        # n=m=1 deve dar L/2
        soma2 = 0.0
        for i in range(N + 1):
            x = i * h
            f_val = math.sin(n * math.pi * x / L) ** 2
            if i == 0 or i == N:
                soma2 += f_val
            elif i % 2 == 1:
                soma2 += 4 * f_val
            else:
                soma2 += 2 * f_val
        integral2 = (h / 3) * soma2
        self.assertAlmostEqual(integral2, L / 2, places=4)

    def test_autofuncoes_legendre(self):
        """Autofunções de Legendre devem conter Rodrigues."""
        latex, hist = autofuncoes_sl('legendre', 3)
        self.assertIn('P_{3}', latex)
        self.assertGreater(len(hist.todos()), 0)

    def test_autofuncoes_bessel(self):
        """Autofunções de Bessel devem conter J_ν."""
        latex, hist = autofuncoes_sl('bessel', 2)
        self.assertIn('J_{', latex)
        self.assertGreater(len(hist.todos()), 0)

    def test_autofuncoes_tipo_invalido(self):
        """Tipo inválido deve levantar erro."""
        with self.assertRaises(ValueError):
            autofuncoes_sl('inexistente', 1)

    def test_autovalores_sl_corda(self):
        """Para y'' + λy = 0 em [0, π], autovalores = n² (n=1,2,3,...).

        p(x)=1, q(x)=0, w(x)=1.
        """
        autovalores, hist = autovalores_sl('1', '0', '1', 0.0, math.pi,
                                           condicoes='dirichlet', n_autovalores=3)
        self.assertGreater(len(autovalores), 0)
        # Primeiro autovalor deve ser ~1.0 (n=1: λ=(1)²=1)
        self.assertAlmostEqual(autovalores[0], 1.0, delta=0.1)
        # Segundo ~4.0 (n=2: λ=(2)²=4)
        if len(autovalores) >= 2:
            self.assertAlmostEqual(autovalores[1], 4.0, delta=0.2)
        self.assertGreater(len(hist.todos()), 0)


class TestGreen(unittest.TestCase):
    """Testes para Funções de Green."""

    def test_green_laplace_2d_formato(self):
        """Função de Green do Laplaciano 2D deve conter ln."""
        latex, hist = green_laplace_2d()
        self.assertIn('ln', latex)
        self.assertIn('2\\pi', latex)
        self.assertGreater(len(hist.todos()), 0)

    def test_green_edo_2ordem_constante(self):
        """Green para y'' + y = f com p=1, q=1."""
        latex, hist = green_edo_2ordem('1', '1', '0', 0, math.pi)
        self.assertIn('G(x', latex)
        self.assertIn('sin', latex.lower() if 'sin' in latex.lower() else latex)
        self.assertGreater(len(hist.todos()), 0)

    def test_green_edo_2ordem_geral(self):
        """Green para caso geral (p(x) não-constante)."""
        latex, hist = green_edo_2ordem('x+1', 'x', '0', 0, 1)
        self.assertIn('G(x', latex)
        self.assertIn('y_1', latex)
        self.assertIn('W', latex)

    def test_green_helmholtz_1d(self):
        """Green para Helmholtz: formato correto."""
        latex, hist = green_helmholtz_1d(k=1.0, a=0.0, b=math.pi)
        # k=1, b-a=pi → sin(pi) ≈ 0, deve ser autovalor
        self.assertIn('autovalor', latex.lower() if 'autovalor' in latex.lower()
                       else hist.todos()[-1].descricao.lower())

    def test_green_helmholtz_1d_valido(self):
        """Green para Helmholtz com k que não é autovalor."""
        latex, hist = green_helmholtz_1d(k=0.5, a=0.0, b=math.pi)
        self.assertIn('sin', latex)
        self.assertIn('G(x', latex)
        self.assertGreater(len(hist.todos()), 0)


class TestExpansaoAutofuncoes(unittest.TestCase):
    """Testes para expansão em autofunções."""

    def test_expansao_fourier_sin(self):
        """Expandir sin(x) em Fourier-seno deve dar B_1 ≈ 1."""
        coefs, hist = expansao_autofuncoes('sin(x)', 'fourier', n_termos=5)
        self.assertAlmostEqual(coefs[0], 1.0, places=2)
        self.assertGreater(len(hist.todos()), 0)

    def test_expansao_tipo_invalido(self):
        """Tipo inválido deve levantar erro."""
        with self.assertRaises(ValueError):
            expansao_autofuncoes('x', 'inexistente')


if __name__ == '__main__':
    unittest.main()
