"""Ferramenta: Funções Especiais (Gamma, Beta, Stirling).

Interface textual para o motor de funções especiais.
Aceita argumento como texto, parseia, e retorna resultado com passos.

Exemplos de uso:
    >>> resultado = calcular_gamma("5")
    >>> print(resultado['latex'])       # \\Gamma(5) = 24.0
    >>> print(resultado['valor'])       # 24.0
    >>> print(resultado['passos'])      # lista de passos serializados

    >>> resultado = calcular_gamma("0.5")
    >>> print(resultado['valor'])       # 1.7724538509...  (sqrt(pi))

    >>> resultado = calcular_gamma("2.5")
    >>> print(resultado['valor'])       # 1.3293403881791...
"""

from engine.funcoes_especiais.gamma import gamma
from engine.basic.passo import Passo, Historico


def calcular_gamma(argumento: str, verbosidade: int = 3) -> dict:
    """Calcula a função Gamma Γ(z) para o argumento fornecido.

    Args:
        argumento: valor de z como texto (ex: "5", "0.5", "2.5")
        verbosidade: nível de detalhe dos passos (0-4)

    Returns:
        dict com chaves:
            'latex'        — representação LaTeX do resultado
            'latex_entrada'— representação LaTeX da entrada
            'valor'        — valor numérico (float)
            'passos'       — lista serializada de passos
            'historico'    — objeto Historico

    Raises:
        Retorna dict com 'erro' em caso de falha.

    Exemplos:
        >>> calcular_gamma("5")['valor']
        24.0
        >>> calcular_gamma("1")['valor']
        1.0
    """
    historico = Historico(verbosidade=verbosidade)
    try:
        z = float(argumento)
    except (ValueError, TypeError) as exc:
        return {
            'latex': '',
            'latex_entrada': argumento,
            'valor': None,
            'passos': [],
            'historico': historico,
            'erro': f'Argumento inválido: {exc}',
        }

    latex_entrada = f'\\Gamma({z})'

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular Γ({z})',
        latex_antes=latex_entrada,
        regra='Função Gamma',
        justificativa='Avaliar a função Gamma no argumento fornecido',
    ))

    try:
        valor, hist_gamma = gamma(z)
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        historico.adicionar(Passo(
            nivel=0,
            descricao=f'Erro ao calcular Γ({z}): {exc}',
            regra='Erro',
        ))
        return {
            'latex': '',
            'latex_entrada': latex_entrada,
            'valor': None,
            'passos': historico.serializar(),
            'historico': historico,
            'erro': str(exc),
        }

    # Incorporar passos do motor
    for passo in hist_gamma.todos():
        historico.adicionar(passo)

    latex_resultado = f'\\Gamma({z}) = {valor:.10g}'

    historico.adicionar(Passo(
        nivel=0,
        descricao=f'Resultado: Γ({z}) = {valor:.10g}',
        latex_antes=latex_entrada,
        latex_depois=latex_resultado,
        regra='resultado',
    ))

    return {
        'latex': latex_resultado,
        'latex_entrada': latex_entrada,
        'valor': valor,
        'passos': historico.serializar(),
        'historico': historico,
    }
