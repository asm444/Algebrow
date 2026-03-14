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
