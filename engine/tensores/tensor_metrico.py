"""Tensor metrico e operacoes tensoriais."""

from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.multivariavel import derivada_parcial
from engine.calculo.derivada import simplificar_no
from engine.basic.passo import Passo, Historico


class TensorMetrico:
    """Tensor metrico g_ij para um sistema de coordenadas."""

    def __init__(self, componentes: list[list[NoExpressao]], coordenadas: list[str]):
        """componentes[i][j] = g_ij como NoExpressao. coordenadas = ['r','theta','phi'] etc."""
        self.g = componentes
        self.coords = coordenadas
        self.dim = len(coordenadas)
        if len(componentes) != self.dim:
            raise ValueError(f'Esperado {self.dim} linhas, recebeu {len(componentes)}')
        for i, linha in enumerate(componentes):
            if len(linha) != self.dim:
                raise ValueError(f'Linha {i} tem {len(linha)} colunas, esperado {self.dim}')

    def elemento(self, i: int, j: int) -> NoExpressao:
        """Retorna g_ij."""
        return self.g[i][j]

    def inverso(self) -> 'TensorMetrico':
        """g^{ij} -- inversa da matriz metrica.

        Para 2x2: g^{-1} = adj/det.
        Para 3x3: usar cofatores.
        Para 4x4: usar cofatores.
        """
        det = self.determinante()
        n = self.dim

        if n == 1:
            inv = [[simplificar_no(op('/', num('1'), self.g[0][0]))]]
            return TensorMetrico(inv, self.coords)

        # Calcular matriz de cofatores
        cofatores = [[None] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                menor = self._menor(i, j)
                sinal = num('1') if (i + j) % 2 == 0 else num('-1')
                cofatores[i][j] = simplificar_no(op('*', sinal, menor))

        # Transpor (adjunta) e dividir por determinante
        inv = [[None] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                inv[i][j] = simplificar_no(op('/', cofatores[j][i], det))

        return TensorMetrico(inv, self.coords)

    def _menor(self, linha: int, coluna: int) -> NoExpressao:
        """Determinante da submatriz obtida removendo linha e coluna."""
        n = self.dim
        sub = []
        for i in range(n):
            if i == linha:
                continue
            row = []
            for j in range(n):
                if j == coluna:
                    continue
                row.append(self.g[i][j])
            sub.append(row)
        return _determinante_matriz(sub)

    def determinante(self) -> NoExpressao:
        """det(g_ij)."""
        return _determinante_matriz(self.g)

    def representacao_latex(self) -> str:
        """ds^2 = g_ij dx^i dx^j expandido."""
        termos = []
        for i in range(self.dim):
            for j in range(i, self.dim):
                gij = self.g[i][j]
                # Pular zeros
                if gij.tipo == 'numero' and gij.valor == '0':
                    continue
                dxi = f'd{self.coords[i]}'
                dxj = f'd{self.coords[j]}'
                coef = gij.representacao_latex()
                if i == j:
                    if coef == '1':
                        termos.append(f'{dxi}^2')
                    else:
                        termos.append(f'{coef} \\, {dxi}^2')
                else:
                    fator = '2' if coef == '1' else f'2 {coef}'
                    termos.append(f'{fator} \\, {dxi} \\, {dxj}')
        return 'ds^2 = ' + ' + '.join(termos) if termos else 'ds^2 = 0'


def _determinante_matriz(m: list[list[NoExpressao]]) -> NoExpressao:
    """Calcula determinante de uma matriz de NoExpressao (recursivo)."""
    n = len(m)
    if n == 1:
        return m[0][0]
    if n == 2:
        # ad - bc
        ad = op('*', m[0][0], m[1][1])
        bc = op('*', m[0][1], m[1][0])
        return simplificar_no(op('-', ad, bc))

    # Expansao por cofatores na primeira linha
    resultado = num('0')
    for j in range(n):
        # Submatriz
        sub = []
        for i in range(1, n):
            row = []
            for k in range(n):
                if k == j:
                    continue
                row.append(m[i][k])
            sub.append(row)
        cofator = _determinante_matriz(sub)
        sinal = num('1') if j % 2 == 0 else num('-1')
        termo = simplificar_no(op('*', op('*', sinal, m[0][j]), cofator))
        resultado = simplificar_no(op('+', resultado, termo))
    return resultado


# ---------------------------------------------------------------------------
# Metricas classicas
# ---------------------------------------------------------------------------

def metrica_plana_2d() -> TensorMetrico:
    """ds^2 = dx^2 + dy^2."""
    return TensorMetrico(
        [[num('1'), num('0')],
         [num('0'), num('1')]],
        ['x', 'y'],
    )


def metrica_polar() -> TensorMetrico:
    """ds^2 = dr^2 + r^2 d(theta)^2."""
    r = var('r')
    return TensorMetrico(
        [[num('1'), num('0')],
         [num('0'), op('^', r, num('2'))]],
        ['r', 'theta'],
    )


def metrica_esferica() -> TensorMetrico:
    """ds^2 = dr^2 + r^2 d(theta)^2 + r^2 sin^2(theta) d(phi)^2."""
    r = var('r')
    theta = var('theta')
    r2 = op('^', r, num('2'))
    r2_sin2 = op('*', r2, op('^', func('sin', theta), num('2')))
    return TensorMetrico(
        [[num('1'), num('0'), num('0')],
         [num('0'), r2, num('0')],
         [num('0'), num('0'), r2_sin2]],
        ['r', 'theta', 'phi'],
    )


def metrica_schwarzschild(M: str = 'M') -> TensorMetrico:
    """ds^2 = -(1-2M/r)dt^2 + (1-2M/r)^{-1}dr^2 + r^2 dOmega^2.

    Coordenadas: [t, r, theta, phi].
    """
    r = var('r')
    theta = var('theta')
    mass = var(M)

    # f = 1 - 2M/r
    f = op('-', num('1'), op('/', op('*', num('2'), mass), r))
    neg_f = op('*', num('-1'), f)
    inv_f = op('/', num('1'), f)
    r2 = op('^', r, num('2'))
    r2_sin2 = op('*', r2, op('^', func('sin', theta), num('2')))

    return TensorMetrico(
        [[neg_f, num('0'), num('0'), num('0')],
         [num('0'), inv_f, num('0'), num('0')],
         [num('0'), num('0'), r2, num('0')],
         [num('0'), num('0'), num('0'), r2_sin2]],
        ['t', 'r', 'theta', 'phi'],
    )
