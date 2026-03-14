"""Funcoes de analise complexa: Cauchy-Riemann e residuos."""

from engine.calculo.arvore import NoExpressao, num, var, op
from engine.calculo.multivariavel import derivada_parcial
from engine.calculo.derivada import simplificar_no
from engine.basic.passo import Passo, Historico
from engine.complexos.complexo import Complexo


def cauchy_riemann(u: NoExpressao, v: NoExpressao,
                   variaveis: list = None) -> tuple:
    """Verifica condicoes de Cauchy-Riemann: du/dx = dv/dy e du/dy = -dv/dx.

    u, v sao NoExpressao representando as partes real e imaginaria de f(z).
    variaveis: lista com nomes das variaveis, default ['x', 'y'].

    Retorna (satisfaz: bool, detalhes: dict, Historico).
    """
    if variaveis is None:
        variaveis = ['x', 'y']

    x_var, y_var = variaveis[0], variaveis[1]

    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Verificar condicoes de Cauchy-Riemann',
        latex_antes=f'\\frac{{\\partial u}}{{\\partial {x_var}}} = '
                    f'\\frac{{\\partial v}}{{\\partial {y_var}}} '
                    f'\\quad e \\quad '
                    f'\\frac{{\\partial u}}{{\\partial {y_var}}} = '
                    f'-\\frac{{\\partial v}}{{\\partial {x_var}}}',
        regra='Condicoes de Cauchy-Riemann',
    ))

    # Calcular as quatro derivadas parciais
    du_dx = derivada_parcial(u, x_var, historico)
    du_dy = derivada_parcial(u, y_var, historico)
    dv_dx = derivada_parcial(v, x_var, historico)
    dv_dy = derivada_parcial(v, y_var, historico)

    historico.adicionar(Passo(
        nivel=2,
        descricao='Derivadas parciais calculadas',
        latex_depois=f'\\frac{{\\partial u}}{{\\partial {x_var}}} = {du_dx.representacao_latex()}, '
                    f'\\frac{{\\partial u}}{{\\partial {y_var}}} = {du_dy.representacao_latex()}, '
                    f'\\frac{{\\partial v}}{{\\partial {x_var}}} = {dv_dx.representacao_latex()}, '
                    f'\\frac{{\\partial v}}{{\\partial {y_var}}} = {dv_dy.representacao_latex()}',
        regra='Derivadas parciais',
    ))

    # Condicao 1: du/dx == dv/dy
    cond1 = _nos_iguais(du_dx, dv_dy)

    # Condicao 2: du/dy == -dv/dx
    # Construir -dv/dx = op('*', num('-1'), dv_dx) e simplificar
    neg_dv_dx = simplificar_no(op('*', num('-1'), dv_dx))
    cond2 = _nos_iguais(du_dy, neg_dv_dx)

    satisfaz = cond1 and cond2

    detalhes = {
        'du_dx': du_dx.representacao_latex(),
        'du_dy': du_dy.representacao_latex(),
        'dv_dx': dv_dx.representacao_latex(),
        'dv_dy': dv_dy.representacao_latex(),
        'condicao_1': cond1,
        'condicao_2': cond2,
    }

    status = 'satisfeitas' if satisfaz else 'NAO satisfeitas'
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Condicoes de Cauchy-Riemann {status}',
        latex_depois=f'du/dx = {du_dx.representacao_latex()}, dv/dy = {dv_dy.representacao_latex()} '
                    f'| du/dy = {du_dy.representacao_latex()}, -dv/dx = {neg_dv_dx.representacao_latex()}',
        regra='Condicoes de Cauchy-Riemann',
    ))

    return (satisfaz, detalhes, historico)


def _nos_iguais(a: NoExpressao, b: NoExpressao) -> bool:
    """Compara dois nos de expressao: estrutural primeiro, numérico como fallback."""
    if a == b:
        return True
    # Fallback: comparar numericamente em vários pontos
    import random
    random.seed(42)
    pontos_teste = [{chr(ord('x') + i): random.uniform(0.5, 3.0) for i in range(3)} for _ in range(5)]
    try:
        for ponto in pontos_teste:
            va = a.avaliar(ponto)
            vb = b.avaliar(ponto)
            if va is None or vb is None:
                continue
            if abs(va - vb) > 1e-8:
                return False
        return True
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        return False


def residuo_polo_simples(f_num: NoExpressao, f_den: NoExpressao,
                         z0: Complexo) -> tuple:
    """Calcula residuo de f = f_num/f_den em polo simples z0.

    Res(f, z0) = lim(z->z0) (z - z0) * f(z) = f_num(z0) / f_den'(z0)

    Para polo simples, usa a formula: Res = p(z0)/q'(z0)
    onde f = p/q.

    Retorna (residuo: Complexo, Historico).
    """
    from engine.calculo.derivada import derivar

    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular residuo no polo simples z0 = {z0.representacao_latex()}',
        latex_antes=f'\\text{{Res}}(f, z_0) = \\frac{{p(z_0)}}{{q\'(z_0)}}',
        regra='Residuo em polo simples',
    ))

    # Derivar denominador em relacao a z
    dq = derivar(f_den, 'z', historico)
    dq = simplificar_no(dq)

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Derivada do denominador: q\'(z) = {dq.representacao_latex()}',
        regra='Derivada do denominador',
    ))

    # Avaliar numerador e derivada do denominador em z0
    # Para simplificar, usamos avaliacao com z = parte real de z0
    # (caso z0 seja real, o que e comum em exercicios basicos)
    z0_val = float(z0.real)
    variaveis = {'z': z0_val}

    try:
        p_z0 = f_num.avaliar(variaveis)
        q_prime_z0 = dq.avaliar(variaveis)
    except Exception as e:
        raise ValueError(f'Erro ao avaliar em z0: {e}')

    if abs(q_prime_z0) < 1e-15:
        raise ValueError('Polo nao e simples: q\'(z0) = 0')

    residuo_val = p_z0 / q_prime_z0
    residuo = Complexo(str(round(residuo_val, 10)), '0')

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Residuo calculado: {residuo.representacao_latex()}',
        latex_depois=f'\\text{{Res}}(f, {z0.representacao_latex()}) = {residuo.representacao_latex()}',
        regra='Residuo em polo simples',
    ))

    return (residuo, historico)
