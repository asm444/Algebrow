"""Ferramenta: Integrais.

Interface textual para o motor de integração simbólica.
Aceita expressão como texto, parseia, e retorna resultado com passos.

Exemplos de uso:
    >>> resultado = calcular_integral("x^2", "x")
    >>> print(resultado['latex'])       # \\frac{{x}^{3}}{3} + C

    >>> resultado = calcular_integral_definida("x^2", "x", "0", "1")
    >>> print(resultado['latex'])       # \\frac{1}{3}
    >>> print(resultado['valor'])       # 0.333333...

    >>> resultado = calcular_integral("sin(x)", "x")
    >>> print(resultado['latex'])       # -1 \\cdot \\cos\\left(x\\right) + C

    >>> resultado = calcular_integral("2*x*cos(x^2)", "x")
    >>> print(resultado['latex'])       # substituição: sin(x²) + C
"""

from engine.parser_simbolico import parsear_simbolico
from engine.calculo.integral import integrar, integral_impropria
from engine.calculo.derivada import simplificar_no
from engine.basic.passo import Passo, Historico


def calcular_integral(expressao: str, variavel: str = 'x',
                      verbosidade: int = 3) -> dict:
    """Calcula integral indefinida ∫ f(x) dx.

    Args:
        expressao: texto da expressão (ex: "x^2 + sin(x)")
        variavel: variável de integração (default: "x")
        verbosidade: nível de detalhe dos passos (0-4)

    Returns:
        dict com 'resultado' (NoExpressao), 'latex', 'latex_entrada',
        'passos', 'historico'
    """
    historico = Historico(verbosidade=verbosidade)
    no = parsear_simbolico(expressao)

    latex_entrada = f'\\int {no.representacao_latex()} \\, d{variavel}'

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular ∫ {no.representacao_latex()} d{variavel}',
        latex_antes=latex_entrada,
        regra='integral_indefinida',
        justificativa='Encontrar a primitiva (antiderivada) da expressão',
    ))

    resultado = integrar(no, variavel, historico)
    resultado = simplificar_no(resultado)
    latex_resultado = resultado.representacao_latex()

    historico.adicionar(Passo(
        nivel=0,
        descricao='Resultado da integral',
        latex_antes=latex_entrada,
        latex_depois=latex_resultado,
        regra='resultado',
    ))

    return {
        'resultado': resultado,
        'latex': latex_resultado,
        'latex_entrada': latex_entrada,
        'passos': historico.serializar(),
        'historico': historico,
    }


def calcular_integral_definida(expressao: str, variavel: str = 'x',
                               limite_inferior: str = '0', limite_superior: str = '1',
                               verbosidade: int = 3) -> dict:
    """Calcula integral definida ∫_a^b f(x) dx.

    Primeiro calcula a primitiva F(x), depois aplica F(b) - F(a).
    Se a ou b for 'inf'/'-inf', usa integração numérica (Simpson).

    Args:
        expressao: texto da expressão
        variavel: variável de integração
        limite_inferior: limite inferior (número ou 'inf'/'-inf')
        limite_superior: limite superior (número ou 'inf'/'-inf')
        verbosidade: nível de detalhe

    Returns:
        dict com 'resultado', 'latex', 'latex_entrada', 'valor' (numérico),
        'passos', 'historico'
    """
    historico = Historico(verbosidade=verbosidade)
    no = parsear_simbolico(expressao)

    latex_entrada = f'\\int_{{{limite_inferior}}}^{{{limite_superior}}} {no.representacao_latex()} \\, d{variavel}'

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular ∫ de {limite_inferior} a {limite_superior} de {no.representacao_latex()} d{variavel}',
        latex_antes=latex_entrada,
        regra='integral_definida',
        justificativa='Integral definida = F(b) - F(a) onde F é a primitiva',
    ))

    # Verificar se é integral imprópria
    eh_impropria = limite_inferior in ('inf', '+inf', '-inf') or limite_superior in ('inf', '+inf', '-inf')

    if eh_impropria:
        valor_str = integral_impropria(no, variavel, limite_inferior, limite_superior, historico)
        latex_resultado = valor_str

        historico.adicionar(Passo(
            nivel=0,
            descricao='Resultado da integral imprópria',
            latex_antes=latex_entrada,
            latex_depois=latex_resultado,
            regra='resultado',
        ))

        return {
            'resultado': None,
            'latex': latex_resultado,
            'latex_entrada': latex_entrada,
            'valor': valor_str,
            'passos': historico.serializar(),
            'historico': historico,
        }

    # Resolver constantes simbólicas nos limites
    limite_inferior = _resolver_constante(limite_inferior)
    limite_superior = _resolver_constante(limite_superior)

    # Integral definida normal: F(b) - F(a)
    try:
        primitiva = integrar(no, variavel, historico)
        primitiva = simplificar_no(primitiva)
    except ValueError as e:
        # Fallback para integração numérica
        valor_str = _integrar_numericamente(no, variavel, limite_inferior, limite_superior)
        historico.adicionar(Passo(
            nivel=1,
            descricao='Primitiva simbólica não encontrada — usando integração numérica (Simpson)',
            regra='simpson',
        ))

        return {
            'resultado': None,
            'latex': valor_str,
            'latex_entrada': latex_entrada,
            'valor': valor_str,
            'passos': historico.serializar(),
            'historico': historico,
        }

    latex_primitiva = primitiva.representacao_latex()

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Primitiva: F({variavel}) = {latex_primitiva}',
        latex_antes=latex_entrada,
        latex_depois=f'\\left[{latex_primitiva}\\right]_{{{limite_inferior}}}^{{{limite_superior}}}',
        regra='tfc',
        justificativa='Teorema Fundamental do Cálculo: ∫_a^b f dx = F(b) - F(a)',
    ))

    # Avaliar F(b) - F(a)
    a = float(limite_inferior)
    b = float(limite_superior)

    try:
        Fb = primitiva.avaliar({variavel: b, 'C': 0})
        Fa = primitiva.avaliar({variavel: a, 'C': 0})
        valor = Fb - Fa

        historico.adicionar(Passo(
            nivel=2,
            descricao=f'F({limite_superior}) - F({limite_inferior}) = {Fb:.10g} - {Fa:.10g}',
            latex_antes=f'F({limite_superior}) - F({limite_inferior})',
            latex_depois=f'{valor:.10g}',
            regra='avaliacao',
        ))

        # Formatar resultado
        inteiro = round(valor)
        if abs(valor - inteiro) < 1e-9:
            valor_str = str(inteiro)
        else:
            valor_str = f'{valor:.10g}'

        latex_resultado = valor_str

        historico.adicionar(Passo(
            nivel=0,
            descricao='Resultado da integral definida',
            latex_antes=latex_entrada,
            latex_depois=latex_resultado,
            regra='resultado',
        ))

        return {
            'resultado': primitiva,
            'latex': latex_resultado,
            'latex_entrada': latex_entrada,
            'valor': valor_str,
            'passos': historico.serializar(),
            'historico': historico,
        }
    except (ValueError, ZeroDivisionError, OverflowError) as e:
        valor_str = _integrar_numericamente(no, variavel, limite_inferior, limite_superior)

        return {
            'resultado': None,
            'latex': valor_str,
            'latex_entrada': latex_entrada,
            'valor': valor_str,
            'passos': historico.serializar(),
            'historico': historico,
        }


def _resolver_constante(valor: str) -> str:
    """Resolve constantes simbólicas como pi, e, inf."""
    import math
    constantes = {
        'pi': str(math.pi),
        'e': str(math.e),
        '-pi': str(-math.pi),
        '2pi': str(2 * math.pi),
        '2*pi': str(2 * math.pi),
    }
    return constantes.get(valor.strip(), valor)


def _integrar_numericamente(no, variavel, a_str, b_str, n=10000):
    """Integração numérica via Simpson composta."""
    import math
    a = float(a_str)
    b = float(b_str)
    h = (b - a) / n
    soma = 0
    for i in range(n + 1):
        xi = a + i * h
        try:
            fi = no.avaliar({variavel: xi})
            if not math.isfinite(fi):
                return 'indefinido'
        except (ValueError, ZeroDivisionError, OverflowError):
            return 'indefinido'
        if i == 0 or i == n:
            soma += fi
        elif i % 2 == 1:
            soma += 4 * fi
        else:
            soma += 2 * fi
    valor = soma * h / 3
    inteiro = round(valor)
    if abs(valor - inteiro) < 1e-6:
        return str(inteiro)
    return f'{valor:.10g}'
