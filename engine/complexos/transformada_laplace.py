"""Transformada de Laplace: tabela de pares, transformada direta e inversa,
resolucao de EDOs via Laplace.
"""

import re
from engine.basic.passo import Passo, Historico
from engine.basic import operacoes_basicas as ops


# ======================================================================
# Tabela de transformadas conhecidas
# ======================================================================

TABELA_LAPLACE = {
    '1':              '1/s',
    't':              '1/s^2',
    't^n':            'n!/s^(n+1)',
    'e^(at)':         '1/(s-a)',
    'sin(wt)':        'w/(s^2+w^2)',
    'cos(wt)':        's/(s^2+w^2)',
    'e^(at)sin(wt)':  'w/((s-a)^2+w^2)',
    'e^(at)cos(wt)':  '(s-a)/((s-a)^2+w^2)',
}

# Tabela inversa construida a partir da tabela direta
_TABELA_INVERSA = {v: k for k, v in TABELA_LAPLACE.items()}


# ======================================================================
# Transformada direta
# ======================================================================

def transformada_laplace(f: str) -> tuple:
    """Calcula L{f(t)} usando tabela + propriedades.

    Suporta:
    - Entradas exatas da tabela: '1', 't', 'e^(at)', 'sin(wt)', 'cos(wt)', etc.
    - Constante multiplicativa: 'c*f(t)' -> c * L{f(t)}
    - Soma de termos: 'f(t) + g(t)' -> L{f(t)} + L{g(t)}
    - Potencias de t: 't^n' com n inteiro

    Retorna (resultado: str LaTeX, Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular transformada de Laplace de f(t) = {f}',
        latex_antes=f'\\mathcal{{L}}\\{{{f}\\}}',
        regra='Transformada de Laplace',
    ))

    resultado = _transformar(f.strip(), historico)

    historico.adicionar(Passo(
        nivel=1,
        descricao='Resultado da transformada de Laplace',
        latex_depois=resultado,
        regra='Transformada de Laplace',
    ))

    return (resultado, historico)


def _transformar(f: str, historico: Historico) -> str:
    """Logica interna de transformacao."""
    f = f.strip()

    # Soma de termos: separar por '+' no nivel mais externo
    termos = _separar_soma(f)
    if len(termos) > 1:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Linearidade: separar em {len(termos)} termos',
            regra='Linearidade da Transformada',
        ))
        resultados = []
        for termo in termos:
            resultados.append(_transformar(termo.strip(), historico))
        return ' + '.join(resultados)

    # Coeficiente multiplicativo: c*f(t)
    coef, nucleo = _extrair_coeficiente(f)

    # Busca direta na tabela
    if nucleo in TABELA_LAPLACE:
        resultado = TABELA_LAPLACE[nucleo]
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Tabela: L{{{nucleo}}} = {resultado}',
            regra='Tabela de Laplace',
        ))
        if coef != '1':
            resultado = f'{coef}*({resultado})'
        return resultado

    # t^n com n especifico
    match_tn = re.match(r'^t\^(\d+)$', nucleo)
    if match_tn:
        n = int(match_tn.group(1))
        fatorial = ops.fatorial(n)
        resultado = f'{fatorial}/s^{n+1}'
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Tabela: L{{t^{n}}} = {n}!/s^({n}+1) = {resultado}',
            regra='Tabela de Laplace (t^n)',
        ))
        if coef != '1':
            resultado = f'{coef}*({resultado})'
        return resultado

    # e^(at) com a especifico
    match_exp = re.match(r'^e\^\((-?\d+(?:\.\d+)?)t\)$', nucleo)
    if match_exp:
        a = match_exp.group(1)
        resultado = f'1/(s-{a})' if not a.startswith('-') else f'1/(s+{a[1:]})'
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Tabela: L{{e^({a}t)}} = {resultado}',
            regra='Tabela de Laplace (exponencial)',
        ))
        if coef != '1':
            resultado = f'{coef}*({resultado})'
        return resultado

    # sin(wt) com w especifico
    match_sin = re.match(r'^sin\((-?\d+(?:\.\d+)?)t\)$', nucleo)
    if match_sin:
        w = match_sin.group(1)
        w2 = ops.multi(w, w)
        resultado = f'{w}/(s^2+{w2})'
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Tabela: L{{sin({w}t)}} = {resultado}',
            regra='Tabela de Laplace (seno)',
        ))
        if coef != '1':
            resultado = f'{coef}*({resultado})'
        return resultado

    # cos(wt) com w especifico
    match_cos = re.match(r'^cos\((-?\d+(?:\.\d+)?)t\)$', nucleo)
    if match_cos:
        w = match_cos.group(1)
        w2 = ops.multi(w, w)
        resultado = f's/(s^2+{w2})'
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Tabela: L{{cos({w}t)}} = {resultado}',
            regra='Tabela de Laplace (cosseno)',
        ))
        if coef != '1':
            resultado = f'{coef}*({resultado})'
        return resultado

    # e^(at)sin(wt)
    match_exp_sin = re.match(r'^e\^\((-?\d+(?:\.\d+)?)t\)sin\((-?\d+(?:\.\d+)?)t\)$', nucleo)
    if match_exp_sin:
        a = match_exp_sin.group(1)
        w = match_exp_sin.group(2)
        w2 = ops.multi(w, w)
        resultado = f'{w}/((s-{a})^2+{w2})'
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Tabela: L{{e^({a}t)sin({w}t)}} = {resultado}',
            regra='Tabela de Laplace (deslocamento em s)',
        ))
        if coef != '1':
            resultado = f'{coef}*({resultado})'
        return resultado

    # e^(at)cos(wt)
    match_exp_cos = re.match(r'^e\^\((-?\d+(?:\.\d+)?)t\)cos\((-?\d+(?:\.\d+)?)t\)$', nucleo)
    if match_exp_cos:
        a = match_exp_cos.group(1)
        w = match_exp_cos.group(2)
        w2 = ops.multi(w, w)
        resultado = f'(s-{a})/((s-{a})^2+{w2})'
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Tabela: L{{e^({a}t)cos({w}t)}} = {resultado}',
            regra='Tabela de Laplace (deslocamento em s)',
        ))
        if coef != '1':
            resultado = f'{coef}*({resultado})'
        return resultado

    raise ValueError(f'Transformada nao reconhecida para: {f}')


# ======================================================================
# Transformada inversa
# ======================================================================

def transformada_inversa(F: str) -> tuple:
    """Calcula L^{-1}{F(s)} usando tabela.

    Retorna (resultado: str LaTeX, Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular transformada inversa de F(s) = {F}',
        latex_antes=f'\\mathcal{{L}}^{{-1}}\\{{{F}\\}}',
        regra='Transformada inversa de Laplace',
    ))

    resultado = _transformar_inversa(F.strip(), historico)

    historico.adicionar(Passo(
        nivel=1,
        descricao='Resultado da transformada inversa',
        latex_depois=resultado,
        regra='Transformada inversa de Laplace',
    ))

    return (resultado, historico)


def _transformar_inversa(F: str, historico: Historico) -> str:
    """Logica interna de transformacao inversa."""
    F = F.strip()

    # Soma de termos
    termos = _separar_soma(F)
    if len(termos) > 1:
        resultados = []
        for termo in termos:
            resultados.append(_transformar_inversa(termo.strip(), historico))
        return ' + '.join(resultados)

    # Coeficiente
    coef, nucleo = _extrair_coeficiente(F)

    # Busca direta na tabela inversa
    if nucleo in _TABELA_INVERSA:
        resultado = _TABELA_INVERSA[nucleo]
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Tabela inversa: L^{{-1}}{{{nucleo}}} = {resultado}',
            regra='Tabela inversa de Laplace',
        ))
        if coef != '1':
            resultado = f'{coef}*({resultado})'
        return resultado

    # 1/s -> 1
    if nucleo == '1/s':
        resultado = '1'
        historico.adicionar(Passo(nivel=2, descricao='Tabela: L^{-1}{1/s} = 1',
                                  regra='Tabela inversa'))
        if coef != '1':
            resultado = coef
        return resultado

    # 1/s^2 -> t
    if nucleo == '1/s^2':
        resultado = 't'
        historico.adicionar(Passo(nivel=2, descricao='Tabela: L^{-1}{1/s^2} = t',
                                  regra='Tabela inversa'))
        if coef != '1':
            resultado = f'{coef}*t'
        return resultado

    # n!/s^(n+1) -> t^n
    match_tn = re.match(r'^(\d+)/s\^(\d+)$', nucleo)
    if match_tn:
        fatorial_val = int(match_tn.group(1))
        potencia = int(match_tn.group(2))
        n = potencia - 1
        if n >= 0 and ops.fatorial(n) == fatorial_val:
            resultado = f't^{n}' if n > 1 else 't'
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Tabela inversa: L^{{-1}}{{{fatorial_val}/s^{potencia}}} = t^{n}',
                regra='Tabela inversa (t^n)',
            ))
            if coef != '1':
                resultado = f'{coef}*({resultado})'
            return resultado

    # 1/(s-a) -> e^(at)
    match_exp = re.match(r'^1/\(s([+-]\d+(?:\.\d+)?)\)$', nucleo)
    if match_exp:
        deslocamento = match_exp.group(1)
        # s-a => a eh o oposto do deslocamento
        if deslocamento.startswith('-'):
            a = deslocamento[1:]
        elif deslocamento.startswith('+'):
            a = '-' + deslocamento[1:]
        else:
            a = '-' + deslocamento
        resultado = f'e^({a}t)'
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Tabela inversa: L^{{-1}}{{{nucleo}}} = e^({a}t)',
            regra='Tabela inversa (exponencial)',
        ))
        if coef != '1':
            resultado = f'{coef}*({resultado})'
        return resultado

    # w/(s^2+w^2) -> sin(wt)
    match_sin = re.match(r'^(\d+(?:\.\d+)?)/\(s\^2\+(\d+(?:\.\d+)?)\)$', nucleo)
    if match_sin:
        w_num = match_sin.group(1)
        w2_val = match_sin.group(2)
        # Verificar que w^2 = w2_val
        if ops.multi(w_num, w_num) == w2_val:
            resultado = f'sin({w_num}t)'
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Tabela inversa: L^{{-1}}{{{nucleo}}} = sin({w_num}t)',
                regra='Tabela inversa (seno)',
            ))
            if coef != '1':
                resultado = f'{coef}*({resultado})'
            return resultado

    # s/(s^2+w^2) -> cos(wt)
    match_cos = re.match(r'^s/\(s\^2\+(\d+(?:\.\d+)?)\)$', nucleo)
    if match_cos:
        w2_val = match_cos.group(1)
        # w = sqrt(w2)
        w2_float = float(w2_val)
        w_float = w2_float ** 0.5
        if abs(w_float - round(w_float)) < 1e-10:
            w = str(int(round(w_float)))
            resultado = f'cos({w}t)'
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Tabela inversa: L^{{-1}}{{{nucleo}}} = cos({w}t)',
                regra='Tabela inversa (cosseno)',
            ))
            if coef != '1':
                resultado = f'{coef}*({resultado})'
            return resultado

    raise ValueError(f'Transformada inversa nao reconhecida para: {F}')


# ======================================================================
# Resolver EDO via Laplace
# ======================================================================

def resolver_edo_laplace(edo: str, condicoes_iniciais: dict) -> tuple:
    """Resolve EDO via Laplace (estrutura basica).

    Passos:
    1. Aplicar L em ambos os lados
    2. Usar condicoes iniciais
    3. Isolar Y(s)
    4. Decompor em fracoes parciais
    5. Aplicar L^{-1}

    NOTA: Implementacao inicial com padroes reconhecidos.
    Retorna (solucao: str LaTeX, Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Resolver EDO via Laplace: {edo}',
        latex_antes=edo,
        regra='Metodo de Laplace para EDOs',
    ))

    # EDO de primeira ordem: y' + ay = f(t), y(0) = y0
    match_1 = re.match(r"y'\s*([+-]\s*\d*\.?\d*)\s*\*?\s*y\s*=\s*(.+)", edo)
    if match_1:
        a_str = match_1.group(1).replace(' ', '')
        a = float(a_str)
        rhs = match_1.group(2).strip()
        y0 = float(condicoes_iniciais.get('y(0)', condicoes_iniciais.get('y0', 0)))

        historico.adicionar(Passo(
            nivel=2,
            descricao=f'EDO de 1a ordem: y\' + {a}y = {rhs}, y(0) = {y0}',
            regra='Identificacao da EDO',
        ))

        # L{y'} = sY(s) - y(0)
        # (s + a)Y(s) = y(0) + L{rhs}
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Aplicar Laplace: (s + {a})Y(s) = {y0} + L{{{rhs}}}',
            regra='Transformada de Laplace da EDO',
        ))

        # Resolver para rhs = 0 (homogenea)
        if rhs.strip() == '0':
            # Y(s) = y0/(s+a)
            solucao = f'{y0}*e^({-a}t)' if a != 0 else f'{y0}'
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Y(s) = {y0}/(s+{a}), aplicando L^{{-1}}',
                latex_depois=f'y(t) = {solucao}',
                regra='Transformada inversa',
            ))
            return (solucao, historico)

    # EDO generica nao reconhecida
    historico.adicionar(Passo(
        nivel=1,
        descricao='Padrao de EDO nao reconhecido para resolucao automatica',
        regra='Limitacao',
    ))

    return ('EDO nao suportada automaticamente', historico)


# ======================================================================
# Utilitarios
# ======================================================================

def _separar_soma(expr: str) -> list:
    """Separa uma expressao por '+' no nivel mais externo (fora de parenteses)."""
    termos = []
    nivel = 0
    atual = ''
    for ch in expr:
        if ch == '(':
            nivel += 1
        elif ch == ')':
            nivel -= 1
        elif ch == '+' and nivel == 0 and atual.strip():
            termos.append(atual)
            atual = ''
            continue
        atual += ch
    if atual.strip():
        termos.append(atual)
    return termos


def _extrair_coeficiente(f: str) -> tuple:
    """Extrai coeficiente multiplicativo: '3*sin(2t)' -> ('3', 'sin(2t)')."""
    f = f.strip()
    # Padrao: numero*resto
    match = re.match(r'^(-?\d+(?:\.\d+)?)\*(.+)$', f)
    if match:
        return (match.group(1), match.group(2).strip())
    return ('1', f)
