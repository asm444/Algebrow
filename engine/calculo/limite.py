"""Limites simbolicos."""

import math
from .arvore import NoExpressao, num, var, op, func
from .derivada import derivar, simplificar_no
from engine.basic.passo import Passo, Historico


def limite(no: NoExpressao, variavel: str, valor: str, historico: Historico = None) -> str:
    """Calcula o limite.

    1. Substituicao direta
    2. Se 0/0: tentar L'Hopital (derivar num e den)
    3. Se inf/inf: L'Hopital

    Retorna string com o resultado (numero ou 'inf'/'-inf'/'indefinido').
    """

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

    # Limites no infinito redirecionam
    if valor in ('inf', '+inf', '-inf'):
        return limite_infinito(no, variavel, valor if valor != 'inf' else '+inf', historico)

    # Tentar substituicao direta
    _passo(
        f'Tentar substituicao direta: {variavel} = {valor}',
        latex_antes=f'\\lim_{{{variavel} \\to {valor}}} {latex_expr}',
        regra='Substituicao direta',
    )

    try:
        val_num = float(valor)
        resultado = no.avaliar({variavel: val_num})
        if math.isfinite(resultado):
            resultado_str = _formatar_numero(resultado)
            _passo(
                f'Substituicao direta funcionou: resultado = {resultado_str}',
                latex_depois=resultado_str,
                regra='Substituicao direta',
            )
            return resultado_str
    except (ValueError, ZeroDivisionError, OverflowError):
        pass

    # Verificar forma indeterminada para quocientes
    if no.tipo == 'operacao' and no.valor == '/':
        numerador = no.filhos[0]
        denominador = no.filhos[1]

        try:
            val_num = float(valor)
            num_val = numerador.avaliar({variavel: val_num})
            den_val = denominador.avaliar({variavel: val_num})
        except (ValueError, ZeroDivisionError, OverflowError):
            num_val = None
            den_val = None

        # 0/0 -> L'Hopital
        forma_indeterminada = False
        if num_val is not None and den_val is not None:
            if abs(num_val) < 1e-12 and abs(den_val) < 1e-12:
                forma_indeterminada = True
            elif math.isinf(num_val) and math.isinf(den_val):
                forma_indeterminada = True

        if forma_indeterminada:
            _passo(
                'Forma indeterminada detectada, aplicar regra de L\'Hopital',
                regra='L\'Hopital',
            )
            return _lhopital(numerador, denominador, variavel, valor, historico, max_iter=5)

    # Tentar limite lateral (aproximacao numerica)
    _passo(
        'Tentando aproximacao numerica',
        regra='Aproximacao',
    )
    resultado = _limite_numerico(no, variavel, float(valor))
    return resultado


def _lhopital(numerador, denominador, variavel, valor, historico, max_iter=5):
    """Aplica regra de L'Hopital iterativamente."""

    def _passo(descricao, latex_antes='', latex_depois='', regra=''):
        if historico is not None:
            historico.adicionar(Passo(
                nivel=2,
                descricao=descricao,
                latex_antes=latex_antes,
                latex_depois=latex_depois,
                regra=regra,
            ))

    for i in range(max_iter):
        d_num = simplificar_no(derivar(numerador, variavel))
        d_den = simplificar_no(derivar(denominador, variavel))

        _passo(
            f'L\'Hopital iteracao {i+1}: derivar numerador e denominador',
            latex_antes=f'\\frac{{{numerador.representacao_latex()}}}{{{denominador.representacao_latex()}}}',
            latex_depois=f'\\frac{{{d_num.representacao_latex()}}}{{{d_den.representacao_latex()}}}',
            regra='L\'Hopital',
        )

        try:
            val_num = float(valor)
            num_val = d_num.avaliar({variavel: val_num})
            den_val = d_den.avaliar({variavel: val_num})

            if abs(den_val) > 1e-12 and math.isfinite(num_val):
                resultado = num_val / den_val
                resultado_str = _formatar_numero(resultado)
                _passo(
                    f'L\'Hopital resolveu: {resultado_str}',
                    latex_depois=resultado_str,
                    regra='L\'Hopital - resultado',
                )
                return resultado_str

            # Ainda indeterminado, continuar
            numerador = d_num
            denominador = d_den
        except (ValueError, ZeroDivisionError, OverflowError):
            numerador = d_num
            denominador = d_den

    return 'indefinido'


def _limite_numerico(no, variavel, valor, epsilon=1e-10):
    """Calcula limite por aproximacao numerica."""
    try:
        # Aproximar pela esquerda e pela direita
        esq = no.avaliar({variavel: valor - epsilon})
        dir_ = no.avaliar({variavel: valor + epsilon})

        if math.isfinite(esq) and math.isfinite(dir_):
            media = (esq + dir_) / 2
            if abs(esq - dir_) < 1e-6:
                return _formatar_numero(media)
        if math.isinf(esq) and math.isinf(dir_):
            if esq > 0 and dir_ > 0:
                return 'inf'
            if esq < 0 and dir_ < 0:
                return '-inf'
    except (ValueError, ZeroDivisionError, OverflowError):
        pass

    return 'indefinido'


def _formatar_numero(valor: float) -> str:
    """Formata numero removendo .0 se inteiro."""
    if valor == int(valor):
        return str(int(valor))
    # Arredondar para evitar erros de ponto flutuante
    arredondado = round(valor, 10)
    if arredondado == int(arredondado):
        return str(int(arredondado))
    return str(arredondado)


# ============================================================
# Limites laterais
# ============================================================

def limite_lateral(no: NoExpressao, variavel: str, valor: str, lado: str = 'esquerda',
                   historico: Historico = None) -> str:
    """Calcula limite lateral.

    lado: 'esquerda' (x -> a-) ou 'direita' (x -> a+)
    """
    def _passo(descricao, latex_antes='', latex_depois='', regra=''):
        if historico is not None:
            historico.adicionar(Passo(
                nivel=2,
                descricao=descricao,
                latex_antes=latex_antes,
                latex_depois=latex_depois,
                regra=regra,
            ))

    sinal = '-' if lado == 'esquerda' else '+'
    _passo(
        f'Limite lateral pela {lado}: {variavel} -> {valor}{sinal}',
        latex_antes=f'\\lim_{{{variavel} \\to {valor}^{sinal}}}',
        regra='Limite lateral',
    )

    val_num = float(valor)
    epsilons = [1e-3, 1e-5, 1e-7, 1e-9, 1e-11]
    resultados = []

    for eps in epsilons:
        ponto = val_num - eps if lado == 'esquerda' else val_num + eps
        try:
            r = no.avaliar({variavel: ponto})
            if math.isfinite(r):
                resultados.append(r)
            elif math.isinf(r):
                return 'inf' if r > 0 else '-inf'
        except (ValueError, ZeroDivisionError, OverflowError):
            pass

    if not resultados:
        return 'indefinido'

    # Verificar se diverge (valores crescem em modulo com epsilon menor)
    if len(resultados) >= 3:
        abs_vals = [abs(r) for r in resultados]
        # Se valores absolutos crescem monotonicamente e sao grandes
        if abs_vals[-1] > abs_vals[-2] > abs_vals[-3] and abs_vals[-1] > 1e6:
            if resultados[-1] > 0:
                return 'inf'
            else:
                return '-inf'

    # Verificar convergencia
    if len(resultados) >= 2 and abs(resultados[-1] - resultados[-2]) < 1e-4 * (1 + abs(resultados[-1])):
        resultado_str = _formatar_numero(resultados[-1])
        _passo(
            f'Limite lateral = {resultado_str}',
            latex_depois=resultado_str,
            regra='Limite lateral - resultado',
        )
        return resultado_str

    if resultados:
        return _formatar_numero(resultados[-1])

    return 'indefinido'


# ============================================================
# Limites no infinito
# ============================================================

def limite_infinito(no: NoExpressao, variavel: str, direcao: str = '+inf',
                    historico: Historico = None) -> str:
    """Calcula lim(x -> ±∞) f(x).

    direcao: '+inf' ou '-inf'
    """
    def _passo(descricao, latex_antes='', latex_depois='', regra=''):
        if historico is not None:
            historico.adicionar(Passo(
                nivel=2,
                descricao=descricao,
                latex_antes=latex_antes,
                latex_depois=latex_depois,
                regra=regra,
            ))

    sinal_latex = '+\\infty' if direcao == '+inf' else '-\\infty'
    _passo(
        f'Limite no infinito: {variavel} -> {direcao}',
        latex_antes=f'\\lim_{{{variavel} \\to {sinal_latex}}} {no.representacao_latex()}',
        regra='Limite no infinito',
    )

    # Avaliar para valores crescentes
    if direcao == '+inf':
        pontos = [10, 100, 1000, 10000, 100000]
    else:
        pontos = [-10, -100, -1000, -10000, -100000]

    resultados = []
    for p in pontos:
        try:
            r = no.avaliar({variavel: p})
            resultados.append(r)
        except (ValueError, ZeroDivisionError, OverflowError):
            resultados.append(None)

    validos = [(i, r) for i, r in enumerate(resultados) if r is not None and math.isfinite(r)]

    if not validos:
        # Todos infinitos ou erro
        infinitos = [r for r in resultados if r is not None and math.isinf(r)]
        if infinitos:
            if all(r > 0 for r in infinitos):
                _passo('Limite diverge para +infinito', latex_depois='+\\infty', regra='Divergencia')
                return 'inf'
            if all(r < 0 for r in infinitos):
                _passo('Limite diverge para -infinito', latex_depois='-\\infty', regra='Divergencia')
                return '-inf'
        # Checar overflow (valores nao finitos indicam divergencia)
        nao_finitos = [r for r in resultados if r is not None and not math.isfinite(r)]
        if nao_finitos:
            return 'inf'
        return 'indefinido'

    # Verificar se diverge (valores absolutos crescem com pontos maiores)
    if len(validos) >= 3:
        abs_vals = [abs(v[1]) for v in validos[-3:]]
        if abs_vals[0] < abs_vals[1] < abs_vals[2] and abs_vals[2] > 1e8:
            if validos[-1][1] > 0:
                _passo('Limite diverge para +infinito', latex_depois='+\\infty', regra='Divergencia')
                return 'inf'
            else:
                _passo('Limite diverge para -infinito', latex_depois='-\\infty', regra='Divergencia')
                return '-inf'

    # Verificar convergencia dos ultimos valores
    if len(validos) >= 2:
        ultimo = validos[-1][1]
        penultimo = validos[-2][1]

        # Convergencia absoluta (para valores que tendem a 0)
        if abs(ultimo - penultimo) < 1e-4:
            # Arredondar valores muito pequenos para 0
            if abs(ultimo) < 1e-3:
                resultado_str = '0'
            else:
                resultado_str = _formatar_numero(ultimo)
            _passo(
                f'Limite converge para {resultado_str}',
                latex_depois=resultado_str,
                regra='Limite no infinito - resultado',
            )
            return resultado_str

        # Convergencia relativa
        if abs(ultimo) > 1e-10 and abs(ultimo - penultimo) < 1e-4 * abs(ultimo):
            resultado_str = _formatar_numero(ultimo)
            _passo(
                f'Limite converge para {resultado_str}',
                latex_depois=resultado_str,
                regra='Limite no infinito - resultado',
            )
            return resultado_str

    if validos:
        val = validos[-1][1]
        if abs(val) < 1e-3:
            return '0'
        return _formatar_numero(val)

    return 'indefinido'


# ============================================================
# Formas indeterminadas estendidas
# ============================================================

def limite_forma_indeterminada(no: NoExpressao, variavel: str, valor: str,
                               historico: Historico = None) -> str:
    """Trata formas indeterminadas: 0*inf, inf-inf, 0^0, 1^inf, inf^0.

    Reduz cada forma a 0/0 ou inf/inf para aplicar L'Hopital.
    """
    def _passo(descricao, latex_antes='', latex_depois='', regra=''):
        if historico is not None:
            historico.adicionar(Passo(
                nivel=2,
                descricao=descricao,
                latex_antes=latex_antes,
                latex_depois=latex_depois,
                regra=regra,
            ))

    # Primeiro tentar o limite padrao
    resultado_direto = limite(no, variavel, valor, historico)
    if resultado_direto != 'indefinido':
        return resultado_direto

    # Analisar a forma da expressao
    # 0 * inf: reescrever como f/(1/g) -> 0/0
    if no.tipo == 'operacao' and no.valor == '*':
        f = no.filhos[0]
        g = no.filhos[1]
        # Tentar como f / (1/g) = quociente
        quociente = op('/', f, op('/', num('1'), g))
        resultado = limite(quociente, variavel, valor, historico)
        if resultado != 'indefinido':
            return resultado
        # Tentar ao contrario
        quociente2 = op('/', g, op('/', num('1'), f))
        resultado2 = limite(quociente2, variavel, valor, historico)
        if resultado2 != 'indefinido':
            return resultado2

    # f^g formas: 0^0, 1^inf, inf^0 -> e^(g*ln(f))
    if no.tipo == 'operacao' and no.valor == '^':
        base = no.filhos[0]
        exp_ = no.filhos[1]
        _passo(
            'Forma indeterminada de potencia: reescrever como e^(g*ln(f))',
            regra='Forma indeterminada - potencia',
        )
        # f^g = e^(g*ln(f))
        expoente = op('*', exp_, func('ln', base))
        resultado_exp = limite(expoente, variavel, valor, historico)
        if resultado_exp not in ('indefinido', 'inf', '-inf'):
            try:
                val = float(resultado_exp)
                resultado_final = math.exp(val)
                return _formatar_numero(resultado_final)
            except (ValueError, OverflowError):
                pass
        if resultado_exp == 'inf':
            return 'inf'
        if resultado_exp == '-inf':
            return '0'

    # inf - inf: reescrever com denominador comum (heuristica numerica)
    if no.tipo == 'operacao' and no.valor == '-':
        return _limite_numerico_bidirecional(no, variavel, valor)

    return 'indefinido'


def _limite_numerico_bidirecional(no, variavel, valor):
    """Calcula limite por aproximacao de ambos os lados."""
    try:
        val_num = float(valor)
    except ValueError:
        return 'indefinido'

    epsilons = [1e-3, 1e-5, 1e-7, 1e-9]
    esq_vals = []
    dir_vals = []

    for eps in epsilons:
        try:
            e = no.avaliar({variavel: val_num - eps})
            if math.isfinite(e):
                esq_vals.append(e)
        except (ValueError, ZeroDivisionError, OverflowError):
            pass
        try:
            d = no.avaliar({variavel: val_num + eps})
            if math.isfinite(d):
                dir_vals.append(d)
        except (ValueError, ZeroDivisionError, OverflowError):
            pass

    if esq_vals and dir_vals:
        media = (esq_vals[-1] + dir_vals[-1]) / 2
        if abs(esq_vals[-1] - dir_vals[-1]) < 1e-4:
            return _formatar_numero(media)

    return 'indefinido'
