"""Ferramenta: Limites.

Interface textual para o motor de limites simbólicos.

Exemplos de uso:
    >>> resultado = calcular_limite("sin(x)/x", "x", "0")
    >>> print(resultado['latex'])       # 1

    >>> resultado = calcular_limite("1/x", "x", "inf")
    >>> print(resultado['latex'])       # 0

    >>> resultado = calcular_limite_lateral("1/x", "x", "0", "direita")
    >>> print(resultado['latex'])       # inf

    >>> resultado = calcular_limite("(x^2 - 1)/(x - 1)", "x", "1")
    >>> print(resultado['latex'])       # 2 (via L'Hôpital)
"""

from engine.parser_simbolico import parsear_simbolico
from engine.calculo.limite import (
    limite as _limite_interno,
    limite_lateral as _limite_lateral_interno,
    limite_infinito as _limite_infinito_interno,
)
from engine.basic.passo import Passo, Historico


def calcular_limite(expressao: str, variavel: str = 'x', valor: str = '0',
                    verbosidade: int = 3) -> dict:
    """Calcula lim_{x→a} f(x).

    Args:
        expressao: texto da expressão (ex: "sin(x)/x")
        variavel: variável do limite
        valor: ponto do limite (número, 'inf', '-inf')
        verbosidade: nível de detalhe

    Returns:
        dict com 'latex', 'latex_entrada', 'valor', 'passos', 'historico'
    """
    historico = Historico(verbosidade=verbosidade)
    no = parsear_simbolico(expressao)

    # Formatar entrada LaTeX
    if valor in ('inf', '+inf'):
        valor_latex = '\\infty'
    elif valor == '-inf':
        valor_latex = '-\\infty'
    else:
        valor_latex = valor

    latex_entrada = f'\\lim_{{{variavel} \\to {valor_latex}}} {no.representacao_latex()}'

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular lim ({variavel}→{valor}) de {no.representacao_latex()}',
        latex_antes=latex_entrada,
        regra='limite',
    ))

    resultado_str = _limite_interno(no, variavel, valor, historico)

    historico.adicionar(Passo(
        nivel=0,
        descricao='Resultado do limite',
        latex_antes=latex_entrada,
        latex_depois=resultado_str,
        regra='resultado',
    ))

    return {
        'latex': resultado_str,
        'latex_entrada': latex_entrada,
        'valor': resultado_str,
        'passos': historico.serializar(),
        'historico': historico,
    }


def calcular_limite_lateral(expressao: str, variavel: str = 'x', valor: str = '0',
                            lado: str = 'direita', verbosidade: int = 3) -> dict:
    """Calcula limite lateral lim_{x→a+} ou lim_{x→a-} f(x).

    Args:
        expressao: texto da expressão
        variavel: variável do limite
        valor: ponto do limite
        lado: 'direita' (a+) ou 'esquerda' (a-)
        verbosidade: nível de detalhe

    Returns:
        dict com 'latex', 'latex_entrada', 'valor', 'passos', 'historico'
    """
    historico = Historico(verbosidade=verbosidade)
    no = parsear_simbolico(expressao)

    sinal = '+' if lado == 'direita' else '-'
    latex_entrada = f'\\lim_{{{variavel} \\to {valor}^{sinal}}} {no.representacao_latex()}'

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular lim ({variavel}→{valor}{sinal}) de {no.representacao_latex()}',
        latex_antes=latex_entrada,
        regra=f'limite_lateral_{lado}',
    ))

    resultado_str = _limite_lateral_interno(no, variavel, valor, lado, historico)

    historico.adicionar(Passo(
        nivel=0,
        descricao='Resultado do limite lateral',
        latex_antes=latex_entrada,
        latex_depois=resultado_str,
        regra='resultado',
    ))

    return {
        'latex': resultado_str,
        'latex_entrada': latex_entrada,
        'valor': resultado_str,
        'passos': historico.serializar(),
        'historico': historico,
    }
