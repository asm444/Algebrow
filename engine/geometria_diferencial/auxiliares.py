"""Funcoes auxiliares para algebra vetorial simbolica via NoExpressao."""

from engine.calculo.arvore import NoExpressao, num, op, func
from engine.calculo.derivada import simplificar_no


def produto_escalar(a: list[NoExpressao], b: list[NoExpressao]) -> NoExpressao:
    """Produto escalar simbolico: a . b = sum(ai * bi)."""
    if len(a) != len(b):
        raise ValueError('Vetores devem ter a mesma dimensao')

    resultado = simplificar_no(op('*', a[0], b[0]))
    for i in range(1, len(a)):
        termo = simplificar_no(op('*', a[i], b[i]))
        resultado = simplificar_no(op('+', resultado, termo))
    return resultado


def produto_vetorial(a: list[NoExpressao], b: list[NoExpressao]) -> list[NoExpressao]:
    """Produto vetorial simbolico (3D): a x b."""
    if len(a) != 3 or len(b) != 3:
        raise ValueError('Produto vetorial requer vetores 3D')

    # i = a1*b2 - a2*b1
    # j = a2*b0 - a0*b2
    # k = a0*b1 - a1*b0
    comp_i = simplificar_no(op('-', op('*', a[1], b[2]), op('*', a[2], b[1])))
    comp_j = simplificar_no(op('-', op('*', a[2], b[0]), op('*', a[0], b[2])))
    comp_k = simplificar_no(op('-', op('*', a[0], b[1]), op('*', a[1], b[0])))

    return [comp_i, comp_j, comp_k]


def norma(v: list[NoExpressao]) -> NoExpressao:
    """|v| = sqrt(sum(vi^2))."""
    soma = simplificar_no(op('^', v[0], num('2')))
    for i in range(1, len(v)):
        termo = simplificar_no(op('^', v[i], num('2')))
        soma = simplificar_no(op('+', soma, termo))
    return simplificar_no(func('sqrt', soma))


def norma_quadrada(v: list[NoExpressao]) -> NoExpressao:
    """|v|^2 = sum(vi^2) — sem raiz, util para evitar sqrt desnecessario."""
    soma = simplificar_no(op('^', v[0], num('2')))
    for i in range(1, len(v)):
        termo = simplificar_no(op('^', v[i], num('2')))
        soma = simplificar_no(op('+', soma, termo))
    return soma
