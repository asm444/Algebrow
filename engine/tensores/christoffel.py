"""Simbolos de Christoffel."""

from engine.calculo.arvore import NoExpressao, num, var, op
from engine.calculo.multivariavel import derivada_parcial
from engine.calculo.derivada import simplificar_no
from engine.basic.passo import Passo, Historico
from engine.tensores.tensor_metrico import TensorMetrico


def christoffel_1especie(metrica: TensorMetrico) -> tuple:
    """Gamma_{kij} = 1/2 (dg_{ik}/dx^j + dg_{jk}/dx^i - dg_{ij}/dx^k).

    Retorna (componentes: dict[(k,i,j), NoExpressao], Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Calculando simbolos de Christoffel de 1a especie',
        regra='Christoffel 1a especie',
    ))

    n = metrica.dim
    coords = metrica.coords
    g = metrica.g
    componentes = {}

    for k in range(n):
        for i in range(n):
            for j in range(i, n):  # simetria em i,j
                # dg_ik/dx^j
                dg_ik_j = derivada_parcial(g[i][k], coords[j])
                # dg_jk/dx^i
                dg_jk_i = derivada_parcial(g[j][k], coords[i])
                # dg_ij/dx^k
                dg_ij_k = derivada_parcial(g[i][j], coords[k])

                soma = simplificar_no(op('+', dg_ik_j, dg_jk_i))
                diff = simplificar_no(op('-', soma, dg_ij_k))
                resultado = simplificar_no(op('*', op('/', num('1'), num('2')), diff))

                componentes[(k, i, j)] = resultado
                if i != j:
                    componentes[(k, j, i)] = resultado  # simetria

                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'Gamma_{{{coords[k]},{coords[i]},{coords[j]}}} calculado',
                    latex_depois=resultado.representacao_latex(),
                    regra='Christoffel 1a especie',
                ))

    return componentes, historico


def christoffel_2especie(metrica: TensorMetrico) -> tuple:
    """Gamma^k_ij = 1/2 g^{kl} (dg_{il}/dx^j + dg_{jl}/dx^i - dg_{ij}/dx^l).

    Retorna (componentes: dict[(k,i,j), NoExpressao], Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Calculando simbolos de Christoffel de 2a especie',
        regra='Christoffel 2a especie',
    ))

    n = metrica.dim
    coords = metrica.coords
    g = metrica.g
    g_inv = metrica.inverso()
    componentes = {}

    for k in range(n):
        for i in range(n):
            for j in range(i, n):  # simetria em i,j
                soma_total = num('0')
                for l in range(n):
                    g_kl = g_inv.elemento(k, l)

                    # dg_il/dx^j
                    dg_il_j = derivada_parcial(g[i][l], coords[j])
                    # dg_jl/dx^i
                    dg_jl_i = derivada_parcial(g[j][l], coords[i])
                    # dg_ij/dx^l
                    dg_ij_l = derivada_parcial(g[i][j], coords[l])

                    # parentese = dg_il_j + dg_jl_i - dg_ij_l
                    parentese = simplificar_no(
                        op('-', simplificar_no(op('+', dg_il_j, dg_jl_i)), dg_ij_l)
                    )
                    termo = simplificar_no(op('*', g_kl, parentese))
                    soma_total = simplificar_no(op('+', soma_total, termo))

                resultado = simplificar_no(op('*', op('/', num('1'), num('2')), soma_total))
                componentes[(k, i, j)] = resultado
                if i != j:
                    componentes[(k, j, i)] = resultado  # simetria

                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'Gamma^{coords[k]}_{{{coords[i]}{coords[j]}}} calculado',
                    latex_depois=resultado.representacao_latex(),
                    regra='Christoffel 2a especie',
                ))

    return componentes, historico


def geodesica_equacao(metrica: TensorMetrico) -> tuple:
    """Equacao geodesica: d^2x^k/ds^2 + Gamma^k_ij dx^i/ds dx^j/ds = 0.

    Retorna (equacoes_latex: list[str], Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Gerando equacoes geodesicas',
        regra='Equacao geodesica',
    ))

    gamma, _ = christoffel_2especie(metrica)
    n = metrica.dim
    coords = metrica.coords
    equacoes = []

    for k in range(n):
        termos = []
        for i in range(n):
            for j in range(n):
                g_kij = gamma.get((k, i, j), num('0'))
                # Pular termos zero
                if g_kij.tipo == 'numero' and g_kij.valor == '0':
                    continue
                latex_g = g_kij.representacao_latex()
                termos.append(
                    f'{latex_g} \\dot{{{coords[i]}}} \\dot{{{coords[j]}}}'
                )

        eq = f'\\ddot{{{coords[k]}}}'
        if termos:
            eq += ' + ' + ' + '.join(termos)
        eq += ' = 0'
        equacoes.append(eq)

        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Equacao geodesica para {coords[k]}',
            latex_depois=eq,
            regra='Equacao geodesica',
        ))

    return equacoes, historico
