"""Ferramenta: Derivadas.

Interface textual para o motor de derivação simbólica.
Aceita expressão como texto, parseia, e retorna resultado com passos.

Exemplos de uso:
    >>> resultado = calcular_derivada("x^3 + 2*x", "x")
    >>> print(resultado['latex'])       # 3 \\cdot {x}^{2} + 2
    >>> print(resultado['passos'])      # lista de Passo

    >>> resultado = calcular_derivada("sin(x^2)", "x")
    >>> print(resultado['latex'])       # regra da cadeia aplicada

    >>> resultado = calcular_derivada_ordem("x^4", "x", 2)
    >>> print(resultado['latex'])       # 12 \\cdot {x}^{2}

    >>> resultado = calcular_derivada_implicita("x^2 + y^2 - 1", "x", "y")
    >>> print(resultado['latex'])       # dy/dx = -x/y
"""

from engine.parser_simbolico import parsear_simbolico
from engine.calculo.derivada import derivar, derivar_ordem, derivada_implicita, simplificar_no
from engine.basic.passo import Passo, Historico


def calcular_derivada(expressao: str, variavel: str = 'x',
                      verbosidade: int = 3) -> dict:
    """Calcula d/d(variavel) da expressão.

    Args:
        expressao: texto da expressão (ex: "x^3 + sin(x)")
        variavel: variável de derivação (default: "x")
        verbosidade: nível de detalhe dos passos (0-4)

    Returns:
        dict com chaves: 'resultado' (NoExpressao), 'latex', 'latex_entrada',
        'passos' (lista serializada), 'historico' (Historico)
    """
    historico = Historico(verbosidade=verbosidade)
    no = parsear_simbolico(expressao)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular d/d{variavel} de {no.representacao_latex()}',
        latex_antes=f'\\frac{{d}}{{d{variavel}}}\\left({no.representacao_latex()}\\right)',
        regra='derivada',
        justificativa=f'Derivar a expressão em relação a {variavel}',
    ))

    resultado = simplificar_no(derivar(no, variavel, historico))
    latex_resultado = resultado.representacao_latex()

    historico.adicionar(Passo(
        nivel=0,
        descricao='Resultado da derivada',
        latex_antes=f'\\frac{{d}}{{d{variavel}}}\\left({no.representacao_latex()}\\right)',
        latex_depois=latex_resultado,
        regra='resultado',
    ))

    return {
        'resultado': resultado,
        'latex': latex_resultado,
        'latex_entrada': f'\\frac{{d}}{{d{variavel}}}\\left({no.representacao_latex()}\\right)',
        'passos': historico.serializar(),
        'historico': historico,
    }


def calcular_derivada_ordem(expressao: str, variavel: str = 'x',
                            ordem: int = 2, verbosidade: int = 3) -> dict:
    """Calcula d^n/d(variavel)^n da expressão.

    Args:
        expressao: texto da expressão
        variavel: variável de derivação
        ordem: ordem da derivada (2, 3, ...)
        verbosidade: nível de detalhe

    Returns:
        dict com 'resultado', 'latex', 'latex_entrada', 'passos', 'historico'
    """
    historico = Historico(verbosidade=verbosidade)
    no = parsear_simbolico(expressao)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular derivada de ordem {ordem} de {no.representacao_latex()}',
        latex_antes=f'\\frac{{d^{ordem}}}{{d{variavel}^{ordem}}}\\left({no.representacao_latex()}\\right)',
        regra=f'derivada_ordem_{ordem}',
    ))

    resultado = derivar_ordem(no, variavel, ordem, historico)
    latex_resultado = resultado.representacao_latex()

    historico.adicionar(Passo(
        nivel=0,
        descricao=f'Resultado da derivada de ordem {ordem}',
        latex_antes=f'\\frac{{d^{ordem}}}{{d{variavel}^{ordem}}}\\left({no.representacao_latex()}\\right)',
        latex_depois=latex_resultado,
        regra='resultado',
    ))

    return {
        'resultado': resultado,
        'latex': latex_resultado,
        'latex_entrada': f'\\frac{{d^{ordem}}}{{d{variavel}^{ordem}}}\\left({no.representacao_latex()}\\right)',
        'passos': historico.serializar(),
        'historico': historico,
    }


def calcular_derivada_implicita(expressao_F: str, var_x: str = 'x',
                                var_y: str = 'y', verbosidade: int = 3) -> dict:
    """Calcula dy/dx dado F(x,y) = 0 usando derivada implícita.

    Args:
        expressao_F: texto de F(x,y) (ex: "x^2 + y^2 - 1")
        var_x: variável independente
        var_y: variável dependente
        verbosidade: nível de detalhe

    Returns:
        dict com 'resultado', 'latex', 'latex_entrada', 'passos', 'historico'
    """
    historico = Historico(verbosidade=verbosidade)
    no = parsear_simbolico(expressao_F)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Derivada implícita: d{var_y}/d{var_x} dado F({var_x},{var_y}) = 0',
        latex_antes=f'{no.representacao_latex()} = 0',
        regra='derivada_implicita',
        justificativa=f'd{var_y}/d{var_x} = -F_{var_x} / F_{var_y}',
    ))

    resultado = derivada_implicita(no, var_x, var_y, historico)
    latex_resultado = resultado.representacao_latex()

    return {
        'resultado': resultado,
        'latex': latex_resultado,
        'latex_entrada': f'\\frac{{d{var_y}}}{{d{var_x}}}\\left({no.representacao_latex()} = 0\\right)',
        'passos': historico.serializar(),
        'historico': historico,
    }
