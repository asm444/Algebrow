"""Equação da onda: ∂²u/∂t² = c²·∂²u/∂x²

Soluções analíticas clássicas:
- Separação de variáveis (corda vibrante)
- Fórmula de d'Alembert
"""

import ast
import math
import operator

from engine.basic.passo import Passo, Historico


# ---------------------------------------------------------------------------
# Avaliador seguro
# ---------------------------------------------------------------------------

_NS_SEGURO = {
    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'exp': math.exp, 'log': math.log, 'sqrt': math.sqrt,
    'abs': abs, 'pi': math.pi, 'e': math.e,
}

_OPS_BIN = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_OPS_UN = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval_node(node, ns):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, ns)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.Name):
        if node.id in ns:
            return ns[node.id]
        raise ValueError(f"Nome não permitido: {node.id}")
    if isinstance(node, ast.BinOp):
        t = type(node.op)
        if t not in _OPS_BIN:
            raise ValueError(f"Operador não permitido: {t.__name__}")
        return _OPS_BIN[t](_eval_node(node.left, ns), _eval_node(node.right, ns))
    if isinstance(node, ast.UnaryOp):
        t = type(node.op)
        if t not in _OPS_UN:
            raise ValueError(f"Operador unário não permitido: {t.__name__}")
        return _OPS_UN[t](_eval_node(node.operand, ns))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        nome = node.func.id
        if nome in ns and callable(ns[nome]):
            args = [_eval_node(a, ns) for a in node.args]
            return ns[nome](*args)
        raise ValueError(f"Função não permitida: {nome}")
    raise ValueError(f"Nó AST não permitido: {type(node).__name__}")


def _avaliar(expr_str, **variaveis):
    ns = {**_NS_SEGURO, **variaveis}
    tree = ast.parse(expr_str, mode='eval')
    return float(_eval_node(tree, ns))


# ---------------------------------------------------------------------------
# Separação de variáveis
# ---------------------------------------------------------------------------

def separacao_variaveis_onda(L, c, n_termos=10):
    """Resolve equação da onda por separação de variáveis.

    ∂²u/∂t² = c²·∂²u/∂x² em [0, L], com u(0,t) = u(L,t) = 0.

    Solução geral:
        u(x,t) = Σ [Aₙ cos(nπct/L) + Bₙ sin(nπct/L)] sin(nπx/L)

    Retorna:
        (solucao_latex: str, Historico)
    """
    hist = Historico()

    hist.adicionar(Passo(
        1, "Equação da onda com condições de Dirichlet",
        latex_antes=f"\\frac{{\\partial^2 u}}{{\\partial t^2}} = {c}^2 "
                    f"\\frac{{\\partial^2 u}}{{\\partial x^2}},\\; x \\in [0, {L}]",
        regra="Equação da onda"
    ))

    hist.adicionar(Passo(
        2, "Separação de variáveis: u(x,t) = X(x)·T(t)",
        latex_depois="\\frac{T''}{c^2 T} = \\frac{X''}{X} = -\\lambda",
        regra="Separação de variáveis"
    ))

    hist.adicionar(Passo(
        2, "Problema espacial: X'' + λX = 0, X(0) = X(L) = 0",
        latex_depois=f"\\lambda_n = \\left(\\frac{{n\\pi}}{{{L}}}\\right)^2,\\; "
                     f"X_n(x) = \\sin\\left(\\frac{{n\\pi x}}{{{L}}}\\right)",
        regra="Autovalores"
    ))

    hist.adicionar(Passo(
        2, "Problema temporal: T'' + c²λT = 0",
        latex_depois=f"T_n(t) = A_n \\cos\\left(\\frac{{n\\pi {c} t}}{{{L}}}\\right) + "
                     f"B_n \\sin\\left(\\frac{{n\\pi {c} t}}{{{L}}}\\right)",
        regra="EDO temporal — oscilador harmônico"
    ))

    hist.adicionar(Passo(
        2, "Frequências naturais da corda vibrante",
        latex_depois=f"\\omega_n = \\frac{{n\\pi {c}}}{{{L}}},\\; n = 1, 2, 3, \\ldots",
        regra="Frequências naturais"
    ))

    # Monta solução geral
    termos = []
    for n in range(1, min(4, n_termos + 1)):
        termos.append(
            f"\\left[A_{{{n}}} \\cos\\left(\\frac{{{n}\\pi \\cdot {c} \\cdot t}}{{{L}}}\\right) + "
            f"B_{{{n}}} \\sin\\left(\\frac{{{n}\\pi \\cdot {c} \\cdot t}}{{{L}}}\\right)\\right] "
            f"\\sin\\left(\\frac{{{n}\\pi x}}{{{L}}}\\right)"
        )

    solucao_latex = "u(x,t) = " + " + ".join(termos)
    if n_termos > 3:
        solucao_latex += " + \\cdots"

    hist.adicionar(Passo(
        1, "Solução geral por separação de variáveis",
        latex_depois=solucao_latex,
        regra="Resultado"
    ))

    return solucao_latex, hist


# ---------------------------------------------------------------------------
# Fórmula de d'Alembert
# ---------------------------------------------------------------------------

def dAlembert(f_str, g_str, c):
    """Solução de d'Alembert para a equação da onda na reta real.

    u(x,t) = [f(x+ct) + f(x-ct)]/2 + 1/(2c) ∫_{x-ct}^{x+ct} g(s) ds

    Parâmetros:
        f_str: condição inicial u(x,0) = f(x) (expressão em x)
        g_str: velocidade inicial ∂u/∂t(x,0) = g(x) (expressão em x)
        c: velocidade de propagação

    Retorna:
        (solucao_latex: str, Historico)
    """
    hist = Historico()

    hist.adicionar(Passo(
        1, "Solução de d'Alembert para a equação da onda",
        latex_antes=f"u_{{tt}} = {c}^2 u_{{xx}},\\; "
                    f"u(x,0) = {f_str},\\; u_t(x,0) = {g_str}",
        regra="Fórmula de d'Alembert"
    ))

    hist.adicionar(Passo(
        2, "Mudança de variáveis: ξ = x + ct, η = x - ct",
        latex_depois="u_{\\xi\\eta} = 0 \\Rightarrow u = F(\\xi) + G(\\eta)",
        regra="Variáveis características",
        justificativa="As características da equação da onda são as retas x ± ct = const"
    ))

    hist.adicionar(Passo(
        2, "Aplicando condições iniciais para determinar F e G",
        regra="Condições iniciais"
    ))

    # Monta expressão LaTeX da solução
    f_plus = f_str.replace('x', f'(x + {c}t)')
    f_minus = f_str.replace('x', f'(x - {c}t)')

    solucao_latex = (
        f"u(x,t) = \\frac{{{f_str.replace('x', '(x+ct)')} + "
        f"{f_str.replace('x', '(x-ct)')}}}"
        f"{{2}}"
    )

    # Verifica se g é zero
    try:
        g_zero = all(abs(_avaliar(g_str, x=xi)) < 1e-15
                     for xi in [0.0, 0.5, 1.0, -1.0, 2.0])
    except Exception:
        g_zero = False

    if not g_zero:
        solucao_latex += (
            f" + \\frac{{1}}{{2 \\cdot {c}}} "
            f"\\int_{{x - {c}t}}^{{x + {c}t}} {g_str.replace('x', 's')}\\, ds"
        )
        hist.adicionar(Passo(
            2, "g(x) ≠ 0: incluindo termo integral",
            regra="Termo de velocidade inicial"
        ))
    else:
        hist.adicionar(Passo(
            2, "g(x) = 0: o termo integral se anula",
            latex_depois="\\frac{1}{2c} \\int_{x-ct}^{x+ct} g(s)\\, ds = 0",
            regra="Velocidade inicial nula"
        ))

    hist.adicionar(Passo(
        1, "Solução de d'Alembert",
        latex_depois=solucao_latex,
        regra="Resultado"
    ))

    return solucao_latex, hist
