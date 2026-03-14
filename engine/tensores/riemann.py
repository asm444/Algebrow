"""Tensor de Riemann, Ricci, escalar de curvatura e tensor de Einstein."""

from engine.calculo.arvore import NoExpressao, num, var, op
from engine.calculo.multivariavel import derivada_parcial
from engine.calculo.derivada import simplificar_no
from engine.basic.passo import Passo, Historico
from engine.tensores.tensor_metrico import TensorMetrico
from engine.tensores.christoffel import christoffel_2especie


def riemann(metrica: TensorMetrico) -> tuple:
    """R^i_jkl = dGamma^i_jl/dx^k - dGamma^i_jk/dx^l
                 + Gamma^i_mk Gamma^m_jl - Gamma^i_ml Gamma^m_jk.

    Retorna (componentes: dict[(i,j,k,l), NoExpressao], Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Calculando tensor de Riemann',
        regra='Tensor de Riemann',
    ))

    n = metrica.dim
    coords = metrica.coords
    gamma, _ = christoffel_2especie(metrica)
    componentes = {}

    for i in range(n):
        for j in range(n):
            for k in range(n):
                for l in range(n):
                    g_ijl = gamma.get((i, j, l), num('0'))
                    g_ijk = gamma.get((i, j, k), num('0'))

                    # dGamma^i_jl / dx^k
                    dg_ijl_k = derivada_parcial(g_ijl, coords[k])
                    # dGamma^i_jk / dx^l
                    dg_ijk_l = derivada_parcial(g_ijk, coords[l])

                    # Somas com contracoes
                    soma1 = num('0')
                    soma2 = num('0')
                    for m in range(n):
                        g_imk = gamma.get((i, m, k), num('0'))
                        g_mjl = gamma.get((m, j, l), num('0'))
                        g_iml = gamma.get((i, m, l), num('0'))
                        g_mjk = gamma.get((m, j, k), num('0'))
                        soma1 = simplificar_no(
                            op('+', soma1, simplificar_no(op('*', g_imk, g_mjl)))
                        )
                        soma2 = simplificar_no(
                            op('+', soma2, simplificar_no(op('*', g_iml, g_mjk)))
                        )

                    resultado = simplificar_no(
                        op('+',
                           simplificar_no(op('-', dg_ijl_k, dg_ijk_l)),
                           simplificar_no(op('-', soma1, soma2)))
                    )
                    componentes[(i, j, k, l)] = resultado

    historico.adicionar(Passo(
        nivel=1,
        descricao='Tensor de Riemann calculado',
        regra='Tensor de Riemann',
    ))

    return componentes, historico


def ricci(metrica: TensorMetrico) -> tuple:
    """R_jl = R^i_jil (contracao).

    Retorna (componentes: dict[(j,l), NoExpressao], Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Calculando tensor de Ricci via contracao do tensor de Riemann',
        regra='Tensor de Ricci',
    ))

    n = metrica.dim
    R, _ = riemann(metrica)
    componentes = {}

    for j in range(n):
        for l in range(n):
            soma = num('0')
            for i in range(n):
                soma = simplificar_no(op('+', soma, R[(i, j, i, l)]))
            componentes[(j, l)] = soma

    historico.adicionar(Passo(
        nivel=1,
        descricao='Tensor de Ricci calculado',
        regra='Tensor de Ricci',
    ))

    return componentes, historico


def escalar_curvatura(metrica: TensorMetrico) -> tuple:
    """R = g^{jl} R_{jl}.

    Retorna (R: NoExpressao, Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Calculando escalar de curvatura R = g^{jl} R_{jl}',
        regra='Escalar de curvatura',
    ))

    n = metrica.dim
    g_inv = metrica.inverso()
    R_jl, _ = ricci(metrica)
    resultado = num('0')

    for j in range(n):
        for l in range(n):
            termo = simplificar_no(op('*', g_inv.elemento(j, l), R_jl[(j, l)]))
            resultado = simplificar_no(op('+', resultado, termo))

    historico.adicionar(Passo(
        nivel=1,
        descricao='Escalar de curvatura calculado',
        latex_depois=resultado.representacao_latex(),
        regra='Escalar de curvatura',
    ))

    return resultado, historico


def einstein(metrica: TensorMetrico) -> tuple:
    """G_ij = R_ij - 1/2 R g_ij.

    Retorna (componentes: dict[(i,j), NoExpressao], Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Calculando tensor de Einstein G_ij = R_ij - 1/2 R g_ij',
        regra='Tensor de Einstein',
    ))

    n = metrica.dim
    R_ij, _ = ricci(metrica)
    R_escalar, _ = escalar_curvatura(metrica)
    componentes = {}

    meio_R = simplificar_no(op('*', op('/', num('1'), num('2')), R_escalar))

    for i in range(n):
        for j in range(n):
            termo = simplificar_no(
                op('-', R_ij[(i, j)],
                   simplificar_no(op('*', meio_R, metrica.g[i][j])))
            )
            componentes[(i, j)] = termo

    historico.adicionar(Passo(
        nivel=1,
        descricao='Tensor de Einstein calculado',
        regra='Tensor de Einstein',
    ))

    return componentes, historico
