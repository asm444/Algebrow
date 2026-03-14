"""Polinômios de Hermite H_n(x) e Laguerre L_n(x)."""
import math
from engine.basic.passo import Passo, Historico


def hermite(n: int) -> tuple:
    """H_n(x) via recursão: H_{n+1} = 2xH_n - 2nH_{n-1}.
    Retorna (coeficientes: list, Historico)
    Coeficientes em ordem [a0, a1, a2, ...] onde poly = a0 + a1*x + a2*x² + ..."""
    hist = Historico()

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Calcular H_{{{n}}}(x) via recursão",
        latex_antes=f"H_{{{n}}}(x)",
        regra="Polinômios de Hermite"
    ))

    if n == 0:
        coefs = [1.0]
        hist.adicionar(Passo(
            nivel=2, descricao="H_0(x) = 1",
            latex_depois="H_0(x) = 1", regra="Caso base"
        ))
        return (coefs, hist)

    if n == 1:
        coefs = [0.0, 2.0]
        hist.adicionar(Passo(
            nivel=2, descricao="H_1(x) = 2x",
            latex_depois="H_1(x) = 2x", regra="Caso base"
        ))
        return (coefs, hist)

    h_prev = [1.0]        # H_0
    h_curr = [0.0, 2.0]   # H_1

    for k in range(1, n):
        # H_{k+1} = 2x·H_k - 2k·H_{k-1}
        # 2x·H_k: shift e multiplicar por 2
        xh = [0.0] + h_curr
        xh = [c * 2 for c in xh]

        # 2k·H_{k-1}
        kh = [c * 2 * k for c in h_prev]

        # Subtrair
        tamanho = max(len(xh), len(kh))
        while len(xh) < tamanho:
            xh.append(0.0)
        while len(kh) < tamanho:
            kh.append(0.0)

        h_next = [xh[i] - kh[i] for i in range(tamanho)]

        hist.adicionar(Passo(
            nivel=3,
            descricao=f"H_{{{k + 1}}}(x) = 2x·H_{{{k}}}(x) - 2·{k}·H_{{{k - 1}}}(x)",
            regra="Recursão de Hermite"
        ))

        h_prev = h_curr
        h_curr = h_next

    coefs = [round(c, 12) for c in h_curr]

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"H_{{{n}}}(x): coeficientes = {coefs}",
        latex_depois=f"H_{{{n}}}(x)",
        regra="Resultado"
    ))

    return (coefs, hist)


def laguerre(n: int, alpha: float = 0) -> tuple:
    """L_n^α(x) generalizados via recursão:
    (k+1)L_{k+1} = (2k+1+α-x)L_k - (k+α)L_{k-1}.
    Retorna (coeficientes: list, Historico)
    Coeficientes em ordem [a0, a1, a2, ...] onde poly = a0 + a1*x + a2*x² + ..."""
    hist = Historico()

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Calcular L_{{{n}}}^{{{alpha}}}(x) via recursão",
        latex_antes=f"L_{{{n}}}^{{{alpha}}}(x)",
        regra="Polinômios de Laguerre"
    ))

    if n == 0:
        coefs = [1.0]
        hist.adicionar(Passo(
            nivel=2, descricao=f"L_0^{{{alpha}}}(x) = 1",
            latex_depois="1", regra="Caso base"
        ))
        return (coefs, hist)

    if n == 1:
        coefs = [1.0 + alpha, -1.0]
        hist.adicionar(Passo(
            nivel=2, descricao=f"L_1^{{{alpha}}}(x) = {1 + alpha} - x",
            latex_depois=f"{1 + alpha} - x", regra="Caso base"
        ))
        return (coefs, hist)

    l_prev = [1.0]                    # L_0
    l_curr = [1.0 + alpha, -1.0]     # L_1

    for k in range(1, n):
        # (k+1)L_{k+1} = (2k+1+α-x)L_k - (k+α)L_{k-1}
        # (2k+1+α)·L_k
        fator1 = 2 * k + 1 + alpha
        parte1 = [c * fator1 for c in l_curr]

        # -x·L_k : shift e negar
        x_lk = [0.0] + l_curr
        x_lk = [-c for c in x_lk]

        # Somar parte1 + x_lk
        tamanho = max(len(parte1), len(x_lk))
        while len(parte1) < tamanho:
            parte1.append(0.0)
        while len(x_lk) < tamanho:
            x_lk.append(0.0)

        soma = [parte1[i] + x_lk[i] for i in range(tamanho)]

        # -(k+α)·L_{k-1}
        fator2 = k + alpha
        sub = [c * fator2 for c in l_prev]
        while len(sub) < tamanho:
            sub.append(0.0)
        while len(soma) < len(sub):
            soma.append(0.0)
        tamanho = max(len(soma), len(sub))

        l_next = [(soma[i] - sub[i]) / (k + 1) for i in range(tamanho)]

        hist.adicionar(Passo(
            nivel=3,
            descricao=f"L_{{{k + 1}}}^{{{alpha}}} via recursão com k={k}",
            regra="Recursão de Laguerre"
        ))

        l_prev = l_curr
        l_curr = l_next

    coefs = [round(c, 12) for c in l_curr]

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"L_{{{n}}}^{{{alpha}}}(x): coeficientes = {coefs}",
        latex_depois=f"L_{{{n}}}^{{{alpha}}}(x)",
        regra="Resultado"
    ))

    return (coefs, hist)
