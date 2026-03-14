"""Integracao simbolica."""

from .arvore import NoExpressao, num, var, op, func
from .derivada import simplificar_no
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
                _passo(
                    f'Regra da potencia: {variavel}^{dir_.valor} -> {variavel}^{novo_exp}/{novo_exp}',
                    latex_antes=f'\\int {latex_expr} \\, d{variavel}',
                    regra='Potencia',
                )
                return simplificar_no(
                    op('/', op('^', var(variavel), num(str(novo_exp))), num(str(novo_exp)))
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

    raise ValueError(f"Nao sei integrar: {no}")
