"""Séries de Fourier completas."""

import math
from engine.basic.passo import Passo, Historico
from engine.avaliador_seguro import avaliar_seguro


def _avaliar_f(f_str: str, x: float) -> float:
    """Avalia f(x) via AST walking seguro (sem eval)."""
    return avaliar_seguro(f_str, {'x': x})


def _simpson(f, a: float, b: float, n: int = 1000) -> float:
    """Quadratura de Simpson composta."""
    if n % 2 != 0:
        n += 1
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        xi = a + i * h
        coef = 4 if i % 2 != 0 else 2
        s += coef * f(xi)
    return s * h / 3


def coeficientes_fourier(f_str: str, L: float, n_termos: int = 10) -> tuple:
    """Calcula a0, an, bn da série de Fourier de f(x) em [-L, L].

    a0 = 1/(2L) integral_{-L}^{L} f(x)dx
    an = 1/L integral_{-L}^{L} f(x)cos(n*pi*x/L)dx
    bn = 1/L integral_{-L}^{L} f(x)sin(n*pi*x/L)dx

    Usa quadratura numérica (Simpson).
    Retorna (a0: float, an: list[float], bn: list[float], Historico).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao=f'Calculando coeficientes de Fourier de f(x) = {f_str} em [-{L}, {L}]',
        regra='Série de Fourier',
    ))

    # a0
    a0 = _simpson(lambda x: _avaliar_f(f_str, x), -L, L) / (2 * L)
    hist.adicionar(Passo(
        nivel=2,
        descricao=f'a_0 = {a0:.6f}',
        latex_depois=f'a_0 = {a0:.6f}',
        regra='Coeficiente a_0',
    ))

    an = []
    bn = []
    for n in range(1, n_termos + 1):
        a_n = _simpson(
            lambda x, n=n: _avaliar_f(f_str, x) * math.cos(n * math.pi * x / L),
            -L, L
        ) / L
        b_n = _simpson(
            lambda x, n=n: _avaliar_f(f_str, x) * math.sin(n * math.pi * x / L),
            -L, L
        ) / L
        an.append(a_n)
        bn.append(b_n)
        hist.adicionar(Passo(
            nivel=3,
            descricao=f'n={n}: a_{n} = {a_n:.6f}, b_{n} = {b_n:.6f}',
            regra=f'Coeficientes n={n}',
        ))

    hist.adicionar(Passo(
        nivel=0,
        descricao='Coeficientes de Fourier calculados',
        regra='Resultado',
    ))
    return (a0, an, bn, hist)


def serie_fourier_latex(a0, an, bn, L) -> str:
    """Gera representação LaTeX da série."""
    termos = [f'{a0:.4f}']
    for n in range(len(an)):
        idx = n + 1
        if abs(an[n]) > 1e-10:
            sinal = '+' if an[n] >= 0 else ''
            termos.append(f'{sinal}{an[n]:.4f}\\cos\\left(\\frac{{{idx}\\pi x}}{{{L}}}\\right)')
        if abs(bn[n]) > 1e-10:
            sinal = '+' if bn[n] >= 0 else ''
            termos.append(f'{sinal}{bn[n]:.4f}\\sin\\left(\\frac{{{idx}\\pi x}}{{{L}}}\\right)')
    return 'f(x) \\approx ' + ' '.join(termos)


def serie_fourier_senos(f_str: str, L: float, n_termos: int = 10) -> tuple:
    """Extensão ímpar — só senos. Retorna (bn: list, Historico)."""
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao=f'Série de Fourier em senos (extensão ímpar) de f(x) = {f_str}',
        regra='Série de senos',
    ))

    bn = []
    for n in range(1, n_termos + 1):
        b_n = _simpson(
            lambda x, n=n: _avaliar_f(f_str, x) * math.sin(n * math.pi * x / L),
            0, L
        ) * 2 / L
        bn.append(b_n)
        hist.adicionar(Passo(
            nivel=2,
            descricao=f'b_{n} = {b_n:.6f}',
            regra=f'Coeficiente b_{n}',
        ))

    return (bn, hist)


def serie_fourier_cossenos(f_str: str, L: float, n_termos: int = 10) -> tuple:
    """Extensão par — só cossenos. Retorna (an: list, Historico)."""
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao=f'Série de Fourier em cossenos (extensão par) de f(x) = {f_str}',
        regra='Série de cossenos',
    ))

    # a0
    a0 = _simpson(lambda x: _avaliar_f(f_str, x), 0, L) * 2 / L
    an = [a0]
    hist.adicionar(Passo(
        nivel=2,
        descricao=f'a_0 = {a0:.6f}',
        regra='Coeficiente a_0',
    ))

    for n in range(1, n_termos + 1):
        a_n = _simpson(
            lambda x, n=n: _avaliar_f(f_str, x) * math.cos(n * math.pi * x / L),
            0, L
        ) * 2 / L
        an.append(a_n)
        hist.adicionar(Passo(
            nivel=2,
            descricao=f'a_{n} = {a_n:.6f}',
            regra=f'Coeficiente a_{n}',
        ))

    return (an, hist)


def parseval(a0, an, bn) -> tuple:
    """Identidade de Parseval: integral|f|^2 = L(a0^2/2 + sum(an^2+bn^2)).

    Retorna (valor, Historico).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao='Aplicando identidade de Parseval',
        regra='Parseval',
    ))

    soma = a0 ** 2 / 2
    for i in range(len(an)):
        soma += an[i] ** 2 + bn[i] ** 2

    hist.adicionar(Passo(
        nivel=2,
        descricao=f'a_0²/2 + sum(a_n² + b_n²) = {soma:.6f}',
        latex_depois=f'\\frac{{a_0^2}}{{2}} + \\sum_{{n=1}}^{{N}}(a_n^2 + b_n^2) = {soma:.6f}',
        regra='Parseval - resultado',
    ))

    return (soma, hist)
