"""Equações integrais de Fredholm e Volterra."""

import math
from engine.basic.passo import Passo, Historico


# Namespace seguro para avaliação de expressões
_NAMESPACE_SEGURO = {
    'sqrt': math.sqrt,
    'log': math.log10,
    'ln': math.log,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'abs': abs,
    'pi': math.pi,
    'e': math.e,
    'exp': math.exp,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
}


def _preparar_expressao(expressao: str) -> str:
    """Converte notações comuns para Python válido."""
    expr = expressao.strip()
    resultado = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c == '^':
            resultado.append('**')
            i += 1
            continue
        if (i > 0 and resultado and
                expr[i - 1].isdigit() and c.isalpha()):
            resultado.append('*')
        resultado.append(c)
        i += 1
    return ''.join(resultado)


def _avaliar_expr(expr_str: str, variaveis: dict) -> float:
    """Avalia expressão com namespace seguro e variáveis fornecidas.

    Usa eval com namespace restrito -- mesma abordagem de engine/funcoes/grafico.py.
    """
    ns = dict(_NAMESPACE_SEGURO)
    ns.update(variaveis)
    expr = _preparar_expressao(expr_str)
    return float(eval(expr, {"__builtins__": {}}, ns))  # noqa: S307


def _simpson(f, a: float, b: float, n: int = 200) -> float:
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


def fredholm_2especie(kernel_str: str, f_str: str, lam: float,
                      a: float, b: float, n_pontos: int = 50) -> tuple:
    """Resolve phi(x) = f(x) + lam * integral_a^b K(x,t)*phi(t)dt por iteração de Neumann.

    Retorna (solucao_pontos: list[tuple(x, phi(x))], Historico).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao=f'Resolvendo equação de Fredholm 2a espécie: phi = f + {lam}*K*phi',
        regra='Fredholm 2a espécie',
    ))

    # Pontos de discretização
    xs = [a + i * (b - a) / (n_pontos - 1) for i in range(n_pontos)]
    h = (b - a) / (n_pontos - 1)

    # Iteração de Neumann: phi_{k+1}(x) = f(x) + lam * integral K(x,t)*phi_k(t)dt
    # Inicialização: phi_0(x) = f(x)
    phi = [_avaliar_expr(f_str, {'x': xi}) for xi in xs]
    hist.adicionar(Passo(
        nivel=2,
        descricao='Inicialização: phi_0(x) = f(x)',
        regra='Iteração 0',
    ))

    max_iter = 20
    tol = 1e-8
    for it in range(1, max_iter + 1):
        phi_novo = []
        for i, xi in enumerate(xs):
            f_val = _avaliar_expr(f_str, {'x': xi})
            # Integral por regra do trapézio
            integral = 0.0
            for j in range(n_pontos):
                tj = xs[j]
                K_val = _avaliar_expr(kernel_str, {'x': xi, 't': tj})
                peso = h if 0 < j < n_pontos - 1 else h / 2
                integral += K_val * phi[j] * peso
            phi_novo.append(f_val + lam * integral)

        # Convergência
        diff = max(abs(phi_novo[k] - phi[k]) for k in range(n_pontos))
        phi = phi_novo
        hist.adicionar(Passo(
            nivel=3,
            descricao=f'Iteração {it}: max|phi_new - phi_old| = {diff:.2e}',
            regra=f'Iteração {it}',
        ))
        if diff < tol:
            hist.adicionar(Passo(
                nivel=2,
                descricao=f'Convergiu em {it} iterações',
                regra='Convergência',
            ))
            break

    solucao = list(zip(xs, phi))
    hist.adicionar(Passo(
        nivel=0,
        descricao='Equação de Fredholm resolvida',
        regra='Resultado',
    ))
    return (solucao, hist)


def volterra_2especie(kernel_str: str, f_str: str, lam: float,
                      a: float, x_max: float, n_pontos: int = 50) -> tuple:
    """Resolve phi(x) = f(x) + lam * integral_a^x K(x,t)*phi(t)dt.

    Usa método de marcha (resolução progressiva).
    Retorna (solucao_pontos: list[tuple(x, phi(x))], Historico).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao=f'Resolvendo equação de Volterra 2a espécie',
        regra='Volterra 2a espécie',
    ))

    xs = [a + i * (x_max - a) / (n_pontos - 1) for i in range(n_pontos)]
    h = (x_max - a) / (n_pontos - 1)
    phi = [0.0] * n_pontos

    # Marcha: para cada x_i, resolver usando phi já conhecido para t <= x_i
    for i in range(n_pontos):
        xi = xs[i]
        f_val = _avaliar_expr(f_str, {'x': xi})

        # Integral de a até x_i por trapézio
        integral = 0.0
        for j in range(i + 1):
            tj = xs[j]
            K_val = _avaliar_expr(kernel_str, {'x': xi, 't': tj})
            if j == 0 or j == i:
                peso = h / 2
            else:
                peso = h
            if j < i:
                integral += K_val * phi[j] * peso
            else:
                # j == i: phi[i] é desconhecido, resolver implicitamente
                # phi[i] = f_val + lam * (integral_parcial + K(x_i,x_i)*phi[i]*h/2)
                # phi[i] * (1 - lam*K(x_i,x_i)*h/2) = f_val + lam*integral_parcial
                K_ii = K_val
                denom = 1.0 - lam * K_ii * h / 2
                if abs(denom) < 1e-15:
                    phi[i] = f_val + lam * integral
                else:
                    phi[i] = (f_val + lam * integral) / denom

    solucao = list(zip(xs, phi))
    hist.adicionar(Passo(
        nivel=0,
        descricao='Equação de Volterra resolvida',
        regra='Resultado',
    ))
    return (solucao, hist)


def serie_neumann(kernel_str: str, f_str: str, lam: float,
                  a: float, b: float, n_iter: int = 5) -> tuple:
    """Série de Neumann: phi = f + lam*K*f + lam^2*K^2*f + ...

    Retorna (iteracoes_latex: list[str], Historico).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao='Construindo série de Neumann',
        regra='Série de Neumann',
    ))

    iteracoes_latex = []

    # phi_0 = f
    iteracoes_latex.append(f'\\phi_0(x) = f(x) = {f_str}')
    hist.adicionar(Passo(
        nivel=2,
        descricao='phi_0 = f',
        latex_depois=iteracoes_latex[-1],
        regra='Termo 0',
    ))

    for k in range(1, n_iter + 1):
        lam_k = f'\\lambda^{{{k}}}' if k > 1 else '\\lambda'
        K_k = f'K^{{{k}}}' if k > 1 else 'K'
        termo = f'\\phi_{{{k}}}(x) = f(x) + {lam_k} {K_k} f(x)'
        iteracoes_latex.append(termo)
        hist.adicionar(Passo(
            nivel=2,
            descricao=f'Termo {k} da série de Neumann',
            latex_depois=termo,
            regra=f'Termo {k}',
        ))

    hist.adicionar(Passo(
        nivel=0,
        descricao='Série de Neumann construída',
        regra='Resultado',
    ))

    return (iteracoes_latex, hist)
