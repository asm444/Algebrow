"""Transformada de Fourier contínua."""

import math
from engine.basic.passo import Passo, Historico
from engine.fourier.serie_fourier import _avaliar_f, _simpson


def transformada_fourier(f_str: str, omega_vals: list = None) -> tuple:
    """F(omega) = integral_{-inf}^{inf} f(x)e^{-i*omega*x}dx — por quadratura numérica.

    Aproxima a integral truncando em [-T, T] com T grande.
    Retorna (valores: list[complex], Historico).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao=f'Calculando transformada de Fourier de f(x) = {f_str}',
        regra='Transformada de Fourier',
    ))

    if omega_vals is None:
        omega_vals = [i * 0.5 for i in range(-20, 21)]

    T = 20.0  # truncamento
    n_pts = 2000
    valores = []

    for omega in omega_vals:
        # Parte real: integral f(x)*cos(omega*x)dx
        parte_real = _simpson(
            lambda x, w=omega: _avaliar_f(f_str, x) * math.cos(w * x),
            -T, T, n_pts
        )
        # Parte imaginária: -integral f(x)*sin(omega*x)dx
        parte_imag = -_simpson(
            lambda x, w=omega: _avaliar_f(f_str, x) * math.sin(w * x),
            -T, T, n_pts
        )
        valores.append(complex(parte_real, parte_imag))
        hist.adicionar(Passo(
            nivel=3,
            descricao=f'F({omega:.2f}) = {parte_real:.4f} + {parte_imag:.4f}i',
            regra=f'Transformada em omega={omega:.2f}',
        ))

    hist.adicionar(Passo(
        nivel=0,
        descricao='Transformada de Fourier calculada',
        regra='Resultado',
    ))
    return (valores, hist)


def transformada_inversa(F_vals: list, x_vals: list) -> tuple:
    """f(x) = 1/(2*pi) integral_{-inf}^{inf} F(omega)e^{i*omega*x}d_omega.

    Usa quadratura numérica sobre os valores discretos fornecidos.
    Retorna (valores: list[float], Historico).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao='Calculando transformada inversa de Fourier',
        regra='Transformada inversa',
    ))

    # Assume F_vals uniformemente espaçados
    n_omega = len(F_vals)
    if n_omega < 2:
        return ([0.0] * len(x_vals), hist)

    # Deduz omega_vals assumindo espaçamento uniforme centrado em 0
    d_omega = 1.0  # espaçamento default
    omega_start = -(n_omega - 1) / 2 * d_omega

    valores = []
    for x in x_vals:
        soma = 0.0
        for k in range(n_omega):
            omega = omega_start + k * d_omega
            F = F_vals[k]
            # F(omega) * e^{i*omega*x}
            fase = omega * x
            soma += (F.real * math.cos(fase) - F.imag * math.sin(fase)) * d_omega
        valores.append(soma / (2 * math.pi))

    hist.adicionar(Passo(
        nivel=0,
        descricao='Transformada inversa calculada',
        regra='Resultado',
    ))
    return (valores, hist)


def prop_linearidade() -> str:
    """Propriedade de linearidade da transformada de Fourier."""
    return (
        "Linearidade: F[a*f(x) + b*g(x)] = a*F[f(x)] + b*F[g(x)]\n"
        "Passo 1: A integral é linear, então distribui sobre somas.\n"
        "Passo 2: Constantes saem da integral.\n"
        "Resultado: a*F(omega) + b*G(omega)"
    )


def prop_deslocamento() -> str:
    """Propriedade de deslocamento no tempo."""
    return (
        "Deslocamento: F[f(x - x0)](omega) = e^{-i*omega*x0} * F(omega)\n"
        "Passo 1: Substituir u = x - x0 na integral.\n"
        "Passo 2: O fator e^{-i*omega*x0} sai da integral.\n"
        "Resultado: Deslocamento no tempo -> modulação na frequência."
    )


def prop_convolucao() -> str:
    """Teorema da convolução."""
    return (
        "Convolução: F[f * g](omega) = F(omega) * G(omega)\n"
        "Passo 1: Escrever a convolução como integral dupla.\n"
        "Passo 2: Trocar ordem de integração.\n"
        "Passo 3: Reconhecer as transformadas individuais.\n"
        "Resultado: Convolução no tempo = multiplicação na frequência."
    )
