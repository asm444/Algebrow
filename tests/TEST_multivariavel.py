"""Testes do modulo de calculo multivariavel."""

import pytest
from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.multivariavel import (
    derivada_parcial,
    gradiente,
    divergente,
    rotacional,
    laplaciano,
    hessiana,
    jacobiana,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _avaliar(no: NoExpressao, vals: dict) -> float:
    """Avalia no numericamente."""
    return no.avaliar(vals)


# ---------------------------------------------------------------------------
# Derivada parcial
# ---------------------------------------------------------------------------

class TestDerivadaParcial:
    def test_x2y_em_x(self):
        """∂(x²y)/∂x = 2xy"""
        # x^2 * y
        f = op('*', op('^', var('x'), num('2')), var('y'))
        resultado = derivada_parcial(f, 'x')
        # Avaliar em x=3, y=5 → 2*3*5 = 30
        assert abs(_avaliar(resultado, {'x': 3, 'y': 5}) - 30.0) < 1e-9

    def test_x2y_em_y(self):
        """∂(x²y)/∂y = x²"""
        f = op('*', op('^', var('x'), num('2')), var('y'))
        resultado = derivada_parcial(f, 'y')
        # Avaliar em x=3, y=5 → 9
        assert abs(_avaliar(resultado, {'x': 3, 'y': 5}) - 9.0) < 1e-9

    def test_constante(self):
        """∂(5)/∂x = 0"""
        f = num('5')
        resultado = derivada_parcial(f, 'x')
        assert abs(_avaliar(resultado, {'x': 1}) - 0.0) < 1e-9

    def test_variavel_independente(self):
        """∂(y)/∂x = 0"""
        f = var('y')
        resultado = derivada_parcial(f, 'x')
        assert abs(_avaliar(resultado, {'x': 1, 'y': 2}) - 0.0) < 1e-9


# ---------------------------------------------------------------------------
# Gradiente
# ---------------------------------------------------------------------------

class TestGradiente:
    def test_x2_mais_y2(self):
        """∇(x² + y²) = (2x, 2y)"""
        f = op('+', op('^', var('x'), num('2')), op('^', var('y'), num('2')))
        grad, hist = gradiente(f, ['x', 'y'])

        assert len(grad) == 2
        # Em x=3, y=4: grad = (6, 8)
        assert abs(_avaliar(grad[0], {'x': 3, 'y': 4}) - 6.0) < 1e-9
        assert abs(_avaliar(grad[1], {'x': 3, 'y': 4}) - 8.0) < 1e-9
        assert len(hist) > 0

    def test_gradiente_3d(self):
        """∇(xyz) = (yz, xz, xy)"""
        f = op('*', op('*', var('x'), var('y')), var('z'))
        grad, hist = gradiente(f, ['x', 'y', 'z'])

        vals = {'x': 2, 'y': 3, 'z': 5}
        # ∂(xyz)/∂x = yz = 15
        assert abs(_avaliar(grad[0], vals) - 15.0) < 1e-9
        # ∂(xyz)/∂y = xz = 10
        assert abs(_avaliar(grad[1], vals) - 10.0) < 1e-9
        # ∂(xyz)/∂z = xy = 6
        assert abs(_avaliar(grad[2], vals) - 6.0) < 1e-9


# ---------------------------------------------------------------------------
# Divergente
# ---------------------------------------------------------------------------

class TestDivergente:
    def test_campo_identidade(self):
        """div(x, y, z) = 1 + 1 + 1 = 3"""
        campo = [var('x'), var('y'), var('z')]
        resultado, hist = divergente(campo, ['x', 'y', 'z'])
        # Deve ser constante = 3
        assert abs(_avaliar(resultado, {'x': 0, 'y': 0, 'z': 0}) - 3.0) < 1e-9

    def test_campo_quadratico(self):
        """div(x², y², z²) = 2x + 2y + 2z"""
        campo = [
            op('^', var('x'), num('2')),
            op('^', var('y'), num('2')),
            op('^', var('z'), num('2')),
        ]
        resultado, hist = divergente(campo, ['x', 'y', 'z'])
        # Em (1,2,3): 2+4+6 = 12
        assert abs(_avaliar(resultado, {'x': 1, 'y': 2, 'z': 3}) - 12.0) < 1e-9

    def test_tamanho_diferente_erro(self):
        """Deve dar erro se campo e variaveis tem tamanhos diferentes."""
        with pytest.raises(ValueError):
            divergente([var('x'), var('y')], ['x', 'y', 'z'])


# ---------------------------------------------------------------------------
# Rotacional
# ---------------------------------------------------------------------------

class TestRotacional:
    def test_campo_y_negx_0(self):
        """rot(y, -x, 0) = (0, 0, -2)"""
        campo = [var('y'), op('*', num('-1'), var('x')), num('0')]
        resultado, hist = rotacional(campo, ['x', 'y', 'z'])

        vals = {'x': 1, 'y': 2, 'z': 3}
        # Componente i: ∂0/∂y - ∂(-x)/∂z = 0 - 0 = 0
        assert abs(_avaliar(resultado[0], vals) - 0.0) < 1e-9
        # Componente j: ∂y/∂z - ∂0/∂x = 0 - 0 = 0
        assert abs(_avaliar(resultado[1], vals) - 0.0) < 1e-9
        # Componente k: ∂(-x)/∂x - ∂y/∂y = -1 - 1 = -2
        assert abs(_avaliar(resultado[2], vals) - (-2.0)) < 1e-9

    def test_campo_nulo(self):
        """rot(0, 0, 0) = (0, 0, 0)"""
        campo = [num('0'), num('0'), num('0')]
        resultado, hist = rotacional(campo, ['x', 'y', 'z'])
        vals = {'x': 0, 'y': 0, 'z': 0}
        for comp in resultado:
            assert abs(_avaliar(comp, vals) - 0.0) < 1e-9


# ---------------------------------------------------------------------------
# Laplaciano
# ---------------------------------------------------------------------------

class TestLaplaciano:
    def test_x2_mais_y2(self):
        """Δ(x² + y²) = 2 + 2 = 4"""
        f = op('+', op('^', var('x'), num('2')), op('^', var('y'), num('2')))
        resultado, hist = laplaciano(f, ['x', 'y'])
        assert abs(_avaliar(resultado, {'x': 0, 'y': 0}) - 4.0) < 1e-9

    def test_x3(self):
        """Δ(x³) em relacao a [x] = 6x"""
        f = op('^', var('x'), num('3'))
        resultado, hist = laplaciano(f, ['x'])
        # Em x=2: 6*2 = 12
        assert abs(_avaliar(resultado, {'x': 2}) - 12.0) < 1e-9


# ---------------------------------------------------------------------------
# Jacobiana
# ---------------------------------------------------------------------------

class TestJacobiana:
    def test_jacobiana_2x2(self):
        """Jacobiana de (x², xy) em relacao a (x, y)."""
        funcoes = [
            op('^', var('x'), num('2')),       # x²
            op('*', var('x'), var('y')),        # xy
        ]
        J, hist = jacobiana(funcoes, ['x', 'y'])

        vals = {'x': 3, 'y': 5}
        # J[0][0] = ∂(x²)/∂x = 2x = 6
        assert abs(_avaliar(J[0][0], vals) - 6.0) < 1e-9
        # J[0][1] = ∂(x²)/∂y = 0
        assert abs(_avaliar(J[0][1], vals) - 0.0) < 1e-9
        # J[1][0] = ∂(xy)/∂x = y = 5
        assert abs(_avaliar(J[1][0], vals) - 5.0) < 1e-9
        # J[1][1] = ∂(xy)/∂y = x = 3
        assert abs(_avaliar(J[1][1], vals) - 3.0) < 1e-9


# ---------------------------------------------------------------------------
# Hessiana
# ---------------------------------------------------------------------------

class TestHessiana:
    def test_x2_xy_y2(self):
        """Hessiana de x² + xy + y²:
        H = [[2, 1],
             [1, 2]]
        """
        # f = x² + xy + y²
        f = op('+',
               op('+',
                  op('^', var('x'), num('2')),
                  op('*', var('x'), var('y'))),
               op('^', var('y'), num('2')))

        H, hist = hessiana(f, ['x', 'y'])

        vals = {'x': 0, 'y': 0}
        # H[0][0] = ∂²f/∂x² = 2
        assert abs(_avaliar(H[0][0], vals) - 2.0) < 1e-9
        # H[0][1] = ∂²f/∂x∂y = 1
        assert abs(_avaliar(H[0][1], vals) - 1.0) < 1e-9
        # H[1][0] = ∂²f/∂y∂x = 1
        assert abs(_avaliar(H[1][0], vals) - 1.0) < 1e-9
        # H[1][1] = ∂²f/∂y² = 2
        assert abs(_avaliar(H[1][1], vals) - 2.0) < 1e-9

    def test_hessiana_simetrica(self):
        """Hessiana deve ser simetrica para funcoes C²."""
        f = op('*', op('^', var('x'), num('2')), var('y'))  # x²y
        H, hist = hessiana(f, ['x', 'y'])

        vals = {'x': 2, 'y': 3}
        # H[0][1] deve ser igual a H[1][0]
        h01 = _avaliar(H[0][1], vals)
        h10 = _avaliar(H[1][0], vals)
        assert abs(h01 - h10) < 1e-9
