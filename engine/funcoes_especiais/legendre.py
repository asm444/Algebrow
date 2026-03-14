"""Polinômios de Legendre P_l(x) e harmônicos esféricos."""
import math
from engine.basic.passo import Passo, Historico


def legendre_p(l: int, x_val: float = None) -> tuple:
    """P_l(x) via fórmula de Rodrigues: P_l = 1/(2^l l!) d^l/dx^l (x²-1)^l.
    Implementação via recursão de Bonnet: (l+1)P_{l+1} = (2l+1)xP_l - lP_{l-1}.
    Se x_val dado, avalia numericamente. Retorna (coeficientes: list, Historico)"""
    hist = Historico()

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Calcular P_{l}(x) via recursão de Bonnet",
        latex_antes=f"P_{{{l}}}(x)",
        regra="Polinômios de Legendre"
    ))

    # Construir coeficientes por recursão
    # P_0 = [1], P_1 = [0, 1] (representam coefs de x^0, x^1, ...)
    if l == 0:
        coefs = [1.0]
        hist.adicionar(Passo(
            nivel=2, descricao="P_0(x) = 1",
            latex_depois="P_0(x) = 1", regra="Caso base"
        ))
    elif l == 1:
        coefs = [0.0, 1.0]
        hist.adicionar(Passo(
            nivel=2, descricao="P_1(x) = x",
            latex_depois="P_1(x) = x", regra="Caso base"
        ))
    else:
        p_prev = [1.0]       # P_0
        p_curr = [0.0, 1.0]  # P_1

        for k in range(1, l):
            # (k+1)P_{k+1} = (2k+1)x·P_k - k·P_{k-1}
            # Multiplicar P_k por x: shift coeficientes
            xp = [0.0] + p_curr  # x * P_k

            # Escalar (2k+1) * x * P_k
            xp_scaled = [c * (2 * k + 1) for c in xp]

            # Escalar k * P_{k-1}
            kp = [c * k for c in p_prev]

            # Subtrair: garantir mesmo tamanho
            tamanho = max(len(xp_scaled), len(kp))
            while len(xp_scaled) < tamanho:
                xp_scaled.append(0.0)
            while len(kp) < tamanho:
                kp.append(0.0)

            p_next = [(xp_scaled[i] - kp[i]) / (k + 1) for i in range(tamanho)]

            hist.adicionar(Passo(
                nivel=3,
                descricao=f"P_{{{k + 1}}}(x) = ((2·{k}+1)·x·P_{{{k}}} - {k}·P_{{{k - 1}}}) / {k + 1}",
                regra="Recursão de Bonnet"
            ))

            p_prev = p_curr
            p_curr = p_next

        coefs = p_curr

    # Limpar coeficientes muito pequenos (artefatos numéricos)
    coefs = [round(c, 12) for c in coefs]

    # Gerar LaTeX do polinômio
    latex = _coefs_para_latex(coefs, l)
    hist.adicionar(Passo(
        nivel=1,
        descricao=f"P_{{{l}}}(x) = {latex}",
        latex_depois=f"P_{{{l}}}(x) = {latex}",
        regra="Resultado"
    ))

    if x_val is not None:
        valor = sum(c * (x_val ** i) for i, c in enumerate(coefs))
        hist.adicionar(Passo(
            nivel=1,
            descricao=f"P_{{{l}}}({x_val}) = {valor}",
            latex_depois=f"P_{{{l}}}({x_val}) = {valor}",
            regra="Avaliação numérica"
        ))

    return (coefs, hist)


def _coefs_para_latex(coefs: list, l: int) -> str:
    """Converte lista de coeficientes [a0, a1, ...] para string LaTeX."""
    termos = []
    for i, c in enumerate(coefs):
        if c == 0:
            continue
        if i == 0:
            termos.append(f"{c:g}")
        elif i == 1:
            if c == 1:
                termos.append("x")
            elif c == -1:
                termos.append("-x")
            else:
                termos.append(f"{c:g}x")
        else:
            if c == 1:
                termos.append(f"x^{{{i}}}")
            elif c == -1:
                termos.append(f"-x^{{{i}}}")
            else:
                termos.append(f"{c:g}x^{{{i}}}")

    return " + ".join(termos).replace("+ -", "- ") if termos else "0"


def legendre_associado(l: int, m: int) -> tuple:
    """P_l^m(x) via P_l^m(x) = (-1)^m (1-x²)^{m/2} d^m/dx^m P_l(x).
    Retorna (coeficientes, Historico)"""
    hist = Historico()

    if abs(m) > l:
        hist.adicionar(Passo(
            nivel=1, descricao=f"|m|={abs(m)} > l={l}, P_l^m = 0",
            regra="Condição de validade"
        ))
        return ([], hist)

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Calcular P_{{{l}}}^{{{m}}}(x)",
        latex_antes=f"P_{{{l}}}^{{{m}}}(x)",
        regra="Legendre associado"
    ))

    # Obter coeficientes de P_l
    coefs_pl, _ = legendre_p(l)

    # Derivar m vezes
    coefs = list(coefs_pl)
    for d in range(abs(m)):
        coefs = _derivar_coefs(coefs)

    # Multiplicar por (-1)^m (1-x²)^(m/2)
    # Para m positivo, o resultado envolve (1-x²)^(m/2) que não é polinomial
    # Retornamos os coeficientes da derivada, o fator (1-x²)^(m/2) é implícito

    sinal = (-1) ** abs(m)
    coefs = [c * sinal for c in coefs]

    if m < 0:
        fator = ((-1) ** (-m)) * math.factorial(l + m) / math.factorial(l - m)
        coefs = [c * fator for c in coefs]

    hist.adicionar(Passo(
        nivel=2,
        descricao=f"Coeficientes da parte polinomial (fator (1-x²)^{{{abs(m)}/2}} implícito): {coefs}",
        regra="Derivação de P_l"
    ))

    return (coefs, hist)


def _derivar_coefs(coefs: list) -> list:
    """Derivar polinômio dado por coeficientes [a0, a1, a2, ...] -> [a1, 2*a2, 3*a3, ...]."""
    if len(coefs) <= 1:
        return [0.0]
    return [coefs[i] * i for i in range(1, len(coefs))]


def harmonico_esferico(l: int, m: int) -> tuple:
    """Y_l^m(θ,φ) = C·P_l^m(cosθ)·e^(imφ). Retorna (latex: str, Historico)"""
    hist = Historico()

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Calcular Y_{{{l}}}^{{{m}}}(θ,φ)",
        regra="Harmônicos esféricos"
    ))

    # Fator de normalização
    # C = √((2l+1)/(4π) · (l-|m|)!/(l+|m|)!)
    num = (2 * l + 1) * math.factorial(l - abs(m))
    den = 4 * math.pi * math.factorial(l + abs(m))
    C = math.sqrt(num / den)

    if m < 0:
        C *= (-1) ** m

    hist.adicionar(Passo(
        nivel=2,
        descricao=f"Fator de normalização C = √((2·{l}+1)/(4π) · ({l}-{abs(m)})!/({l}+{abs(m)})!) = {C:.6g}",
        regra="Normalização"
    ))

    latex = (f"Y_{{{l}}}^{{{m}}}(\\theta, \\phi) = {C:.6g} \\cdot "
             f"P_{{{l}}}^{{{m}}}(\\cos\\theta) \\cdot e^{{i{m}\\phi}}")

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Y_{{{l}}}^{{{m}}}(θ,φ) = {C:.6g} · P_{{{l}}}^{{{m}}}(cosθ) · e^(i{m}φ)",
        latex_depois=latex,
        regra="Resultado"
    ))

    return (latex, hist)


def ortogonalidade_legendre(l1: int, l2: int, n_pontos: int = 2000) -> tuple:
    """Verifica ∫₋₁¹ P_l1·P_l2 dx = 2δ/(2l+1). Retorna (valor: str, Historico)"""
    hist = Historico()

    hist.adicionar(Passo(
        nivel=1,
        descricao=f"Verificar ortogonalidade: ∫₋₁¹ P_{{{l1}}}(x)·P_{{{l2}}}(x) dx",
        latex_antes=f"\\int_{{-1}}^{{1}} P_{{{l1}}}(x) P_{{{l2}}}(x) \\, dx",
        regra="Ortogonalidade de Legendre"
    ))

    coefs1, _ = legendre_p(l1)
    coefs2, _ = legendre_p(l2)

    # Integração numérica por Simpson
    if n_pontos % 2 == 1:
        n_pontos += 1

    a, b = -1.0, 1.0
    h = (b - a) / n_pontos

    def avaliar_poly(coefs, x):
        return sum(c * (x ** i) for i, c in enumerate(coefs))

    def f(x):
        return avaliar_poly(coefs1, x) * avaliar_poly(coefs2, x)

    soma = f(a) + f(b)
    for i in range(1, n_pontos):
        x_i = a + i * h
        if i % 2 == 0:
            soma += 2 * f(x_i)
        else:
            soma += 4 * f(x_i)

    integral = soma * h / 3

    if l1 == l2:
        esperado = 2.0 / (2 * l1 + 1)
        hist.adicionar(Passo(
            nivel=2,
            descricao=f"l1 = l2 = {l1}: esperado = 2/(2·{l1}+1) = {esperado:.10g}",
            regra="Caso l1 = l2"
        ))
    else:
        esperado = 0.0
        hist.adicionar(Passo(
            nivel=2,
            descricao=f"l1 ≠ l2: esperado = 0",
            regra="Caso l1 ≠ l2"
        ))

    resultado = f"∫ P_{l1}·P_{l2} dx = {integral:.10g} (esperado: {esperado:.10g})"

    hist.adicionar(Passo(
        nivel=1,
        descricao=resultado,
        latex_depois=f"\\int_{{-1}}^{{1}} P_{{{l1}}} P_{{{l2}}} dx = {integral:.6g}",
        regra="Resultado da integração"
    ))

    return (resultado, hist)
