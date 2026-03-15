"""Integracao simbolica."""

import math
from .arvore import NoExpressao, num, var, op, func
from .derivada import simplificar_no, derivar
from engine.basic.passo import Passo, Historico


def _contem_variavel(no: NoExpressao, variavel: str) -> bool:
    """Verifica se a expressao contem a variavel."""
    if no.tipo == 'variavel':
        return no.valor == variavel
    if no.tipo == 'numero':
        return False
    for filho in no.filhos:
        if _contem_variavel(filho, variavel):
            return True
    return False


def integrar(no: NoExpressao, variavel: str = 'x', historico: Historico = None) -> NoExpressao:
    """Integra a expressao simbolica.

    Tentativas em ordem:
    1. Direta (tabela): x^n -> x^(n+1)/(n+1), 1/x -> ln|x|, e^x -> e^x
    2. Constante x funcao
    3. Soma/diferenca: integral(f+g) = integral(f) + integral(g)
    Adiciona + C ao final.
    """
    resultado = _integrar_interno(no, variavel, historico)
    # Adicionar + C
    c = var('C')
    return op('+', resultado, c)


def _integrar_interno(no: NoExpressao, variavel: str, historico: Historico = None) -> NoExpressao:
    """Integracao interna sem + C."""

    def _passo(descricao, latex_antes='', latex_depois='', regra=''):
        if historico is not None:
            historico.adicionar(Passo(
                nivel=2,
                descricao=descricao,
                latex_antes=latex_antes,
                latex_depois=latex_depois,
                regra=regra,
            ))

    latex_expr = no.representacao_latex()

    # Constante (nao contem variavel)
    if no.tipo == 'numero' or (no.tipo == 'variavel' and no.valor != variavel):
        _passo(
            f'Integral de constante: c*{variavel}',
            latex_antes=f'\\int {latex_expr} \\, d{variavel}',
            latex_depois=f'{latex_expr} \\cdot {variavel}',
            regra='Constante',
        )
        return op('*', no, var(variavel))

    # Variavel simples: integral(x dx) = x^2/2
    if no.tipo == 'variavel' and no.valor == variavel:
        _passo(
            f'Integral de {variavel}: {variavel}^2/2',
            latex_antes=f'\\int {variavel} \\, d{variavel}',
            latex_depois=f'\\frac{{{variavel}^2}}{{2}}',
            regra='Potencia (n=1)',
        )
        return op('/', op('^', var(variavel), num('2')), num('2'))

    # Operacoes
    if no.tipo == 'operacao':
        esq = no.filhos[0]
        dir_ = no.filhos[1]

        # Soma/diferenca
        if no.valor in ('+', '-'):
            _passo(
                'Integral da soma/diferenca: integrar cada parcela',
                latex_antes=f'\\int ({latex_expr}) \\, d{variavel}',
                regra='Soma/Diferenca',
            )
            i_esq = _integrar_interno(esq, variavel, historico)
            i_dir = _integrar_interno(dir_, variavel, historico)
            return simplificar_no(op(no.valor, i_esq, i_dir))

        # Constante * funcao
        if no.valor == '*':
            if not _contem_variavel(esq, variavel):
                _passo(
                    'Constante multiplicativa sai da integral',
                    latex_antes=f'\\int {latex_expr} \\, d{variavel}',
                    regra='Constante multiplicativa',
                )
                i_dir = _integrar_interno(dir_, variavel, historico)
                return simplificar_no(op('*', esq, i_dir))
            if not _contem_variavel(dir_, variavel):
                _passo(
                    'Constante multiplicativa sai da integral',
                    latex_antes=f'\\int {latex_expr} \\, d{variavel}',
                    regra='Constante multiplicativa',
                )
                i_esq = _integrar_interno(esq, variavel, historico)
                return simplificar_no(op('*', dir_, i_esq))

        # Potencia: x^n -> x^(n+1)/(n+1) para n != -1
        if no.valor == '^':
            if (esq.tipo == 'variavel' and esq.valor == variavel
                    and not _contem_variavel(dir_, variavel)):
                n = float(dir_.valor)
                if n == -1:
                    _passo(
                        f'Integral de {variavel}^(-1) = ln|{variavel}|',
                        latex_antes=f'\\int {latex_expr} \\, d{variavel}',
                        latex_depois=f'\\ln|{variavel}|',
                        regra='Logaritmo natural',
                    )
                    return func('ln', func('abs', var(variavel)))
                novo_exp = n + 1
                # Formatar sem .0 quando é inteiro
                novo_exp_str = str(int(novo_exp)) if novo_exp == int(novo_exp) else str(novo_exp)
                _passo(
                    f'Regra da potencia: {variavel}^{dir_.valor} -> {variavel}^{novo_exp_str}/{novo_exp_str}',
                    latex_antes=f'\\int {latex_expr} \\, d{variavel}',
                    regra='Potencia',
                )
                return simplificar_no(
                    op('/', op('^', var(variavel), num(novo_exp_str)), num(novo_exp_str))
                )

        # 1/x -> ln|x|
        if no.valor == '/':
            if (esq.tipo == 'numero' and esq.valor == '1'
                    and dir_.tipo == 'variavel' and dir_.valor == variavel):
                _passo(
                    f'Integral de 1/{variavel} = ln|{variavel}|',
                    latex_antes=f'\\int {latex_expr} \\, d{variavel}',
                    latex_depois=f'\\ln|{variavel}|',
                    regra='Logaritmo natural',
                )
                return func('ln', func('abs', var(variavel)))

    # Funcoes
    if no.tipo == 'funcao':
        arg = no.filhos[0]
        # Apenas para argumento simples = variavel
        if arg.tipo == 'variavel' and arg.valor == variavel:
            if no.valor == 'sin':
                _passo(
                    f'Integral de sin({variavel}) = -cos({variavel})',
                    latex_antes=f'\\int {latex_expr} \\, d{variavel}',
                    regra='sin -> -cos',
                )
                return op('*', num('-1'), func('cos', var(variavel)))

            if no.valor == 'cos':
                _passo(
                    f'Integral de cos({variavel}) = sin({variavel})',
                    latex_antes=f'\\int {latex_expr} \\, d{variavel}',
                    regra='cos -> sin',
                )
                return func('sin', var(variavel))

            if no.valor == 'exp':
                _passo(
                    f'Integral de e^{variavel} = e^{variavel}',
                    latex_antes=f'\\int {latex_expr} \\, d{variavel}',
                    regra='exp -> exp',
                )
                return func('exp', var(variavel))

    # Tentar integracao por substituicao
    resultado_sub = _tentar_substituicao(no, variavel, historico)
    if resultado_sub is not None:
        return resultado_sub

    # Tentar integracao por partes
    resultado_partes = _tentar_partes(no, variavel, historico)
    if resultado_partes is not None:
        return resultado_partes

    raise ValueError(f"Nao sei integrar: {no}")


# ============================================================
# Integracao por substituicao
# ============================================================

def _nos_iguais(a: NoExpressao, b: NoExpressao) -> bool:
    """Compara dois nos de expressao recursivamente."""
    if a.tipo != b.tipo or a.valor != b.valor:
        return False
    if len(a.filhos) != len(b.filhos):
        return False
    return all(_nos_iguais(af, bf) for af, bf in zip(a.filhos, b.filhos))


def _substituir_no(no: NoExpressao, alvo: NoExpressao, substituto: NoExpressao) -> NoExpressao:
    """Substitui todas as ocorrencias de 'alvo' por 'substituto' na arvore."""
    if _nos_iguais(no, alvo):
        return substituto
    if no.tipo in ('numero', 'variavel'):
        return no
    novos_filhos = [_substituir_no(f, alvo, substituto) for f in no.filhos]
    return NoExpressao(no.tipo, no.valor, novos_filhos)


def _tentar_substituicao(no: NoExpressao, variavel: str, historico: Historico = None) -> NoExpressao:
    """Tenta integracao por substituicao: ∫f(g(x))·g'(x)dx -> ∫f(u)du.

    Detecta padroes onde o integrando eh produto de f(g(x)) * g'(x).
    """
    if no.tipo != 'operacao' or no.valor != '*':
        return None

    esq = no.filhos[0]
    dir_ = no.filhos[1]

    # Tentar ambas as ordens: esq pode ser g'(x) e dir_ pode ser f(g(x)) ou vice-versa
    for fator_derivada, fator_funcao in [(esq, dir_), (dir_, esq)]:
        candidato = _extrair_funcao_interna(fator_funcao, variavel)
        if candidato is None:
            continue
        g_x = candidato  # a funcao interna g(x)

        # Calcular g'(x) e ver se bate com fator_derivada
        dg = simplificar_no(derivar(g_x, variavel))

        # Verificar se fator_derivada == g'(x) (ou multiplo constante)
        fator_const = _eh_multiplo_constante(fator_derivada, dg, variavel)
        if fator_const is not None:
            if historico is not None:
                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'Substituicao: u = {g_x.representacao_latex()}, du = {dg.representacao_latex()} d{variavel}',
                    regra='Substituicao',
                ))

            # Substituir g(x) por u na funcao externa
            u = var('u')
            integrando_u = _substituir_no(fator_funcao, g_x, u)

            # Integrar em u
            try:
                resultado_u = _integrar_interno(integrando_u, 'u', historico)
            except ValueError:
                continue

            # Substituir u de volta por g(x)
            resultado = _substituir_no(resultado_u, u, g_x)

            # Multiplicar pelo fator constante se houver
            if fator_const != 1.0:
                resultado = simplificar_no(op('*', num(str(fator_const)), resultado))

            return resultado

    return None


def _extrair_funcao_interna(no: NoExpressao, variavel: str) -> NoExpressao:
    """Extrai a funcao interna g(x) de uma composicao f(g(x))."""
    if no.tipo == 'funcao' and no.filhos:
        arg = no.filhos[0]
        if _contem_variavel(arg, variavel) and arg != var(variavel):
            return arg
    # Para potencias tipo (g(x))^n
    if (no.tipo == 'operacao' and no.valor == '^'
            and not _contem_variavel(no.filhos[1], variavel)
            and _contem_variavel(no.filhos[0], variavel)):
        base = no.filhos[0]
        if base.tipo != 'variavel':
            return base
    return None


def _eh_multiplo_constante(expr: NoExpressao, referencia: NoExpressao, variavel: str) -> float:
    """Verifica se expr eh multiplo constante de referencia.

    Retorna o fator constante ou None.
    """
    # Avaliacao numerica para comparar
    pontos_teste = [0.5, 1.0, 1.5, 2.0, 2.5]
    ratios = []
    for val in pontos_teste:
        try:
            v_expr = expr.avaliar({variavel: val})
            v_ref = referencia.avaliar({variavel: val})
            if abs(v_ref) < 1e-15:
                continue
            ratios.append(v_expr / v_ref)
        except (ValueError, ZeroDivisionError, OverflowError):
            continue

    if len(ratios) < 2:
        return None

    # Verificar se todos os ratios sao aproximadamente iguais
    media = ratios[0]
    for r in ratios[1:]:
        if abs(r - media) > 1e-8:
            return None

    return media


# ============================================================
# Integracao por partes
# ============================================================

# Heuristica LIATE: Logaritmica, Inversa trig, Algebrica, Trigonometrica, Exponencial
_LIATE_PRIORIDADE = {
    'ln': 0,
    'arcsin': 1, 'arccos': 1, 'arctan': 1,
    'sin': 3, 'cos': 3, 'tan': 3,
    'exp': 4,
}


def _prioridade_liate(no: NoExpressao) -> int:
    """Retorna prioridade LIATE do no (menor = melhor escolha para u)."""
    if no.tipo == 'funcao':
        return _LIATE_PRIORIDADE.get(no.valor, 2)
    if no.tipo == 'operacao' and no.valor == '^':
        return 2  # algebrica
    if no.tipo == 'variavel':
        return 2  # algebrica
    if no.tipo == 'numero':
        return 5  # constante
    return 2


def _tentar_partes(no: NoExpressao, variavel: str, historico: Historico = None,
                   profundidade: int = 0) -> NoExpressao:
    """Tenta integracao por partes: ∫u·dv = u·v - ∫v·du.

    Usa heuristica LIATE para escolher u.
    """
    if profundidade > 3:
        return None

    if no.tipo != 'operacao' or no.valor != '*':
        return None

    esq = no.filhos[0]
    dir_ = no.filhos[1]

    # Escolher u e dv pela prioridade LIATE (menor prioridade -> u)
    p_esq = _prioridade_liate(esq)
    p_dir = _prioridade_liate(dir_)

    if p_esq <= p_dir:
        u = esq
        dv_integrando = dir_
    else:
        u = dir_
        dv_integrando = esq

    if historico is not None:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Integracao por partes: u = {u.representacao_latex()}, dv = {dv_integrando.representacao_latex()} d{variavel}',
            regra='Por partes (LIATE)',
        ))

    # Calcular du = u' dx
    du = simplificar_no(derivar(u, variavel))

    # Calcular v = ∫dv
    try:
        v = _integrar_interno(dv_integrando, variavel, historico)
    except ValueError:
        return None

    # ∫u·dv = u·v - ∫v·du
    uv = simplificar_no(op('*', u, v))

    # ∫v·du
    integrando_vdu = simplificar_no(op('*', v, du))
    try:
        integral_vdu = _integrar_interno(integrando_vdu, variavel, historico)
    except ValueError:
        # Tentar por partes recursivamente
        integral_vdu = _tentar_partes(integrando_vdu, variavel, historico, profundidade + 1)
        if integral_vdu is None:
            return None

    resultado = simplificar_no(op('-', uv, integral_vdu))

    if historico is not None:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Resultado por partes: {resultado.representacao_latex()}',
            latex_depois=resultado.representacao_latex(),
            regra='Por partes - resultado',
        ))

    return resultado


# ============================================================
# Integrais improprias
# ============================================================

def integral_impropria(no: NoExpressao, variavel: str, a: str, b: str,
                       historico: Historico = None) -> str:
    """Calcula integral impropria ∫_a^b f(x)dx onde a ou b pode ser 'inf'/'-inf'.

    Usa aproximacao numerica com limites crescentes para detectar convergencia.
    Retorna string com resultado numerico, 'inf', '-inf' ou 'divergente'.
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Integral impropria de {a} a {b}',
            regra='Integral impropria',
        ))

    # Aproximacao numerica com somas de Riemann crescentes
    limites_teste = [10, 100, 1000, 10000]
    resultados = []

    for L in limites_teste:
        lim_inf = -L if a in ('inf', '-inf', '+inf') and a.startswith('-') else (float(a) if a not in ('inf', '-inf', '+inf') else None)
        lim_sup = L if b in ('inf', '+inf') else (float(b) if b not in ('-inf',) else -L)

        if a == '-inf':
            lim_inf = -L
        elif a == 'inf' or a == '+inf':
            return 'divergente'
        else:
            lim_inf = float(a)

        if b == 'inf' or b == '+inf':
            lim_sup = L
        elif b == '-inf':
            return 'divergente'
        else:
            lim_sup = float(b)

        # Simpson composto
        n = 1000
        h = (lim_sup - lim_inf) / n
        soma = 0
        try:
            for i in range(n + 1):
                xi = lim_inf + i * h
                fi = no.avaliar({variavel: xi})
                if not math.isfinite(fi):
                    break
                if i == 0 or i == n:
                    soma += fi
                elif i % 2 == 1:
                    soma += 4 * fi
                else:
                    soma += 2 * fi
            else:
                resultados.append(soma * h / 3)
                continue
        except (ValueError, ZeroDivisionError, OverflowError):
            pass
        resultados.append(None)

    # Verificar convergencia
    validos = [r for r in resultados if r is not None]
    if len(validos) < 2:
        return 'divergente'

    # Se os ultimos valores convergem
    if abs(validos[-1] - validos[-2]) < 1e-4:
        val = validos[-1]
        if abs(val) > 1e15:
            return 'inf' if val > 0 else '-inf'
        inteiro = round(val)
        if abs(val - inteiro) < 1e-6:
            return str(inteiro)
        return str(round(val, 6))

    return 'divergente'
