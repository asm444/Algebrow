"""Funções de Green para EDOs e PDEs.

Implementa construção analítica de funções de Green para:
- EDOs lineares de 2ª ordem
- Laplaciano 2D
- Equação de Helmholtz 1D
"""

import math

from engine.basic.passo import Passo, Historico


def green_edo_2ordem(p, q, r, a, b):
    """Constrói G(x,ξ) para Ly = [p(x)y']' + q(x)y = r(x).

    Usa soluções homogêneas y₁, y₂ e o Wronskiano para construir
    a função de Green com condições de Dirichlet y(a) = y(b) = 0.

    Para o caso p(x) = constante e q(x) = constante, resolve analiticamente.

    Parâmetros:
        p: coeficiente p (string representando constante ou expressão)
        q: coeficiente q (string representando constante ou expressão)
        r: lado direito (string)
        a, b: extremos do intervalo

    Retorna:
        (descricao_latex: str, Historico)
    """
    hist = Historico()

    hist.adicionar(Passo(
        1, "Construção da função de Green para EDO de 2ª ordem",
        latex_antes=f"[p(x)y']' + q(x)y = r(x),\\; x \\in [{a}, {b}]",
        regra="Função de Green"
    ))

    hist.adicionar(Passo(
        2, "Condições de contorno: y(a) = 0, y(b) = 0 (Dirichlet)",
        regra="Condições de contorno"
    ))

    # Tenta interpretar p e q como constantes
    try:
        p_val = float(p)
        q_val = float(q)
    except (ValueError, TypeError):
        # Caso geral simbólico
        hist.adicionar(Passo(
            2, "Para p(x) e q(x) gerais, a função de Green é construída com "
               "y₁(x) (satisfaz y₁(a)=0) e y₂(x) (satisfaz y₂(b)=0)",
            regra="Construção geral"
        ))

        latex = (
            f"G(x, \\xi) = \\begin{{cases}} "
            f"\\frac{{y_1(x) \\cdot y_2(\\xi)}}{{p(\\xi) \\cdot W(\\xi)}}, & a \\leq x \\leq \\xi \\\\ "
            f"\\frac{{y_1(\\xi) \\cdot y_2(x)}}{{p(\\xi) \\cdot W(\\xi)}}, & \\xi \\leq x \\leq b "
            f"\\end{{cases}}"
        )

        hist.adicionar(Passo(
            1, "Função de Green em termos das soluções homogêneas",
            latex_depois=latex,
            justificativa="W(ξ) é o Wronskiano de y₁ e y₂ avaliado em ξ",
            regra="Resultado"
        ))
        return latex, hist

    # Caso constante: p*y'' + q*y = r(x) → y'' + (q/p)*y = r(x)/p
    if abs(p_val) < 1e-15:
        raise ValueError("p não pode ser zero.")

    mu = q_val / p_val  # y'' + μy = f(x)

    hist.adicionar(Passo(
        2, f"Equação simplificada: y'' + ({mu:.4g})y = f(x)",
        latex_depois=f"y'' + {mu:.4g}\\, y = f(x)",
        regra="Normalização"
    ))

    if mu < 0:
        # μ < 0: soluções hiperbólicas
        k = math.sqrt(-mu)
        hist.adicionar(Passo(
            2, f"μ < 0 → soluções hiperbólicas com k = √(-μ) = {k:.6f}",
            regra="Classificação"
        ))
        y1_desc = f"\\sinh({k:.4g}(x - {a}))"
        y2_desc = f"\\sinh({k:.4g}({b} - x))"
        W_desc = f"-{k:.4g} \\sinh({k:.4g}({b} - {a}))"
    elif mu > 0:
        # μ > 0: soluções trigonométricas
        k = math.sqrt(mu)
        hist.adicionar(Passo(
            2, f"μ > 0 → soluções trigonométricas com k = √μ = {k:.6f}",
            regra="Classificação"
        ))
        y1_desc = f"\\sin({k:.4g}(x - {a}))"
        y2_desc = f"\\sin({k:.4g}({b} - x))"
        W_desc = f"-{k:.4g} \\sin({k:.4g}({b} - {a}))"
    else:
        # μ = 0: soluções lineares
        hist.adicionar(Passo(2, "μ = 0 → soluções lineares", regra="Classificação"))
        y1_desc = f"(x - {a})"
        y2_desc = f"({b} - x)"
        W_desc = f"-({b} - {a})"

    latex = (
        f"G(x, \\xi) = \\begin{{cases}} "
        f"\\frac{{{y1_desc} \\cdot {y2_desc.replace('x', '\\\\xi')}}}{{p \\cdot W}}, "
        f"& {a} \\leq x \\leq \\xi \\\\ "
        f"\\frac{{{y1_desc.replace('x', '\\\\xi')} \\cdot {y2_desc}}}{{p \\cdot W}}, "
        f"& \\xi \\leq x \\leq {b} "
        f"\\end{{cases}}"
    )

    hist.adicionar(Passo(
        2, f"Wronskiano: W = {W_desc}",
        latex_depois=f"W = {W_desc}",
        regra="Wronskiano"
    ))

    hist.adicionar(Passo(
        1, "Função de Green construída",
        latex_depois=latex,
        regra="Resultado"
    ))

    return latex, hist


def green_laplace_2d():
    """Função de Green para o Laplaciano em 2D: ∇²u = f.

    G(r, r') = -1/(2π) ln|r - r'|

    Retorna:
        (latex: str, Historico)
    """
    hist = Historico()

    hist.adicionar(Passo(
        1, "Função de Green para o Laplaciano em 2D",
        latex_antes="\\nabla^2 u = f(\\mathbf{r})",
        regra="Equação de Poisson 2D"
    ))

    hist.adicionar(Passo(
        2, "Em 2D, a solução fundamental do Laplaciano é logarítmica",
        justificativa="Simetria radial: ∇²G = δ(r - r') em coordenadas polares "
                       "leva a G = C·ln|r - r'|",
        regra="Simetria radial"
    ))

    hist.adicionar(Passo(
        2, "Determinação da constante: integrando ∇²G = δ sobre disco de raio ε → C = -1/(2π)",
        latex_depois="\\oint_{|\\mathbf{r}-\\mathbf{r'}|=\\varepsilon} "
                     "\\nabla G \\cdot d\\mathbf{S} = 1 \\Rightarrow C = -\\frac{1}{2\\pi}",
        regra="Normalização da delta de Dirac"
    ))

    latex = "G(\\mathbf{r}, \\mathbf{r'}) = -\\frac{1}{2\\pi} \\ln|\\mathbf{r} - \\mathbf{r'}|"

    hist.adicionar(Passo(
        1, "Função de Green do Laplaciano 2D",
        latex_depois=latex,
        regra="Resultado"
    ))

    return latex, hist


def green_helmholtz_1d(k, a, b):
    """Função de Green para a equação de Helmholtz 1D: y'' + k²y = f(x).

    Com condições de Dirichlet y(a) = y(b) = 0.

    G(x, ξ) = sin(k(x-a)) sin(k(b-ξ)) / [k sin(k(b-a))]  para a ≤ x ≤ ξ
              sin(k(ξ-a)) sin(k(b-x)) / [k sin(k(b-a))]  para ξ ≤ x ≤ b

    Parâmetros:
        k: número de onda
        a, b: extremos do intervalo

    Retorna:
        (latex: str, Historico)
    """
    hist = Historico()

    hist.adicionar(Passo(
        1, "Função de Green para Helmholtz 1D",
        latex_antes=f"y'' + {k}^2 y = f(x),\\; x \\in [{a}, {b}]",
        regra="Equação de Helmholtz"
    ))

    hist.adicionar(Passo(
        2, f"Soluções homogêneas: y₁(x) = sin(k(x-a)), y₂(x) = sin(k(b-x))",
        latex_depois=f"y_1(x) = \\sin({k}(x - {a})),\\; y_2(x) = \\sin({k}({b} - x))",
        regra="Soluções homogêneas com condições de contorno"
    ))

    # Wronskiano
    W_val = -k * math.sin(k * (b - a))
    hist.adicionar(Passo(
        2, f"Wronskiano: W = -k·sin(k(b-a)) = {W_val:.6f}",
        latex_depois=f"W = -{k} \\sin({k}({b} - {a})) = {W_val:.6f}",
        regra="Wronskiano"
    ))

    if abs(W_val) < 1e-12:
        hist.adicionar(Passo(
            1, "AVISO: Wronskiano ≈ 0, λ = k² é autovalor — Green não existe",
            regra="Condição de existência"
        ))
        return "\\text{Green não existe (autovalor)}", hist

    latex = (
        f"G(x, \\xi) = \\begin{{cases}} "
        f"\\frac{{\\sin({k}(x - {a})) \\sin({k}({b} - \\xi))}}"
        f"{{{k} \\sin({k}({b} - {a}))}}, "
        f"& {a} \\leq x \\leq \\xi \\\\ "
        f"\\frac{{\\sin({k}(\\xi - {a})) \\sin({k}({b} - x))}}"
        f"{{{k} \\sin({k}({b} - {a}))}}, "
        f"& \\xi \\leq x \\leq {b} "
        f"\\end{{cases}}"
    )

    hist.adicionar(Passo(
        1, "Função de Green de Helmholtz 1D construída",
        latex_depois=latex,
        regra="Resultado"
    ))

    return latex, hist
