"""Aplicacoes do calculo diferencial e integral.

Conteudo:
- Taxa de variacao
- Maximos e minimos
- Pontos de inflexao
- Regra de L'Hopital estendida
- Teorema do valor medio
- Esboco de curvas
- Problemas de otimizacao
- Solidos de revolucao (volume)
- Comprimento de arco
"""

import math
from .arvore import NoExpressao, num, var, op, func
from .derivada import derivar, derivar_ordem, simplificar_no
from .integral import _integrar_interno, _contem_variavel
from .limite import limite, limite_infinito
from engine.basic.passo import Passo, Historico


# ============================================================
# Taxa de variacao
# ============================================================

def taxa_variacao(no: NoExpressao, variavel: str, ponto: float,
                  historico: Historico = None) -> float:
    """Calcula a taxa de variacao instantanea f'(a).

    Retorna o valor numerico de f'(ponto).
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Taxa de variacao instantanea em {variavel} = {ponto}',
            regra='Taxa de variacao',
        ))

    df = simplificar_no(derivar(no, variavel, historico))

    resultado = df.avaliar({variavel: ponto})

    if historico is not None:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f"f'({ponto}) = {resultado}",
            regra='Taxa de variacao - resultado',
        ))

    return resultado


# ============================================================
# Maximos e minimos
# ============================================================

def encontrar_criticos(no: NoExpressao, variavel: str, intervalo: tuple = None,
                       historico: Historico = None) -> list:
    """Encontra pontos criticos: f'(x) = 0.

    Usa busca numerica no intervalo dado.
    Retorna lista de dicionarios com x, f(x), tipo ('maximo', 'minimo', 'indefinido').
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao='Encontrando pontos criticos: f\'(x) = 0',
            regra='Pontos criticos',
        ))

    df = simplificar_no(derivar(no, variavel, historico))
    d2f = simplificar_no(derivar(df, variavel))

    if intervalo is None:
        intervalo = (-10, 10)

    a, b = intervalo
    pontos_criticos = _encontrar_zeros_numericos(df, variavel, a, b)

    resultados = []
    for xc in pontos_criticos:
        try:
            fx = no.avaliar({variavel: xc})
            d2fx = d2f.avaliar({variavel: xc})

            if d2fx < -1e-8:
                tipo = 'maximo'
            elif d2fx > 1e-8:
                tipo = 'minimo'
            else:
                tipo = 'indefinido'

            resultados.append({
                'x': xc,
                'fx': fx,
                'tipo': tipo,
            })

            if historico is not None:
                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'Ponto critico em x = {xc}: f(x) = {fx}, f\'\'(x) = {d2fx} -> {tipo}',
                    regra='Teste da 2a derivada',
                ))
        except (ValueError, ZeroDivisionError, OverflowError):
            continue

    return resultados


# ============================================================
# Pontos de inflexao
# ============================================================

def encontrar_inflexao(no: NoExpressao, variavel: str, intervalo: tuple = None,
                       historico: Historico = None) -> list:
    """Encontra pontos de inflexao: f''(x) = 0 com mudanca de concavidade.

    Retorna lista de dicionarios com x, f(x).
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao='Encontrando pontos de inflexao: f\'\'(x) = 0',
            regra='Pontos de inflexao',
        ))

    d2f = simplificar_no(derivar_ordem(no, variavel, 2))

    if intervalo is None:
        intervalo = (-10, 10)

    a, b = intervalo
    candidatos = _encontrar_zeros_numericos(d2f, variavel, a, b)

    resultados = []
    for xc in candidatos:
        # Verificar mudanca de concavidade
        delta = 0.01
        try:
            antes = d2f.avaliar({variavel: xc - delta})
            depois = d2f.avaliar({variavel: xc + delta})

            if (antes > 0 and depois < 0) or (antes < 0 and depois > 0):
                fx = no.avaliar({variavel: xc})
                resultados.append({
                    'x': xc,
                    'fx': fx,
                })

                if historico is not None:
                    historico.adicionar(Passo(
                        nivel=2,
                        descricao=f'Ponto de inflexao em x = {xc}: f(x) = {fx}',
                        regra='Inflexao confirmada',
                    ))
        except (ValueError, ZeroDivisionError, OverflowError):
            continue

    return resultados


# ============================================================
# L'Hopital estendida
# ============================================================

def lhopital_estendido(numerador: NoExpressao, denominador: NoExpressao,
                       variavel: str, valor: str, max_iter: int = 10,
                       historico: Historico = None) -> str:
    """Aplica regra de L'Hopital iterativamente ate resolver.

    Suporta ate max_iter iteracoes.
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'L\'Hopital estendida: ate {max_iter} iteracoes',
            regra='L\'Hopital estendida',
        ))

    num_atual = numerador
    den_atual = denominador

    for i in range(max_iter):
        # Verificar se ainda eh forma indeterminada
        quociente = op('/', num_atual, den_atual)
        try:
            if valor in ('inf', '+inf', '-inf'):
                # Para limites no infinito, avaliar numericamente
                ponto = 1e12 if valor in ('inf', '+inf') else -1e12
                r = quociente.avaliar({variavel: ponto})
                if math.isfinite(r):
                    resultado_str = str(round(r, 10))
                    if resultado_str.endswith('.0'):
                        resultado_str = resultado_str[:-2]
                    return resultado_str
            else:
                val = float(valor)
                r = quociente.avaliar({variavel: val})
                if math.isfinite(r):
                    inteiro = round(r)
                    if abs(r - inteiro) < 1e-8:
                        return str(inteiro)
                    return str(round(r, 10))
        except (ValueError, ZeroDivisionError, OverflowError):
            pass

        # Derivar
        d_num = simplificar_no(derivar(num_atual, variavel))
        d_den = simplificar_no(derivar(den_atual, variavel))

        if historico is not None:
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'L\'Hopital iteracao {i+1}',
                latex_antes=f'\\frac{{{num_atual.representacao_latex()}}}{{{den_atual.representacao_latex()}}}',
                latex_depois=f'\\frac{{{d_num.representacao_latex()}}}{{{d_den.representacao_latex()}}}',
                regra='L\'Hopital',
            ))

        num_atual = d_num
        den_atual = d_den

    return 'indefinido'


# ============================================================
# Teorema do valor medio
# ============================================================

def teorema_valor_medio(no: NoExpressao, variavel: str, a: float, b: float,
                        historico: Historico = None) -> list:
    """Encontra c em (a,b) tal que f'(c) = (f(b) - f(a)) / (b - a).

    Retorna lista de valores c encontrados.
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Teorema do valor medio em [{a}, {b}]',
            regra='TVM',
        ))

    fa = no.avaliar({variavel: a})
    fb = no.avaliar({variavel: b})
    taxa_media = (fb - fa) / (b - a)

    if historico is not None:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Taxa media: (f({b}) - f({a})) / ({b} - {a}) = ({fb} - {fa}) / {b - a} = {taxa_media}',
            regra='TVM - taxa media',
        ))

    df = simplificar_no(derivar(no, variavel))

    # f'(c) - taxa_media = 0 -> encontrar zeros de f'(x) - taxa_media
    equacao = op('-', df, num(str(taxa_media)))
    candidatos = _encontrar_zeros_numericos(equacao, variavel, a, b)

    # Filtrar: c deve estar estritamente em (a, b)
    resultados = [c for c in candidatos if a < c < b]

    if historico is not None:
        for c in resultados:
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'c = {c}: f\'({c}) = {taxa_media}',
                regra='TVM - resultado',
            ))

    return resultados


# ============================================================
# Esboco de curvas
# ============================================================

def esboco_curva(no: NoExpressao, variavel: str, intervalo: tuple = (-10, 10),
                 historico: Historico = None) -> dict:
    """Analisa uma funcao para esboco de curva.

    Retorna dicionario com:
    - zeros: raizes de f(x) = 0
    - criticos: pontos criticos (max/min)
    - inflexao: pontos de inflexao
    - assintotas_verticais: candidatas a assintotas verticais
    - crescimento: intervalos de crescimento/decrescimento
    - concavidade: intervalos de concavidade para cima/baixo
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao='Analise completa para esboco de curva',
            regra='Esboco de curva',
        ))

    a, b = intervalo

    # Zeros
    zeros = _encontrar_zeros_numericos(no, variavel, a, b)

    # Pontos criticos
    criticos = encontrar_criticos(no, variavel, intervalo, historico)

    # Inflexao
    inflexao = encontrar_inflexao(no, variavel, intervalo, historico)

    # Derivadas
    df = simplificar_no(derivar(no, variavel))

    # Crescimento/decrescimento
    pontos_teste = _gerar_pontos_teste(zeros + [c['x'] for c in criticos], a, b)
    crescimento = []
    for pt in pontos_teste:
        try:
            dfx = df.avaliar({variavel: pt})
            if dfx > 1e-8:
                crescimento.append((pt, 'crescente'))
            elif dfx < -1e-8:
                crescimento.append((pt, 'decrescente'))
            else:
                crescimento.append((pt, 'constante'))
        except (ValueError, ZeroDivisionError, OverflowError):
            pass

    # Concavidade
    d2f = simplificar_no(derivar(df, variavel))
    concavidade = []
    for pt in pontos_teste:
        try:
            d2fx = d2f.avaliar({variavel: pt})
            if d2fx > 1e-8:
                concavidade.append((pt, 'concava_cima'))
            elif d2fx < -1e-8:
                concavidade.append((pt, 'concava_baixo'))
            else:
                concavidade.append((pt, 'reta'))
        except (ValueError, ZeroDivisionError, OverflowError):
            pass

    # Assintotas verticais (onde f explode)
    assintotas_v = _detectar_assintotas_verticais(no, variavel, a, b)

    return {
        'zeros': zeros,
        'criticos': criticos,
        'inflexao': inflexao,
        'assintotas_verticais': assintotas_v,
        'crescimento': crescimento,
        'concavidade': concavidade,
    }


# ============================================================
# Problemas de otimizacao
# ============================================================

def otimizar(objetivo: NoExpressao, variavel: str, intervalo: tuple = None,
             tipo: str = 'minimo', historico: Historico = None) -> dict:
    """Encontra maximo ou minimo de f(x) no intervalo dado.

    tipo: 'minimo' ou 'maximo'
    Retorna dicionario com x_otimo, f_otimo.
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Otimizacao: encontrar {tipo}',
            regra='Otimizacao',
        ))

    criticos = encontrar_criticos(objetivo, variavel, intervalo, historico)

    # Filtrar pelo tipo desejado
    candidatos = []
    for c in criticos:
        if tipo == 'minimo' and c['tipo'] == 'minimo':
            candidatos.append(c)
        elif tipo == 'maximo' and c['tipo'] == 'maximo':
            candidatos.append(c)
        elif c['tipo'] == 'indefinido':
            candidatos.append(c)

    # Avaliar nos extremos do intervalo tambem
    if intervalo is not None:
        a, b = intervalo
        for ponto in [a, b]:
            try:
                fx = objetivo.avaliar({variavel: ponto})
                candidatos.append({'x': ponto, 'fx': fx, 'tipo': 'extremo'})
            except (ValueError, ZeroDivisionError, OverflowError):
                pass

    if not candidatos:
        return {'x_otimo': None, 'f_otimo': None}

    if tipo == 'minimo':
        melhor = min(candidatos, key=lambda c: c['fx'])
    else:
        melhor = max(candidatos, key=lambda c: c['fx'])

    if historico is not None:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'{tipo.capitalize()} em x = {melhor["x"]}: f(x) = {melhor["fx"]}',
            regra='Otimizacao - resultado',
        ))

    return {'x_otimo': melhor['x'], 'f_otimo': melhor['fx']}


# ============================================================
# Solidos de revolucao
# ============================================================

def volume_disco(no: NoExpressao, variavel: str, a: float, b: float,
                 historico: Historico = None) -> float:
    """Calcula volume de solido de revolucao pelo metodo dos discos.

    V = pi * ∫_a^b [f(x)]^2 dx

    Usa integracao numerica (Simpson).
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Volume por discos: V = pi * integral de [f(x)]^2 de {a} a {b}',
            regra='Discos',
        ))

    # f(x)^2
    f_quad = op('^', no, num('2'))

    integral_val = _integrar_numerico(f_quad, variavel, a, b)
    volume = math.pi * integral_val

    if historico is not None:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'V = pi * {integral_val} = {volume}',
            regra='Discos - resultado',
        ))

    return volume


def volume_casca(no: NoExpressao, variavel: str, a: float, b: float,
                 historico: Historico = None) -> float:
    """Calcula volume de solido de revolucao pelo metodo das cascas cilindricas.

    V = 2*pi * ∫_a^b x * f(x) dx

    Usa integracao numerica (Simpson).
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Volume por cascas: V = 2*pi * integral de x*f(x) de {a} a {b}',
            regra='Cascas cilindricas',
        ))

    # x * f(x)
    integrando = op('*', var(variavel), no)

    integral_val = _integrar_numerico(integrando, variavel, a, b)
    volume = 2 * math.pi * integral_val

    if historico is not None:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'V = 2*pi * {integral_val} = {volume}',
            regra='Cascas - resultado',
        ))

    return volume


# ============================================================
# Comprimento de arco
# ============================================================

def comprimento_arco(no: NoExpressao, variavel: str, a: float, b: float,
                     historico: Historico = None) -> float:
    """Calcula comprimento de arco: L = ∫_a^b sqrt(1 + [f'(x)]^2) dx.

    Usa integracao numerica (Simpson).
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Comprimento de arco: L = integral de sqrt(1 + [f\'(x)]^2) de {a} a {b}',
            regra='Comprimento de arco',
        ))

    df = simplificar_no(derivar(no, variavel))

    # sqrt(1 + (f')^2)
    integrando = op('^', op('+', num('1'), op('^', df, num('2'))), num('0.5'))

    comprimento = _integrar_numerico(integrando, variavel, a, b)

    if historico is not None:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'L = {comprimento}',
            regra='Comprimento de arco - resultado',
        ))

    return comprimento


# ============================================================
# Funcoes auxiliares
# ============================================================

def _encontrar_zeros_numericos(no: NoExpressao, variavel: str,
                               a: float, b: float, n_pontos: int = 1000) -> list:
    """Encontra zeros de f(x) no intervalo [a,b] por busca de mudanca de sinal + biseccao."""
    h = (b - a) / n_pontos
    zeros = []

    prev_val = None
    prev_x = None
    for i in range(n_pontos + 1):
        xi = a + i * h
        try:
            fi = no.avaliar({variavel: xi})
            if not math.isfinite(fi):
                prev_val = None
                prev_x = None
                continue
        except (ValueError, ZeroDivisionError, OverflowError):
            prev_val = None
            prev_x = None
            continue

        if abs(fi) < 1e-12:
            # Exatamente zero
            zeros.append(round(xi, 10))
            prev_val = fi
            prev_x = xi
            continue

        if prev_val is not None and prev_val * fi < 0:
            # Mudanca de sinal -> biseccao
            zero = _biseccao(no, variavel, prev_x, xi)
            if zero is not None:
                zeros.append(zero)

        prev_val = fi
        prev_x = xi

    # Remover duplicatas proximas
    zeros_unicos = []
    for z in sorted(zeros):
        if not zeros_unicos or abs(z - zeros_unicos[-1]) > 1e-6:
            zeros_unicos.append(z)

    return zeros_unicos


def _biseccao(no: NoExpressao, variavel: str, a: float, b: float,
              tol: float = 1e-12, max_iter: int = 100) -> float:
    """Biseccao para encontrar zero em [a,b]."""
    try:
        fa = no.avaliar({variavel: a})
        fb = no.avaliar({variavel: b})
    except (ValueError, ZeroDivisionError, OverflowError):
        return None

    if fa * fb > 0:
        return None

    for _ in range(max_iter):
        c = (a + b) / 2
        try:
            fc = no.avaliar({variavel: c})
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

        if abs(fc) < tol or (b - a) / 2 < tol:
            return round(c, 10)

        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

    return round((a + b) / 2, 10)


def _integrar_numerico(no: NoExpressao, variavel: str, a: float, b: float,
                       n: int = 10000) -> float:
    """Integracao numerica por regra de Simpson composta."""
    h = (b - a) / n
    soma = 0
    for i in range(n + 1):
        xi = a + i * h
        try:
            fi = no.avaliar({variavel: xi})
        except (ValueError, ZeroDivisionError, OverflowError):
            fi = 0

        if not math.isfinite(fi):
            fi = 0

        if i == 0 or i == n:
            soma += fi
        elif i % 2 == 1:
            soma += 4 * fi
        else:
            soma += 2 * fi

    return soma * h / 3


def _gerar_pontos_teste(pontos_especiais: list, a: float, b: float) -> list:
    """Gera pontos de teste entre pontos especiais."""
    todos = sorted(set([a] + pontos_especiais + [b]))
    pontos = []
    for i in range(len(todos) - 1):
        pontos.append((todos[i] + todos[i + 1]) / 2)
    return pontos


def _detectar_assintotas_verticais(no: NoExpressao, variavel: str,
                                    a: float, b: float) -> list:
    """Detecta candidatas a assintotas verticais por avaliacao numerica."""
    n = 1000
    h = (b - a) / n
    candidatos = []

    for i in range(n + 1):
        xi = a + i * h
        try:
            fi = no.avaliar({variavel: xi})
            if abs(fi) > 1e10:
                candidatos.append(round(xi, 6))
        except (ValueError, ZeroDivisionError, OverflowError):
            candidatos.append(round(xi, 6))

    # Agrupar candidatos proximos
    if not candidatos:
        return []

    agrupados = [candidatos[0]]
    for c in candidatos[1:]:
        if abs(c - agrupados[-1]) > 0.1:
            agrupados.append(c)

    return agrupados
