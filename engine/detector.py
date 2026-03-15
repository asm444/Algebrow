"""Detector de operação: classifica a entrada e extrai parâmetros.

Recebe texto (já convertido de LaTeX) e identifica qual tipo de operação
o usuário quer executar, extraindo os parâmetros relevantes.

Exemplos:
    detectar("DERIVAR(x^3 + sin(x), x)")
        → {'tipo': 'derivada', 'expressao': 'x^3 + sin(x)', 'variavel': 'x'}

    detectar("INTEGRAL(x^2, x, 0, 1)")
        → {'tipo': 'integral_definida', 'expressao': 'x^2', 'variavel': 'x',
           'inferior': '0', 'superior': '1'}

    detectar("LIMITE(sin(x)/x, x, 0)")
        → {'tipo': 'limite', 'expressao': 'sin(x)/x', 'variavel': 'x', 'valor': '0'}

    detectar("3/4 + sqrt(2)")
        → {'tipo': 'basico', 'expressao': '3/4 + sqrt(2)'}
"""

import re


def detectar(texto: str) -> dict:
    """Detecta a operação matemática e extrai parâmetros.

    Returns:
        dict com pelo menos 'tipo' e 'expressao'
    """
    texto = texto.strip()

    # --- Operações de cálculo (formato: OPERACAO(args...)) ---

    # DERIVAR(expr, var) ou DERIVAR(expr, var, ordem)
    m = re.match(r'^DERIVAR\((.+),\s*([a-z]),?\s*(\d+)?\)$', texto, re.DOTALL)
    if m:
        ordem = int(m.group(3)) if m.group(3) else 1
        if ordem == 1:
            return {'tipo': 'derivada', 'expressao': m.group(1).strip(), 'variavel': m.group(2)}
        return {'tipo': 'derivada_ordem', 'expressao': m.group(1).strip(),
                'variavel': m.group(2), 'ordem': ordem}

    # DERIVAR_IMPLICITA(F, x, y)
    m = re.match(r'^DERIVAR_IMPLICITA\((.+),\s*([a-z]),\s*([a-z])\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'derivada_implicita', 'expressao': m.group(1).strip(),
                'var_x': m.group(2), 'var_y': m.group(3)}

    # INTEGRAL(expr, var) — indefinida
    m = re.match(r'^INTEGRAL\((.+),\s*([a-z])\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'integral', 'expressao': m.group(1).strip(), 'variavel': m.group(2)}

    # INTEGRAL(expr, var, a, b) — definida
    m = re.match(r'^INTEGRAL\((.+),\s*([a-z]),\s*([^,]+),\s*([^)]+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'integral_definida', 'expressao': m.group(1).strip(),
                'variavel': m.group(2), 'inferior': m.group(3).strip(),
                'superior': m.group(4).strip()}

    # LIMITE(expr, var, valor)
    m = re.match(r'^LIMITE\((.+),\s*([a-z]),\s*([^)]+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'limite', 'expressao': m.group(1).strip(),
                'variavel': m.group(2), 'valor': m.group(3).strip()}

    # LIMITE_LATERAL(expr, var, valor, lado)
    m = re.match(r'^LIMITE_LATERAL\((.+),\s*([a-z]),\s*([^,]+),\s*(direita|esquerda)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'limite_lateral', 'expressao': m.group(1).strip(),
                'variavel': m.group(2), 'valor': m.group(3).strip(), 'lado': m.group(4)}

    # TAYLOR(expr, var, ponto, ordem)
    m = re.match(r'^TAYLOR\((.+),\s*([a-z]),\s*([^,]+),\s*(\d+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'taylor', 'expressao': m.group(1).strip(),
                'variavel': m.group(2), 'ponto': m.group(3).strip(),
                'ordem': int(m.group(4))}

    # EDO(expr, var_dep, var_indep, tipo_opcional)
    m = re.match(r'^EDO\((.+),\s*([a-z]),\s*([a-z])(?:,\s*(\w+))?\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'edo', 'expressao': m.group(1).strip(),
                'var_dep': m.group(2), 'var_indep': m.group(3),
                'subtipo': m.group(4) or 'auto'}

    # GRADIENTE(expr, vars...)
    m = re.match(r'^GRADIENTE\((.+),\s*([a-z,\s]+)\)$', texto, re.DOTALL)
    if m:
        vars_list = [v.strip() for v in m.group(2).split(',')]
        return {'tipo': 'gradiente', 'expressao': m.group(1).strip(), 'variaveis': vars_list}

    # JACOBIANA(exprs, vars)
    m = re.match(r'^JACOBIANA\((.+),\s*\[([a-z,\s]+)\]\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'jacobiana', 'expressao': m.group(1).strip(),
                'variaveis': [v.strip() for v in m.group(2).split(',')]}

    # HESSIANA(expr, vars)
    m = re.match(r'^HESSIANA\((.+),\s*\[([a-z,\s]+)\]\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'hessiana', 'expressao': m.group(1).strip(),
                'variaveis': [v.strip() for v in m.group(2).split(',')]}

    # --- Álgebra Linear ---

    # DETERMINANTE([[a, b], [c, d]])
    m = re.match(r'^DETERMINANTE\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'determinante', 'matriz_texto': m.group(1).strip()}

    # AUTOVALORES([[a, b], [c, d]])
    m = re.match(r'^AUTOVALORES\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'autovalores', 'matriz_texto': m.group(1).strip()}

    # GAUSS([[a, b, c], [d, e, f]])
    m = re.match(r'^GAUSS\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'gauss', 'matriz_texto': m.group(1).strip()}

    # --- Complexos ---

    # COMPLEXO(expressao)
    m = re.match(r'^COMPLEXO\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'complexo', 'expressao': m.group(1).strip()}

    # POLAR(expressao)
    m = re.match(r'^POLAR\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'polar', 'expressao': m.group(1).strip()}

    # LAPLACE(expr, var)
    m = re.match(r'^LAPLACE\((.+),\s*([a-z])\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'laplace', 'expressao': m.group(1).strip(), 'variavel': m.group(2)}

    # --- Funções Especiais ---

    # GAMMA(n)
    m = re.match(r'^GAMMA\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'gamma', 'argumento': m.group(1).strip()}

    # BESSEL(n, x)
    m = re.match(r'^BESSEL\((\d+),\s*(.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'bessel', 'ordem': int(m.group(1)), 'argumento': m.group(2).strip()}

    # LEGENDRE(n, x)
    m = re.match(r'^LEGENDRE\((\d+),\s*(.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'legendre', 'grau': int(m.group(1)), 'argumento': m.group(2).strip()}

    # --- Fourier ---

    # FOURIER(expr, L, n)
    m = re.match(r'^FOURIER\((.+),\s*([^,]+),\s*(\d+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'fourier', 'expressao': m.group(1).strip(),
                'L': m.group(2).strip(), 'termos': int(m.group(3))}

    # TRANSFORMADA_FOURIER(expr, var)
    m = re.match(r'^TRANSFORMADA_FOURIER\((.+),\s*([a-z])\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'transformada_fourier', 'expressao': m.group(1).strip(),
                'variavel': m.group(2)}

    # --- Geometria Diferencial ---

    # CURVATURA(componentes...)
    m = re.match(r'^CURVATURA\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'curvatura', 'expressao': m.group(1).strip()}

    # FRENET(componentes...)
    m = re.match(r'^FRENET\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'frenet', 'expressao': m.group(1).strip()}

    # --- Cálculo Variacional ---

    # EULER_LAGRANGE(F, x, y)
    m = re.match(r'^EULER_LAGRANGE\((.+),\s*([a-z]),\s*([a-z])\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'euler_lagrange', 'expressao': m.group(1).strip(),
                'var_indep': m.group(2), 'var_dep': m.group(3)}

    # --- Equações Integrais ---

    # FREDHOLM(f, K, lambda)
    m = re.match(r'^FREDHOLM\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'fredholm', 'expressao': m.group(1).strip()}

    # VOLTERRA(f, K, lambda)
    m = re.match(r'^VOLTERRA\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'volterra', 'expressao': m.group(1).strip()}

    # --- EDPs ---

    # CALOR(expr, L, alpha)
    m = re.match(r'^CALOR\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'calor', 'expressao': m.group(1).strip()}

    # ONDA(expr, L, c)
    m = re.match(r'^ONDA\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'onda', 'expressao': m.group(1).strip()}

    # --- Grupos ---

    # GRUPO(tipo, n)
    m = re.match(r'^GRUPO\((\w+),\s*(\d+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'grupo', 'grupo_tipo': m.group(1), 'n': int(m.group(2))}

    # CAYLEY(tipo, n)
    m = re.match(r'^CAYLEY\((\w+),\s*(\d+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'cayley', 'grupo_tipo': m.group(1), 'n': int(m.group(2))}

    # --- Aplicações do Cálculo ---

    # MAXMIN(expr, var, a, b)
    m = re.match(r'^MAXMIN\((.+),\s*([a-z]),\s*([^,]+),\s*([^)]+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'maxmin', 'expressao': m.group(1).strip(),
                'variavel': m.group(2), 'a': m.group(3).strip(), 'b': m.group(4).strip()}

    # VOLUME_REVOLUCAO(expr, var, a, b)
    m = re.match(r'^VOLUME_REVOLUCAO\((.+),\s*([a-z]),\s*([^,]+),\s*([^)]+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'volume_revolucao', 'expressao': m.group(1).strip(),
                'variavel': m.group(2), 'a': m.group(3).strip(), 'b': m.group(4).strip()}

    # COMPRIMENTO_ARCO(expr, var, a, b)
    m = re.match(r'^COMPRIMENTO_ARCO\((.+),\s*([a-z]),\s*([^,]+),\s*([^)]+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'comprimento_arco', 'expressao': m.group(1).strip(),
                'variavel': m.group(2), 'a': m.group(3).strip(), 'b': m.group(4).strip()}

    # --- Tensores ---

    # CHRISTOFFEL(metrica)
    m = re.match(r'^CHRISTOFFEL\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'christoffel', 'expressao': m.group(1).strip()}

    # RIEMANN(metrica)
    m = re.match(r'^RIEMANN\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'riemann', 'expressao': m.group(1).strip()}

    # --- Sturm-Liouville ---

    # STURM_LIOUVILLE(p, q, rho, a, b)
    m = re.match(r'^STURM_LIOUVILLE\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'sturm_liouville', 'expressao': m.group(1).strip()}

    # GREEN(operador, a, b)
    m = re.match(r'^GREEN\((.+)\)$', texto, re.DOTALL)
    if m:
        return {'tipo': 'green', 'expressao': m.group(1).strip()}

    # --- Expressão contendo operação de cálculo como sub-expressão ---
    # Ex: "INTEGRAL(x^2, x) - x^3/3" ou "2 * DERIVAR(x^2, x)"
    if 'INTEGRAL(' in texto or 'DERIVAR(' in texto or 'LIMITE(' in texto:
        return {'tipo': 'expressao_simbolica', 'expressao': texto}

    # --- Fallback: expressão básica ---
    return {'tipo': 'basico', 'expressao': texto}
