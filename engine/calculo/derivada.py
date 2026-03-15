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
    """Simplifica uma arvore: 0+x->x, 1*x->x, 0*x->0, cancelamento de termos, etc."""
    if no.tipo in ('numero', 'variavel'):
        return no

    if no.tipo == 'funcao':
        filhos_simpl = [simplificar_no(f) for f in no.filhos]
        return NoExpressao('funcao', no.valor, filhos_simpl)

    if no.tipo == 'operacao':
        esq = simplificar_no(no.filhos[0])
        dir_ = simplificar_no(no.filhos[1])

        if no.valor == '+':
            if _eh_numero(esq, '0'):
                return dir_
            if _eh_numero(dir_, '0'):
                return esq
            if _eh_numero(esq) and _eh_numero(dir_):
                return num(str(float(esq.valor) + float(dir_.valor)))

        if no.valor == '-':
            if _eh_numero(dir_, '0'):
                return esq
            if _eh_numero(esq) and _eh_numero(dir_):
                return num(str(float(esq.valor) - float(dir_.valor)))
            # a - a -> 0 (comparacao estrutural)
            if esq == dir_:
                return num('0')

        if no.valor == '*':
            if _eh_numero(esq, '0'):
                return num('0')
            if _eh_numero(dir_, '0'):
                return num('0')
            if _eh_numero(esq, '1'):
                return dir_
            if _eh_numero(dir_, '1'):
                return esq
            if _eh_numero(esq) and _eh_numero(dir_):
                return num(str(float(esq.valor) * float(dir_.valor)))

        if no.valor == '/':
            if _eh_numero(esq, '0'):
                return num('0')
            if _eh_numero(dir_, '1'):
                return esq

        if no.valor == '^':
            if _eh_numero(dir_, '0'):
                return num('1')
            if _eh_numero(dir_, '1'):
                return esq
            if _eh_numero(esq, '0'):
                return num('0')

        return op(no.valor, esq, dir_)

    return no


def simplificar_com_cancelamento(no: NoExpressao) -> NoExpressao:
    """Simplificacao avancada: coleta termos, cancela iguais, reconstroi.

    Resolve casos como x^3/3 + xy + C - x^3/3 -> xy + C.
    """
    termos = _coletar_termos_soma(no)
    termos = _cancelar_termos(termos)

    if not termos:
        return num('0')

    # Reconstruir a arvore
    resultado = termos[0]
    for t in termos[1:]:
        resultado = op('+', resultado, t)

    return simplificar_no(resultado)


def _coletar_termos_soma(no: NoExpressao) -> list:
    """Flatten a+b-c em [a, b, -1*c]."""
    if no.tipo == 'operacao' and no.valor == '+':
        return _coletar_termos_soma(no.filhos[0]) + _coletar_termos_soma(no.filhos[1])
    if no.tipo == 'operacao' and no.valor == '-':
        termos_dir = _coletar_termos_soma(no.filhos[1])
        termos_dir_neg = [_negar_termo(t) for t in termos_dir]
        return _coletar_termos_soma(no.filhos[0]) + termos_dir_neg
    return [no]


def _negar_termo(no: NoExpressao) -> NoExpressao:
    """Retorna -1 * no."""
    if _eh_numero(no):
        val = float(no.valor)
        return num(str(-val))
    if (no.tipo == 'operacao' and no.valor == '*'
            and _eh_numero(no.filhos[0])):
        novo_coef = str(-float(no.filhos[0].valor))
        return op('*', num(novo_coef), no.filhos[1])
    return op('*', num('-1'), no)


def _assinatura_numerica(no: NoExpressao) -> tuple:
    """Avalia o no em varios pontos para gerar uma assinatura numerica."""
    import math
    pontos = [
        {'x': 1.1, 'y': 0.7, 'z': 0.3, 'a': 0.5, 'b': 0.9, 'C': 0, 't': 0.4},
        {'x': 2.3, 'y': 1.1, 'z': 0.8, 'a': 1.2, 'b': 0.4, 'C': 0, 't': 0.7},
        {'x': 0.5, 'y': 2.1, 'z': 1.5, 'a': 0.3, 'b': 1.7, 'C': 0, 't': 1.1},
    ]
    valores = []
    for p in pontos:
        try:
            v = no.avaliar(p)
            if math.isfinite(v):
                valores.append(round(v, 8))
            else:
                return None
        except (ValueError, ZeroDivisionError, OverflowError):
            return None
    return tuple(valores)


def _cancelar_termos(termos: list) -> list:
    """Cancela termos que somam zero (assinatura numerica oposta)."""
    if len(termos) <= 1:
        return termos

    # Computar assinaturas
    assinaturas = []
    for t in termos:
        sig = _assinatura_numerica(t)
        assinaturas.append(sig)

    # Encontrar pares que se cancelam (sig_a + sig_b ≈ 0)
    usados = set()
    for i in range(len(termos)):
        if i in usados or assinaturas[i] is None:
            continue
        for j in range(i + 1, len(termos)):
            if j in usados or assinaturas[j] is None:
                continue
            # Verificar se a soma das assinaturas eh ~0
            soma = tuple(a + b for a, b in zip(assinaturas[i], assinaturas[j]))
            if all(abs(s) < 1e-6 for s in soma):
                usados.add(i)
                usados.add(j)
                break

    return [t for idx, t in enumerate(termos) if idx not in usados]


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
                n_menos_1 = n - 1
                n_menos_1_str = str(int(n_menos_1)) if n_menos_1 == int(n_menos_1) else str(n_menos_1)
                novo_exp = num(n_menos_1_str)
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

        if no.valor == 'arcsin':
            _passo(
                'Derivada de arcsin(x) -> 1/sqrt(1-x^2), com regra da cadeia',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='arcsin -> 1/sqrt(1-x^2)',
            )
            # 1 / sqrt(1 - arg^2) * d_arg
            interior = op('-', num('1'), op('^', arg, num('2')))
            raiz = op('^', interior, num('0.5'))
            return simplificar_no(op('*', op('/', num('1'), raiz), d_arg))

        if no.valor == 'arccos':
            _passo(
                'Derivada de arccos(x) -> -1/sqrt(1-x^2), com regra da cadeia',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='arccos -> -1/sqrt(1-x^2)',
            )
            interior = op('-', num('1'), op('^', arg, num('2')))
            raiz = op('^', interior, num('0.5'))
            return simplificar_no(op('*', op('/', num('-1'), raiz), d_arg))

        if no.valor == 'arctan':
            _passo(
                'Derivada de arctan(x) -> 1/(1+x^2), com regra da cadeia',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='arctan -> 1/(1+x^2)',
            )
            denominador = op('+', num('1'), op('^', arg, num('2')))
            return simplificar_no(op('*', op('/', num('1'), denominador), d_arg))

        if no.valor == 'sqrt':
            _passo(
                'Derivada de sqrt(x) -> 1/(2*sqrt(x)), com regra da cadeia',
                latex_antes=f'\\frac{{d}}{{d{variavel}}}({latex_expr})',
                regra='sqrt -> 1/(2*sqrt)',
            )
            return simplificar_no(
                op('*', op('/', num('1'), op('*', num('2'), op('^', arg, num('0.5')))), d_arg)
            )

    raise ValueError(f"Nao sei derivar: {no}")


def derivar_ordem(no: NoExpressao, variavel: str = 'x', ordem: int = 1,
                  historico: Historico = None) -> NoExpressao:
    """Calcula a derivada de ordem n: d^n f / dx^n."""
    resultado = no
    for i in range(ordem):
        if historico is not None:
            historico.adicionar(Passo(
                nivel=1,
                descricao=f'Calculando derivada de ordem {i+1}',
                regra=f'Derivada ordem {i+1}',
            ))
        resultado = simplificar_no(derivar(resultado, variavel, historico))
    return resultado


def derivada_implicita(expressao_F: NoExpressao, var_x: str = 'x', var_y: str = 'y',
                       historico: Historico = None) -> NoExpressao:
    """Calcula dy/dx dado F(x,y) = 0 usando derivada implicita.

    dy/dx = -Fx / Fy
    onde Fx = dF/dx e Fy = dF/dy.
    """
    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Derivada implicita: dy/dx = -F_{var_x} / F_{var_y}',
            regra='Derivada implicita',
        ))

    Fx = simplificar_no(derivar(expressao_F, var_x, historico))
    Fy = simplificar_no(derivar(expressao_F, var_y, historico))

    # dy/dx = -Fx / Fy
    resultado = simplificar_no(op('/', op('*', num('-1'), Fx), Fy))

    if historico is not None:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'dy/dx = {resultado.representacao_latex()}',
            latex_depois=resultado.representacao_latex(),
            regra='Derivada implicita - resultado',
        ))

    return resultado
