"""Teoria de Sturm-Liouville: [p(x)y']' + [q(x) + λw(x)]y = 0

Implementa autovalores via shooting method, autofunções clássicas
(Fourier, Bessel, Legendre) e expansão em séries de autofunções.
"""

import ast
import math
import operator

from engine.basic.passo import Passo, Historico


# ---------------------------------------------------------------------------
# Avaliador seguro de expressões (sem eval)
# ---------------------------------------------------------------------------

_NAMESPACE_SEGURO = {
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
    """Avalia expressão string de forma segura."""
    ns = {**_NAMESPACE_SEGURO, **variaveis}
    tree = ast.parse(expr_str, mode='eval')
    return float(_eval_node(tree, ns))


# ---------------------------------------------------------------------------
# Shooting method para autovalores SL
# ---------------------------------------------------------------------------

def _rk4_sl(p_str, q_str, w_str, lam, a, b, y0, yp0, N=200):
    """Integra [p(x)y']' + [q(x) + λw(x)]y = 0 via RK4.

    Reescrita como sistema:
        y' = z
        z' = -[p'(x)z + (q(x) + λw(x))y] / p(x)

    Para simplificar, usamos diferenças finitas para p'(x).
    """
    h = (b - a) / N
    x = a
    y = y0
    z = yp0  # z = y'

    for _ in range(N):
        def f_sys(xi, yi, zi):
            p_val = _avaliar(p_str, x=xi)
            q_val = _avaliar(q_str, x=xi)
            w_val = _avaliar(w_str, x=xi)
            # p'(x) por diferença central
            dx = h * 0.01
            pp = (_avaliar(p_str, x=xi + dx) - _avaliar(p_str, x=xi - dx)) / (2 * dx)
            if abs(p_val) < 1e-15:
                p_val = 1e-15
            dz = -(pp * zi + (q_val + lam * w_val) * yi) / p_val
            return zi, dz

        k1y, k1z = f_sys(x, y, z)
        k2y, k2z = f_sys(x + h/2, y + h/2*k1y, z + h/2*k1z)
        k3y, k3z = f_sys(x + h/2, y + h/2*k2y, z + h/2*k2z)
        k4y, k4z = f_sys(x + h, y + h*k3y, z + h*k3z)

        y += h/6 * (k1y + 2*k2y + 2*k3y + k4y)
        z += h/6 * (k1z + 2*k2z + 2*k3z + k4z)
        x += h

    return y, z


def autovalores_sl(p_str, q_str, w_str, a, b,
                   condicoes='dirichlet', n_autovalores=5):
    """Encontra autovalores do problema de Sturm-Liouville por shooting method.

    Parâmetros:
        p_str, q_str, w_str: expressões em x para p(x), q(x), w(x)
        a, b: intervalo [a, b]
        condicoes: 'dirichlet' (y(a)=y(b)=0) ou 'neumann' (y'(a)=y'(b)=0)
        n_autovalores: número de autovalores a encontrar

    Retorna:
        (autovalores: list[float], Historico)
    """
    hist = Historico()
    hist.adicionar(Passo(
        1, "Configuração do problema de Sturm-Liouville",
        latex_antes=f"[p(x)y']' + [q(x) + \\lambda w(x)]y = 0",
        latex_depois=f"p(x) = {p_str},\\; q(x) = {q_str},\\; w(x) = {w_str}",
        regra="Problema de Sturm-Liouville"
    ))

    if condicoes == 'dirichlet':
        y0, yp0 = 0.0, 1.0  # y(a)=0, y'(a)=1 (normalização)
        hist.adicionar(Passo(2, "Condições de Dirichlet: y(a)=0, y(b)=0",
                             regra="Condições de contorno"))
    else:
        y0, yp0 = 1.0, 0.0  # y'(a)=0, y(a)=1
        hist.adicionar(Passo(2, "Condições de Neumann: y'(a)=0, y'(b)=0",
                             regra="Condições de contorno"))

    hist.adicionar(Passo(
        2, "Aplica shooting method: varia λ até que condição em x=b seja satisfeita",
        regra="Shooting method"
    ))

    # Busca autovalores varrendo λ e detectando mudanças de sinal
    autovalores = []
    lam_min, lam_max = 0.01, (n_autovalores + 2) ** 2 * (math.pi / (b - a)) ** 2
    N_scan = max(2000, n_autovalores * 400)
    dlam = (lam_max - lam_min) / N_scan

    def objetivo(lam):
        yb, zb = _rk4_sl(p_str, q_str, w_str, lam, a, b, y0, yp0)
        if condicoes == 'dirichlet':
            return yb
        return zb

    prev_val = objetivo(lam_min)
    for i in range(1, N_scan + 1):
        lam_i = lam_min + i * dlam
        cur_val = objetivo(lam_i)
        if prev_val * cur_val < 0:
            # Bisecção para refinar
            lo, hi = lam_i - dlam, lam_i
            for _ in range(60):
                mid = (lo + hi) / 2
                if objetivo(lo) * objetivo(mid) < 0:
                    hi = mid
                else:
                    lo = mid
            autovalor = (lo + hi) / 2
            autovalores.append(round(autovalor, 8))
            hist.adicionar(Passo(
                3, f"Autovalor encontrado: λ_{len(autovalores)} ≈ {autovalor:.6f}",
                latex_depois=f"\\lambda_{{{len(autovalores)}}} \\approx {autovalor:.6f}",
                regra="Bisecção"
            ))
            if len(autovalores) >= n_autovalores:
                break
        prev_val = cur_val

    hist.adicionar(Passo(
        1, f"Encontrados {len(autovalores)} autovalores no intervalo [{a}, {b}]",
        latex_depois=f"\\lambda = {autovalores}",
        regra="Resultado"
    ))

    return autovalores, hist


# ---------------------------------------------------------------------------
# Autofunções clássicas
# ---------------------------------------------------------------------------

def autofuncoes_sl(tipo, n):
    """Autofunções para problemas de Sturm-Liouville clássicos.

    Parâmetros:
        tipo: 'fourier', 'bessel' ou 'legendre'
        n: índice da autofunção

    Retorna:
        (descricao_latex: str, Historico)
    """
    hist = Historico()

    if tipo == 'fourier':
        hist.adicionar(Passo(
            1, f"Autofunções de Fourier para n={n}",
            latex_antes="y'' + \\lambda y = 0,\\; y(0) = y(L) = 0",
            regra="Problema de Sturm-Liouville de Fourier"
        ))
        hist.adicionar(Passo(
            2, "Equação característica: r² + λ = 0 → r = ±i√λ",
            latex_antes="r^2 + \\lambda = 0",
            latex_depois="r = \\pm i\\sqrt{\\lambda}",
            regra="Equação característica"
        ))
        hist.adicionar(Passo(
            2, f"Autovalor: λ_n = (nπ/L)², Autofunções: sin(nπx/L) e cos(nπx/L)",
            latex_depois=f"\\lambda_{{{n}}} = \\left(\\frac{{{n}\\pi}}{{L}}\\right)^2",
            regra="Condições de contorno de Dirichlet"
        ))

        latex = (f"\\phi_{{{n}}}(x) = \\sin\\left(\\frac{{{n}\\pi x}}{{L}}\\right), \\quad "
                 f"\\psi_{{{n}}}(x) = \\cos\\left(\\frac{{{n}\\pi x}}{{L}}\\right)")
        hist.adicionar(Passo(
            1, f"Autofunções de Fourier de ordem {n}",
            latex_depois=latex,
            regra="Resultado"
        ))
        return latex, hist

    elif tipo == 'bessel':
        hist.adicionar(Passo(
            1, f"Autofunções de Bessel para n={n}",
            latex_antes="x^2 y'' + x y' + (x^2 - \\nu^2)y = 0",
            regra="Equação de Bessel"
        ))
        hist.adicionar(Passo(
            2, "Solução em série de Frobenius converge para funções de Bessel J_ν(x)",
            regra="Método de Frobenius"
        ))
        latex = f"\\phi_{{{n}}}(x) = J_{{\\nu}}\\left(\\frac{{\\alpha_{{{n}}} x}}{{a}}\\right)"
        hist.adicionar(Passo(
            1, f"Autofunção de Bessel de ordem {n}",
            latex_depois=latex,
            justificativa="α_n é o n-ésimo zero de J_ν",
            regra="Resultado"
        ))
        return latex, hist

    elif tipo == 'legendre':
        hist.adicionar(Passo(
            1, f"Polinômio de Legendre P_{n}(x)",
            latex_antes="(1-x^2)y'' - 2xy' + n(n+1)y = 0",
            regra="Equação de Legendre"
        ))
        # Fórmula de Rodrigues
        hist.adicionar(Passo(
            2, "Usando a fórmula de Rodrigues",
            latex_depois=f"P_{{{n}}}(x) = \\frac{{1}}{{2^{{{n}}} {n}!}} "
                         f"\\frac{{d^{{{n}}}}}{{dx^{{{n}}}}}(x^2 - 1)^{{{n}}}",
            regra="Fórmula de Rodrigues"
        ))
        latex = (f"P_{{{n}}}(x) = \\frac{{1}}{{2^{{{n}}} {n}!}} "
                 f"\\frac{{d^{{{n}}}}}{{dx^{{{n}}}}}(x^2 - 1)^{{{n}}}")
        hist.adicionar(Passo(1, f"Polinômio de Legendre de grau {n}",
                             latex_depois=latex, regra="Resultado"))
        return latex, hist

    else:
        raise ValueError(f"Tipo desconhecido: {tipo}. Use 'fourier', 'bessel' ou 'legendre'.")


# ---------------------------------------------------------------------------
# Expansão em autofunções
# ---------------------------------------------------------------------------

def expansao_autofuncoes(f_str, tipo, n_termos=10):
    """Expande f(x) em série de autofunções.

    Para tipo='fourier', calcula os coeficientes da série de Fourier seno
    no intervalo [0, L] com L=pi por padrão:
        f(x) = Σ Bₙ sin(nπx/L)
        Bₙ = (2/L) ∫₀ᴸ f(x) sin(nπx/L) dx

    Retorna:
        (coeficientes: list[float], Historico)
    """
    hist = Historico()
    L = math.pi  # intervalo padrão

    hist.adicionar(Passo(
        1, f"Expansão de f(x) = {f_str} em série de autofunções ({tipo})",
        latex_antes=f"f(x) = {f_str}",
        regra="Expansão em autofunções"
    ))

    if tipo == 'fourier':
        hist.adicionar(Passo(
            2, "Coeficientes de Fourier-seno: Bₙ = (2/L) ∫₀ᴸ f(x) sin(nπx/L) dx",
            latex_depois=f"B_n = \\frac{{2}}{{L}} \\int_0^L f(x) \\sin\\left(\\frac{{n\\pi x}}{{L}}\\right) dx",
            regra="Fórmula dos coeficientes"
        ))

        coeficientes = []
        N_quad = 500  # pontos para integração numérica (Simpson)

        for n in range(1, n_termos + 1):
            # Integração por Simpson composta
            h_int = L / N_quad
            soma = 0.0
            for i in range(N_quad + 1):
                xi = i * h_int
                fi = _avaliar(f_str, x=xi)
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
                regra="Integração numérica (Simpson)"
            ))

        hist.adicionar(Passo(
            1, f"Expansão com {n_termos} termos calculada",
            latex_depois=f"f(x) \\approx \\sum_{{n=1}}^{{{n_termos}}} B_n \\sin\\left(\\frac{{n\\pi x}}{{L}}\\right)",
            regra="Resultado"
        ))
        return coeficientes, hist

    else:
        raise ValueError(f"Expansão para tipo '{tipo}' não implementada. Use 'fourier'.")
