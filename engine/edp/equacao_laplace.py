"""Equação de Laplace: nabla^2 u = 0

Soluções analíticas clássicas por separação de variáveis:
- Retângulo (coordenadas cartesianas)
- Disco (coordenadas polares)
"""

import math

from engine.basic.passo import Passo, Historico


def laplace_retangulo(a, b, condicao, n_termos=10):
    """Resolve equação de Laplace em retângulo [0,a] x [0,b] por separação de variáveis.

    nabla^2 u = 0 com u = 0 em três lados e u(x, b) = condicao(x) no lado superior.

    Solução: u(x,y) = sum_n B_n sin(n pi x / a) sinh(n pi y / a) / sinh(n pi b / a)

    Parâmetros:
        a: largura do retângulo
        b: altura do retângulo
        condicao: string descrevendo a condição de contorno superior
                  ('sin', 'constante', ou valor numérico para temperatura constante)
        n_termos: número de termos na série

    Retorna:
        (solucao_latex: str, Historico)
    """
    hist = Historico()

    hist.adicionar(Passo(
        1, "Equação de Laplace em domínio retangular",
        latex_antes=f"\\nabla^2 u = 0,\\; (x,y) \\in [0, {a}] \\times [0, {b}]",
        regra="Equação de Laplace"
    ))

    hist.adicionar(Passo(
        2, "Condições de contorno homogêneas em 3 lados: u(0,y)=0, u(a,y)=0, u(x,0)=0",
        regra="Condições de contorno"
    ))

    hist.adicionar(Passo(
        2, f"Condição não-homogênea: u(x, {b}) = {condicao}",
        regra="Condição de contorno superior"
    ))

    hist.adicionar(Passo(
        2, "Separação de variáveis: u(x,y) = X(x)·Y(y)",
        latex_depois="\\frac{X''}{X} = -\\frac{Y''}{Y} = -\\lambda",
        regra="Separação de variáveis"
    ))

    hist.adicionar(Passo(
        2, "Problema em x: X'' + λX = 0, X(0) = X(a) = 0",
        latex_depois=f"\\lambda_n = \\left(\\frac{{n\\pi}}{{{a}}}\\right)^2,\\; "
                     f"X_n(x) = \\sin\\left(\\frac{{n\\pi x}}{{{a}}}\\right)",
        regra="Autovalores"
    ))

    hist.adicionar(Passo(
        2, "Problema em y: Y'' - λY = 0, Y(0) = 0",
        latex_depois=f"Y_n(y) = \\sinh\\left(\\frac{{n\\pi y}}{{{a}}}\\right)",
        regra="EDO em y",
        justificativa="Y(0) = 0 elimina o cosh; sinh cresce com y"
    ))

    # Calcula coeficientes B_n
    coeficientes = []
    for n in range(1, n_termos + 1):
        sinh_val = math.sinh(n * math.pi * b / a)
        if abs(sinh_val) < 1e-300:
            coeficientes.append(0.0)
            continue

        # Calcula integral de condicao(x) * sin(n*pi*x/a) dx de 0 a a
        if condicao == 'sin' or condicao == 'sin(pi*x/a)':
            # sin(pi*x/a) * sin(n*pi*x/a) dx = a/2 * delta_{n,1}
            if n == 1:
                integral = a / 2.0
            else:
                integral = 0.0
        else:
            # Condição constante
            try:
                T_val = float(condicao)
            except (ValueError, TypeError):
                T_val = 1.0  # padrão
            # integral_0^a T * sin(n*pi*x/a) dx = T * a/(n*pi) * (1 - cos(n*pi))
            integral = T_val * a / (n * math.pi) * (1 - math.cos(n * math.pi))

        bn = (2.0 / a) * integral / sinh_val
        coeficientes.append(bn)

        if abs(bn) > 1e-15:
            hist.adicionar(Passo(
                3, f"B_{n} = {bn:.6f}",
                latex_depois=f"B_{{{n}}} = {bn:.6f}",
                regra="Coeficiente de Fourier"
            ))

    # Monta solução LaTeX
    termos_latex = []
    for n in range(1, min(4, n_termos + 1)):
        bn = coeficientes[n - 1]
        if abs(bn) > 1e-15:
            termos_latex.append(
                f"{bn:.4f} \\sin\\left(\\frac{{{n}\\pi x}}{{{a}}}\\right) "
                f"\\frac{{\\sinh\\left(\\frac{{{n}\\pi y}}{{{a}}}\\right)}}"
                f"{{\\sinh\\left(\\frac{{{n}\\pi \\cdot {b}}}{{{a}}}\\right)}}"
            )

    if termos_latex:
        solucao_latex = "u(x,y) = " + " + ".join(termos_latex)
        if n_termos > 3:
            solucao_latex += " + \\cdots"
    else:
        solucao_latex = "u(x,y) = 0"

    hist.adicionar(Passo(
        1, "Solução da equação de Laplace no retângulo",
        latex_depois=solucao_latex,
        regra="Resultado"
    ))

    return solucao_latex, hist


def laplace_disco(R, n_termos=10):
    """Resolve equação de Laplace em disco de raio R (coordenadas polares).

    nabla^2 u = 0, com u(R, theta) = f(theta).

    Solução (fórmula de Poisson):
        u(r, theta) = A_0/2 + sum_n (r/R)^n [A_n cos(n theta) + B_n sin(n theta)]

    Parâmetros:
        R: raio do disco
        n_termos: número de termos na série

    Retorna:
        (solucao_latex: str, Historico)
    """
    hist = Historico()

    hist.adicionar(Passo(
        1, "Equação de Laplace em disco de raio R",
        latex_antes=f"\\nabla^2 u = 0,\\; r < {R}",
        regra="Equação de Laplace em coordenadas polares"
    ))

    hist.adicionar(Passo(
        2, "Em coordenadas polares: u_rr + (1/r)u_r + (1/r²)u_θθ = 0",
        latex_depois="\\frac{\\partial^2 u}{\\partial r^2} + "
                     "\\frac{1}{r}\\frac{\\partial u}{\\partial r} + "
                     "\\frac{1}{r^2}\\frac{\\partial^2 u}{\\partial \\theta^2} = 0",
        regra="Laplaciano em polares"
    ))

    hist.adicionar(Passo(
        2, "Separação: u(r,θ) = R(r)·Θ(θ)",
        latex_depois="r^2 R'' + r R' - n^2 R = 0,\\; \\Theta'' + n^2 \\Theta = 0",
        regra="Separação de variáveis"
    ))

    hist.adicionar(Passo(
        2, "Periodicidade em θ força n inteiro; regularidade na origem força R(r) = rⁿ",
        latex_depois=f"R_n(r) = \\left(\\frac{{r}}{{{R}}}\\right)^n",
        regra="Condições de regularidade",
        justificativa="Descartamos r^{-n} para u limitado em r=0"
    ))

    # Monta termos
    termos = [f"\\frac{{A_0}}{{2}}"]
    for n in range(1, min(4, n_termos + 1)):
        termos.append(
            f"\\left(\\frac{{r}}{{{R}}}\\right)^{{{n}}} "
            f"\\left[A_{{{n}}} \\cos({n}\\theta) + B_{{{n}}} \\sin({n}\\theta)\\right]"
        )

    solucao_latex = "u(r,\\theta) = " + " + ".join(termos)
    if n_termos > 3:
        solucao_latex += " + \\cdots"

    hist.adicionar(Passo(
        2, "Coeficientes determinados pela condição de contorno u(R,θ) = f(θ)",
        latex_depois=f"A_n = \\frac{{1}}{{\\pi}} \\int_0^{{2\\pi}} f(\\theta) \\cos(n\\theta)\\, d\\theta,\\; "
                     f"B_n = \\frac{{1}}{{\\pi}} \\int_0^{{2\\pi}} f(\\theta) \\sin(n\\theta)\\, d\\theta",
        regra="Coeficientes de Fourier"
    ))

    hist.adicionar(Passo(
        1, "Solução da equação de Laplace no disco",
        latex_depois=solucao_latex,
        regra="Resultado"
    ))

    return solucao_latex, hist
