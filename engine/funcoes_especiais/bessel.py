"""Funções de Bessel J_ν(x) e Y_ν(x)."""
import math
from engine.basic.passo import Passo, Historico
from engine.funcoes_especiais.gamma import _lanczos_gamma


def bessel_j(nu: float, x: float, n_termos: int = 20) -> tuple:
    """J_ν(x) = Σ (-1)^k (x/2)^(2k+ν) / (k! Γ(k+ν+1)), k=0..n.
    Retorna (valor: float, serie_latex: str, Historico)"""
    hist = Historico()

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Calcular J_{{{nu}}}({x}) com {n_termos} termos da série",
        latex_antes=f"J_{{{nu}}}({x}) = \\sum_{{k=0}}^{{{n_termos - 1}}} "
                    f"\\frac{{(-1)^k}}{{k! \\, \\Gamma(k+{nu}+1)}} "
                    f"\\left(\\frac{{{x}}}{{2}}\\right)^{{2k+{nu}}}",
        regra="Série de Bessel"
    ))

    soma = 0.0
    termos_latex = []

    for k in range(n_termos):
        sinal = (-1) ** k
        numerador = (x / 2) ** (2 * k + nu)
        fatorial_k = math.factorial(k)
        gamma_val = _lanczos_gamma(k + nu + 1)
        termo = sinal * numerador / (fatorial_k * gamma_val)
        soma += termo

        if k < 5:
            termos_latex.append(
                f"\\frac{{(-1)^{k}}}{{ {fatorial_k} \\cdot \\Gamma({k + nu + 1}) }} "
                f"\\left(\\frac{{{x}}}{{2}}\\right)^{{{2 * k + nu}}}"
            )

        hist.adicionar(Passo(
            nivel=3,
            descricao=f"k={k}: termo = {termo:.10g}, soma parcial = {soma:.10g}",
            regra="Termo da série"
        ))

    serie_latex = " + ".join(termos_latex)
    if n_termos > 5:
        serie_latex += " + \\cdots"

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"J_{{{nu}}}({x}) ≈ {soma:.10g}",
        latex_depois=f"J_{{{nu}}}({x}) \\approx {soma:.10g}",
        regra="Resultado da série de Bessel"
    ))

    return (soma, serie_latex, hist)


def bessel_zeros(nu: float, n_zeros: int = 5) -> list:
    """Primeiros n zeros de J_ν(x) por bisseção."""
    zeros = []
    # Buscar zeros começando próximo de x = nu + 1
    passo = 0.1
    x = max(passo, nu * 0.5 + 0.5)
    val_ant, _, _ = bessel_j(nu, x, n_termos=30)

    max_x = 1000.0
    while len(zeros) < n_zeros and x < max_x:
        x += passo
        val_atual, _, _ = bessel_j(nu, x, n_termos=30)

        if val_ant * val_atual < 0:
            # Bisseção
            a, b = x - passo, x
            for _ in range(60):
                meio = (a + b) / 2
                val_meio, _, _ = bessel_j(nu, meio, n_termos=30)
                if val_meio == 0:
                    break
                if val_ant * val_meio < 0:
                    b = meio
                else:
                    a = meio
                    val_ant = val_meio
            zeros.append(round((a + b) / 2, 4))

        val_ant = val_atual

    return zeros


def bessel_recorrencia(nu: float, x: float) -> tuple:
    """J_{ν-1}(x) + J_{ν+1}(x) = (2ν/x)J_ν(x). Retorna (Historico com passos)"""
    hist = Historico()

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Verificar recorrência: J_{{{nu - 1}}}({x}) + J_{{{nu + 1}}}({x}) = (2·{nu}/{x})·J_{{{nu}}}({x})",
        latex_antes=f"J_{{{nu - 1}}}({x}) + J_{{{nu + 1}}}({x}) = \\frac{{2 \\cdot {nu}}}{{{x}}} J_{{{nu}}}({x})",
        regra="Relação de recorrência de Bessel"
    ))

    j_prev, _, _ = bessel_j(nu - 1, x)
    j_curr, _, _ = bessel_j(nu, x)
    j_next, _, _ = bessel_j(nu + 1, x)

    lado_esq = j_prev + j_next
    lado_dir = (2 * nu / x) * j_curr

    hist.adicionar(Passo(
        nivel=2,
        descricao=f"J_{{{nu - 1}}}({x}) = {j_prev:.10g}",
        regra="Cálculo de Bessel"
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao=f"J_{{{nu}}}({x}) = {j_curr:.10g}",
        regra="Cálculo de Bessel"
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao=f"J_{{{nu + 1}}}({x}) = {j_next:.10g}",
        regra="Cálculo de Bessel"
    ))

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Lado esquerdo = {lado_esq:.10g}, Lado direito = {lado_dir:.10g}, "
                  f"Diferença = {abs(lado_esq - lado_dir):.2e}",
        latex_depois=f"{lado_esq:.10g} \\approx {lado_dir:.10g}",
        regra="Verificação da recorrência"
    ))

    return (hist,)
