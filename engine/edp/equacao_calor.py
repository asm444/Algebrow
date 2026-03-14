"""Equação do calor: ∂u/∂t = k·∂²u/∂x²

Soluções analíticas clássicas:
- Separação de variáveis com condições de Dirichlet
- Solução fundamental (fonte pontual)
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

def separacao_variaveis_calor(L, k, n_termos=10,
                               condicao_inicial='sin(pi*x/L)'):
    """Resolve equação do calor por separação de variáveis.

    ∂u/∂t = k·∂²u/∂x² em [0, L], com u(0,t) = u(L,t) = 0.

    Solução: u(x,t) = Σ Bₙ sin(nπx/L) exp(-k(nπ/L)²t)

    Parâmetros:
        L: comprimento do domínio
        k: coeficiente de difusão térmica
        n_termos: número de termos na série
        condicao_inicial: expressão em x para u(x,0)

    Retorna:
        (coeficientes_Bn: list, solucao_latex: str, Historico)
    """
    hist = Historico()

    hist.adicionar(Passo(
        1, "Equação do calor com condições de Dirichlet",
        latex_antes=f"\\frac{{\\partial u}}{{\\partial t}} = {k} \\cdot "
                    f"\\frac{{\\partial^2 u}}{{\\partial x^2}},\\; "
                    f"x \\in [0, {L}]",
        regra="Equação do calor"
    ))

    hist.adicionar(Passo(
        2, "Separação de variáveis: u(x,t) = X(x)·T(t)",
        latex_depois="\\frac{T'}{kT} = \\frac{X''}{X} = -\\lambda",
        regra="Separação de variáveis",
        justificativa="Cada lado depende de uma variável diferente, logo ambos são constantes"
    ))

    hist.adicionar(Passo(
        2, "Problema de autovalores: X'' + λX = 0, X(0) = X(L) = 0",
        latex_depois=f"\\lambda_n = \\left(\\frac{{n\\pi}}{{{L}}}\\right)^2,\\; "
                     f"X_n(x) = \\sin\\left(\\frac{{n\\pi x}}{{{L}}}\\right)",
        regra="Autovalores de Dirichlet"
    ))

    hist.adicionar(Passo(
        2, "Equação temporal: T' + kλT = 0 → T(t) = exp(-kλt)",
        latex_depois=f"T_n(t) = \\exp\\left(-{k}\\left(\\frac{{n\\pi}}{{{L}}}\\right)^2 t\\right)",
        regra="EDO temporal"
    ))

    # Calcula coeficientes Bn por integração numérica (Simpson)
    hist.adicionar(Passo(
        2, f"Cálculo dos coeficientes Bₙ a partir de u(x,0) = {condicao_inicial}",
        latex_depois=f"B_n = \\frac{{2}}{{{L}}} \\int_0^{{{L}}} u(x,0) "
                     f"\\sin\\left(\\frac{{n\\pi x}}{{{L}}}\\right) dx",
        regra="Ortogonalidade das autofunções"
    ))

    coeficientes = []
    N_quad = 500

    # Substitui L na expressão da condição inicial
    ci_str = condicao_inicial.replace('L', str(L))

    for n in range(1, n_termos + 1):
        h_int = L / N_quad
        soma = 0.0
        for i in range(N_quad + 1):
            xi = i * h_int
            try:
                fi = _avaliar(ci_str, x=xi)
            except Exception:
                fi = 0.0
            gi = fi * math.sin(n * math.pi * xi / L)
            if i == 0 or i == N_quad:
                soma += gi
            elif i % 2 == 1:
                soma += 4 * gi
            else:
                soma += 2 * gi
        integral = (h_int / 3) * soma
        bn = (2.0 / L) * integral
        coeficientes.append(round(bn, 10))

        hist.adicionar(Passo(
            3, f"B_{n} = {bn:.6f}",
            latex_depois=f"B_{{{n}}} = {bn:.6f}",
            regra="Integração numérica"
        ))

    # Monta solução LaTeX
    termos_latex = []
    for n in range(1, min(4, n_termos + 1)):
        bn = coeficientes[n - 1]
        if abs(bn) > 1e-10:
            termos_latex.append(
                f"{bn:.4f} \\sin\\left(\\frac{{{n}\\pi x}}{{{L}}}\\right) "
                f"\\exp\\left(-{k}\\left(\\frac{{{n}\\pi}}{{{L}}}\\right)^2 t\\right)"
            )

    if len(termos_latex) > 0:
        solucao_latex = "u(x,t) = " + " + ".join(termos_latex)
        if n_termos > 3:
            solucao_latex += " + \\cdots"
    else:
        solucao_latex = "u(x,t) = 0"

    hist.adicionar(Passo(
        1, "Solução por separação de variáveis",
        latex_depois=solucao_latex,
        regra="Resultado"
    ))

    return coeficientes, solucao_latex, hist


# ---------------------------------------------------------------------------
# Solução fundamental (fonte pontual)
# ---------------------------------------------------------------------------

def solucao_calor_pontual(k, t, x):
    """Solução fundamental da equação do calor (núcleo de calor / função de Green).

    u(x,t) = 1/√(4πkt) · exp(-x²/(4kt))

    Para t > 0.

    Parâmetros:
        k: coeficiente de difusão térmica
        t: instante de tempo (deve ser > 0)
        x: posição

    Retorna:
        (valor: float, Historico)
    """
    hist = Historico()

    hist.adicionar(Passo(
        1, "Solução fundamental da equação do calor",
        latex_antes=f"\\frac{{\\partial u}}{{\\partial t}} = {k} "
                    f"\\frac{{\\partial^2 u}}{{\\partial x^2}}",
        regra="Núcleo de calor"
    ))

    if t <= 0:
        raise ValueError("t deve ser positivo para a solução fundamental.")

    hist.adicionar(Passo(
        2, "A solução fundamental satisfaz u(x,0) = δ(x) (delta de Dirac)",
        justificativa="Representa difusão de uma fonte pontual de calor em t=0",
        regra="Condição inicial"
    ))

    hist.adicionar(Passo(
        2, "Fórmula da solução fundamental",
        latex_depois=f"u(x,t) = \\frac{{1}}{{\\sqrt{{4\\pi \\cdot {k} \\cdot t}}}} "
                     f"\\exp\\left(-\\frac{{x^2}}{{4 \\cdot {k} \\cdot t}}\\right)",
        regra="Transformada de Fourier"
    ))

    denominador = math.sqrt(4 * math.pi * k * t)
    expoente = -(x ** 2) / (4 * k * t)
    valor = (1.0 / denominador) * math.exp(expoente)

    hist.adicionar(Passo(
        3, f"Substituindo k={k}, t={t}, x={x}",
        latex_antes=f"u({x}, {t}) = \\frac{{1}}{{\\sqrt{{4\\pi \\cdot {k} \\cdot {t}}}}} "
                    f"\\exp\\left(-\\frac{{{x}^2}}{{4 \\cdot {k} \\cdot {t}}}\\right)",
        latex_depois=f"u({x}, {t}) = {valor:.10f}",
        regra="Substituição numérica"
    ))

    hist.adicionar(Passo(
        1, f"u({x}, {t}) = {valor:.10f}",
        latex_depois=f"u({x}, {t}) = {valor:.10f}",
        regra="Resultado"
    ))

    return valor, hist
