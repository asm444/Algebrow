"""Derivacao simbolica via regras recursivas."""

from .arvore import NoExpressao, num, var, op, func
from engine.basic.passo import Passo, Historico


def _eh_numero(no: NoExpressao, valor: str = None) -> bool:
    if no.tipo != 'numero':
        return False
    if valor is not None:
        return no.valor == valor
    return True


def simplificar_no(no: NoExpressao) -> NoExpressao:
    """Simplifica uma arvore: 0+x->x, 1*x->x, 0*x->0, etc."""
    if no.tipo in ('numero', 'variavel'):
        return no

    if no.tipo == 'funcao':
        filhos_simpl = [simplificar_no(f) for f in no.filhos]
        return NoExpressao('funcao', no.valor, filhos_simpl)

    if no.tipo == 'operacao':
        esq = simplificar_no(no.filhos[0])
        dir_ = simplificar_no(no.filhos[1])

        if no.valor == '+':
            # 0 + x -> x
            if _eh_numero(esq, '0'):
                return dir_
            # x + 0 -> x
            if _eh_numero(dir_, '0'):
                return esq
            # ambos numeros -> calcular
            if _eh_numero(esq) and _eh_numero(dir_):
                return num(str(float(esq.valor) + float(dir_.valor)))

        if no.valor == '-':
            # x - 0 -> x
            if _eh_numero(dir_, '0'):
                return esq
            if _eh_numero(esq) and _eh_numero(dir_):
                return num(str(float(esq.valor) - float(dir_.valor)))

        if no.valor == '*':
            # 0 * x -> 0
            if _eh_numero(esq, '0'):
                return num('0')
            # x * 0 -> 0
            if _eh_numero(dir_, '0'):
                return num('0')
            # 1 * x -> x
            if _eh_numero(esq, '1'):
                return dir_
            # x * 1 -> x
            if _eh_numero(dir_, '1'):
                return esq
            # ambos numeros -> calcular
            if _eh_numero(esq) and _eh_numero(dir_):
                return num(str(float(esq.valor) * float(dir_.valor)))

        if no.valor == '/':
            # 0 / x -> 0
            if _eh_numero(esq, '0'):
                return num('0')
            # x / 1 -> x
            if _eh_numero(dir_, '1'):
                return esq

        if no.valor == '^':
            # x^0 -> 1
            if _eh_numero(dir_, '0'):
                return num('1')
            # x^1 -> x
            if _eh_numero(dir_, '1'):
                return esq
            # 0^n -> 0 (n > 0)
            if _eh_numero(esq, '0'):
                return num('0')

        return op(no.valor, esq, dir_)

    return no


def derivar(no: NoExpressao, variavel: str = 'x', historico: Historico = None) -> NoExpressao:
    """Deriva a expressao simbolica em relacao a variavel.

    Regras implementadas:
    - Constante: d/dx(c) = 0
    - Variavel: d/dx(x) = 1
    - Soma: d/dx(f+g) = f' + g'
    - Produto: d/dx(f*g) = f'g + fg'
    - Quociente: d/dx(f/g) = (f'g - fg')/g^2
    - Potencia: d/dx(x^n) = n*x^(n-1)
    - Cadeia: d/dx(f(g(x))) = f'(g(x))*g'(x)
    - sin->cos, cos->-sin, exp->exp, ln->1/x
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

    # Constante
    if no.tipo == 'numero':
        resultado = num('0')
        _passo(
            f'Derivada de constante {no.valor} eh 0',
            latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
            latex_depois='0',
            regra='Constante',
        )
        return resultado

    # Variavel
    if no.tipo == 'variavel':
        if no.valor == variavel:
            _passo(
                f'Derivada de {variavel} em relacao a {variavel} eh 1',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                latex_depois='1',
                regra='Variavel',
            )
            return num('1')
        else:
            _passo(
                f'Derivada de {no.valor} (constante em relacao a {variavel}) eh 0',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                latex_depois='0',
                regra='Constante',
            )
            return num('0')

    # Operacoes
    if no.tipo == 'operacao':
        esq = no.filhos[0]
        dir_ = no.filhos[1]

        if no.valor == '+':
            _passo(
                'Regra da soma: derivar cada parcela',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='Soma',
            )
            d_esq = derivar(esq, variavel, historico)
            d_dir = derivar(dir_, variavel, historico)
            return simplificar_no(op('+', d_esq, d_dir))

        if no.valor == '-':
            _passo(
                'Regra da diferenca: derivar cada parcela',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='Diferenca',
            )
            d_esq = derivar(esq, variavel, historico)
            d_dir = derivar(dir_, variavel, historico)
            return simplificar_no(op('-', d_esq, d_dir))

        if no.valor == '*':
            _passo(
                'Regra do produto: f\'g + fg\'',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='Produto',
            )
            d_esq = derivar(esq, variavel, historico)
            d_dir = derivar(dir_, variavel, historico)
            termo1 = op('*', d_esq, dir_)
            termo2 = op('*', esq, d_dir)
            return simplificar_no(op('+', termo1, termo2))

        if no.valor == '/':
            _passo(
                'Regra do quociente: (f\'g - fg\') / g^2',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='Quociente',
            )
            d_esq = derivar(esq, variavel, historico)
            d_dir = derivar(dir_, variavel, historico)
            numerador = op('-', op('*', d_esq, dir_), op('*', esq, d_dir))
            denominador = op('^', dir_, num('2'))
            return simplificar_no(op('/', numerador, denominador))

        if no.valor == '^':
            # Caso: f(x)^n onde n eh constante
            if dir_.tipo == 'numero':
                n = float(dir_.valor)
                _passo(
                    f'Regra da potencia: n*x^(n-1) com n={dir_.valor}',
                    latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                    regra='Potencia',
                )
                d_base = derivar(esq, variavel, historico)
                # n * base^(n-1) * d_base (regra da cadeia)
                novo_exp = num(str(n - 1))
                resultado = op('*', op('*', dir_, op('^', esq, novo_exp)), d_base)
                return simplificar_no(resultado)

            # Caso geral: f^g (nao implementado completamente)
            _passo(
                'Potencia com expoente variavel - caso geral',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='Potencia geral',
            )
            # d/dx(f^g) = f^g * (g' * ln(f) + g * f'/f)
            d_esq = derivar(esq, variavel, historico)
            d_dir = derivar(dir_, variavel, historico)
            ln_f = func('ln', esq)
            termo1 = op('*', d_dir, ln_f)
            termo2 = op('*', dir_, op('/', d_esq, esq))
            return simplificar_no(op('*', no, op('+', termo1, termo2)))

    # Funcoes
    if no.tipo == 'funcao':
        arg = no.filhos[0]
        d_arg = derivar(arg, variavel, historico)

        if no.valor == 'sin':
            _passo(
                'Derivada de sin -> cos, com regra da cadeia',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='sin -> cos',
            )
            return simplificar_no(op('*', func('cos', arg), d_arg))

        if no.valor == 'cos':
            _passo(
                'Derivada de cos -> -sin, com regra da cadeia',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='cos -> -sin',
            )
            return simplificar_no(op('*', op('*', num('-1'), func('sin', arg)), d_arg))

        if no.valor == 'exp':
            _passo(
                'Derivada de e^x -> e^x, com regra da cadeia',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='exp -> exp',
            )
            return simplificar_no(op('*', no, d_arg))

        if no.valor == 'ln':
            _passo(
                'Derivada de ln(x) -> 1/x, com regra da cadeia',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='ln -> 1/x',
            )
            return simplificar_no(op('*', op('/', num('1'), arg), d_arg))

        if no.valor == 'tan':
            _passo(
                'Derivada de tan(x) -> 1/cos^2(x), com regra da cadeia',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='tan -> sec^2',
            )
            cos2 = op('^', func('cos', arg), num('2'))
            return simplificar_no(op('*', op('/', num('1'), cos2), d_arg))

    raise ValueError(f"Nao sei derivar: {no}")
