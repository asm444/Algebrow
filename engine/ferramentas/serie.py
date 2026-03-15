"""Ferramenta: Séries de Taylor/Maclaurin.

Exemplos:
    >>> resultado = calcular_taylor("sin(x)", "x", "0", 5)
    >>> print(resultado['latex'])  # x - x^3/6 + x^5/120
"""

from engine.parser_simbolico import parsear_simbolico
from engine.calculo.serie import serie_taylor
from engine.calculo.derivada import simplificar_no
from engine.basic.passo import Passo, Historico


def calcular_taylor(expressao: str, variavel: str = 'x', ponto: str = '0',
                    ordem: int = 5, verbosidade: int = 3) -> dict:
    """Calcula série de Taylor de f(x) em torno de a até ordem n."""
    historico = Historico(verbosidade=verbosidade)
    no = parsear_simbolico(expressao)
    a = float(ponto)

    latex_entrada = f'T_{{{ordem}}}\\left({no.representacao_latex()},\\, {variavel}={ponto}\\right)'

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Série de Taylor de {no.representacao_latex()} em {variavel}={ponto} até ordem {ordem}',
        latex_antes=latex_entrada,
        regra='taylor',
    ))

    resultado = serie_taylor(no, variavel, a, ordem, historico)
    resultado = simplificar_no(resultado)
    latex_resultado = resultado.representacao_latex()

    historico.adicionar(Passo(
        nivel=0,
        descricao='Resultado da série de Taylor',
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
