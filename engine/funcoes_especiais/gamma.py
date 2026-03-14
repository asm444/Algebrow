"""Função Gamma, Beta e Stirling."""
import math
from engine.basic.passo import Passo, Historico


def gamma(z: float) -> tuple:
    """Γ(z) — para inteiros positivos: Γ(n)=(n-1)!, para meio-inteiros: usa reflexão.
    Retorna (valor: float, Historico)"""
    hist = Historico()

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Calcular Γ({z})",
        latex_antes=f"\\Gamma({z})",
        regra="Função Gamma"
    ))

    if isinstance(z, int) or (isinstance(z, float) and z == int(z)):
        n = int(z)
        if n <= 0:
            raise ValueError("Γ(z) não definida para inteiros não-positivos")
        valor = math.factorial(n - 1)
        hist.adicionar(Passo(
            nivel=2,
            descricao=f"Para inteiro positivo: Γ({n}) = ({n}-1)! = {n - 1}!",
            latex_antes=f"\\Gamma({n})",
            latex_depois=f"{n - 1}! = {valor}",
            regra="Γ(n) = (n-1)!"
        ))
        return (float(valor), hist)

    # Meio-inteiros e fracionários via Lanczos
    valor = _lanczos_gamma(z)

    hist.adicionar(Passo(
        nivel=2,
        descricao=f"Γ({z}) calculado via aproximação de Lanczos",
        latex_antes=f"\\Gamma({z})",
        latex_depois=f"{valor:.10g}",
        regra="Aproximação de Lanczos"
    ))

    return (valor, hist)


def _lanczos_gamma(z: float) -> float:
    """Aproximação de Lanczos para Γ(z), z > 0."""
    # Coeficientes de Lanczos (g=7)
    p = [
        0.99999999999980993,
        676.5203681218851,
        -1259.1392167224028,
        771.32342877765313,
        -176.61502916214059,
        12.507343278686905,
        -0.13857109526572012,
        9.9843695780195716e-6,
        1.5056327351493116e-7,
    ]

    if z < 0.5:
        # Fórmula de reflexão: Γ(z)Γ(1-z) = π/sin(πz)
        return math.pi / (math.sin(math.pi * z) * _lanczos_gamma(1 - z))

    z -= 1
    x = p[0]
    for i in range(1, len(p)):
        x += p[i] / (z + i)

    t = z + 7.5  # g + 0.5
    return math.sqrt(2 * math.pi) * (t ** (z + 0.5)) * math.exp(-t) * x


def beta(a: float, b: float) -> tuple:
    """B(a,b) = Γ(a)Γ(b)/Γ(a+b). Retorna (valor: float, Historico)"""
    hist = Historico()

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Calcular B({a}, {b})",
        latex_antes=f"B({a}, {b})",
        regra="Função Beta"
    ))

    ga, hist_a = gamma(a)
    gb, hist_b = gamma(b)
    gab, hist_ab = gamma(a + b)

    hist.adicionar(Passo(
        nivel=2,
        descricao=f"Γ({a}) = {ga}, Γ({b}) = {gb}, Γ({a + b}) = {gab}",
        latex_antes=f"\\frac{{\\Gamma({a}) \\cdot \\Gamma({b})}}{{\\Gamma({a + b})}}",
        regra="B(a,b) = Γ(a)Γ(b)/Γ(a+b)"
    ))

    valor = ga * gb / gab

    hist.adicionar(Passo(
        nivel=2,
        descricao=f"B({a}, {b}) = {ga} × {gb} / {gab} = {valor}",
        latex_depois=f"{valor:.10g}",
        regra="B(a,b) = Γ(a)Γ(b)/Γ(a+b)"
    ))

    return (valor, hist)


def stirling(n: int) -> tuple:
    """Aproximação de Stirling: n! ≈ √(2πn)(n/e)^n. Retorna (aprox: float, Historico)"""
    hist = Historico()

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Aproximação de Stirling para {n}!",
        latex_antes=f"{n}! \\approx \\sqrt{{2\\pi \\cdot {n}}} \\left(\\frac{{{n}}}{{e}}\\right)^{{{n}}}",
        regra="Aproximação de Stirling"
    ))

    raiz = math.sqrt(2 * math.pi * n)
    potencia = (n / math.e) ** n
    aprox = raiz * potencia

    hist.adicionar(Passo(
        nivel=2,
        descricao=f"√(2π·{n}) = {raiz:.6g}",
        latex_depois=f"\\sqrt{{2\\pi \\cdot {n}}} = {raiz:.6g}",
        regra="Cálculo da raiz"
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao=f"({n}/e)^{n} = {potencia:.6g}",
        latex_depois=f"\\left(\\frac{{{n}}}{{e}}\\right)^{{{n}}} = {potencia:.6g}",
        regra="Cálculo da potência"
    ))

    real = math.factorial(n)
    erro_pct = abs(aprox - real) / real * 100

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Stirling({n}) ≈ {aprox:.6g}, valor real = {real}, erro = {erro_pct:.4f}%",
        latex_depois=f"{n}! \\approx {aprox:.6g}",
        regra="Resultado de Stirling"
    ))

    return (aprox, hist)


def gamma_incompleta(a: float, x: float, n_pontos: int = 1000) -> float:
    """γ(a,x) = ∫₀ˣ t^(a-1) e^(-t) dt — por quadratura numérica (Simpson)."""
    if x <= 0:
        return 0.0

    # Regra de Simpson composta
    if n_pontos % 2 == 1:
        n_pontos += 1

    h = x / n_pontos
    soma = 0.0

    def f(t):
        if t == 0 and a < 1:
            return 0.0
        if t == 0:
            return 0.0
        return (t ** (a - 1)) * math.exp(-t)

    soma = f(0) + f(x)
    for i in range(1, n_pontos):
        t_i = i * h
        if i % 2 == 0:
            soma += 2 * f(t_i)
        else:
            soma += 4 * f(t_i)

    return soma * h / 3
