"""Cálculo de autovalores e autovetores com passo-a-passo pedagógico."""

from engine.basic.operacoes_basicas import soma, diff, multi, div, reduz_fracao
from engine.basic.passo import Passo, Historico
from engine.algebra.equacao import Equacao2Grau
from engine.algebra_linear.matriz import Matriz


def autovalores_2x2(m: Matriz) -> tuple:
    """Calcula autovalores de matriz 2x2.

    1. Montar polinômio característico: det(A - lambda*I) = 0
    2. Resolver equação quadrática (usando Equacao2Grau)
    3. Retorna (autovalores: list, historico: Historico)
    """
    if m.linhas != 2 or m.colunas != 2:
        raise ValueError(
            f"Esta função é para matrizes 2x2. Dimensões: {m.linhas}x{m.colunas}"
        )

    historico = Historico(verbosidade=3)
    a, b_mat = m.dados[0][0], m.dados[0][1]
    c, d = m.dados[1][0], m.dados[1][1]

    historico.adicionar(Passo(
        nivel=1,
        descricao='Calcular autovalores da matriz 2x2',
        latex_antes=m.representacao_latex(),
        regra='Autovalores'
    ))

    # det(A - lambda*I) = 0
    # |a - lambda    b      |
    # |c            d-lambda | = 0
    #
    # (a - lambda)(d - lambda) - bc = 0
    # lambda^2 - (a+d)*lambda + (ad - bc) = 0
    #
    # Coeficientes da equação quadrática:
    # a_eq = 1
    # b_eq = -(a + d)  (negativo do traço)
    # c_eq = ad - bc   (determinante)

    traco = soma(a, d)
    det_valor = diff(multi(a, d), multi(b_mat, c))

    # b_eq = -(a + d) = multi('-1', traco)
    b_eq = multi('-1', traco)

    historico.adicionar(Passo(
        nivel=2,
        descricao=(
            f'Polinômio característico: lambda^2 - tr(A)*lambda + det(A) = 0\n'
            f'  tr(A) = {a} + {d} = {traco}\n'
            f'  det(A) = {a}*{d} - {b_mat}*{c} = {det_valor}'
        ),
        latex_antes='\\det(A - \\lambda I) = 0',
        latex_depois=f'\\lambda^2 + ({b_eq})\\lambda + {det_valor} = 0',
        regra='Polinômio característico'
    ))

    # Resolver lambda^2 + b_eq*lambda + det_valor = 0
    eq = Equacao2Grau('1', b_eq, det_valor)
    autovalores, hist_eq = eq.resolver()

    # Incorporar passos da equação
    for passo in hist_eq.todos():
        historico.adicionar(passo)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Autovalores: {", ".join(av.representacao_latex() for av in autovalores)}',
        regra='Resultado final'
    ))

    return (autovalores, historico)


def autovetores_2x2(m: Matriz, autovalor: str) -> list[str]:
    """Calcula autovetores para um dado autovalor em uma matriz 2x2.

    Resolve (A - lambda*I)v = 0 e retorna o autovetor como lista de strings.
    """
    if m.linhas != 2 or m.colunas != 2:
        raise ValueError(
            f"Esta função é para matrizes 2x2. Dimensões: {m.linhas}x{m.colunas}"
        )

    a, b_mat = m.dados[0][0], m.dados[0][1]
    c, d = m.dados[1][0], m.dados[1][1]

    # A - lambda*I
    a11 = diff(a, autovalor)
    a12 = b_mat
    a21 = c
    a22 = diff(d, autovalor)

    # Usar a primeira linha: a11*v1 + a12*v2 = 0
    # Se a12 != 0: v1 = -a12, v2 = a11 (ou equivalente)
    # Se a12 == 0 e a11 == 0: usar segunda linha
    # Se a11 != 0 e a12 == 0: v = (0, 1) vetor trivial

    if a12 != '0':
        # v1/v2 = -a12/a11 nao, v1 = -a12, v2 = a11
        return [multi('-1', a12), a11]
    elif a11 == '0':
        # Primeira linha inteira zero, usar segunda
        if a22 != '0':
            return [multi('-1', a22), a21]
        else:
            # Matriz A - lambda*I é zero: qualquer vetor é autovetor
            return ['1', '0']
    else:
        # a12 == 0 e a11 != 0: v1 = 0
        return ['0', '1']
