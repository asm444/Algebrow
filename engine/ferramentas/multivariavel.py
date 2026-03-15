"""Ferramenta: Cálculo Multivariável.

Exemplos:
    >>> r = calcular_gradiente("x^2 + y^2", ["x", "y"])
    >>> print(r['latex'])  # (2x, 2y)
"""

from engine.parser_simbolico import parsear_simbolico
from engine.calculo.derivada import derivar, simplificar_no
from engine.basic.passo import Passo, Historico


def calcular_gradiente(expressao: str, variaveis: list, verbosidade: int = 3) -> dict:
    """Calcula o gradiente de f em relacao as variaveis dadas."""
    historico = Historico(verbosidade=verbosidade)
    try:
        no = parsear_simbolico(expressao)
        vars_str = ', '.join(variaveis)
        latex_entrada = f'\\nabla f({vars_str}) \\text{{ onde }} f = {no.representacao_latex()}'

        historico.adicionar(Passo(
            nivel=1, descricao=f'Calcular gradiente de {no.representacao_latex()}',
            latex_antes=latex_entrada, regra='gradiente',
        ))

        componentes = []
        for v in variaveis:
            d = simplificar_no(derivar(no, v, historico))
            componentes.append(d.representacao_latex())

        latex_resultado = '\\left(' + ', '.join(componentes) + '\\right)'

        historico.adicionar(Passo(
            nivel=0, descricao='Resultado do gradiente',
            latex_antes=latex_entrada, latex_depois=latex_resultado, regra='resultado',
        ))

        return {'latex': latex_resultado, 'latex_entrada': latex_entrada,
                'passos': historico.serializar(), 'historico': historico}
    except Exception as e:
        historico.adicionar(Passo(nivel=0, descricao=f'Erro: {e}', regra='erro'))
        return {'latex': '', 'latex_entrada': expressao,
                'passos': historico.serializar(), 'historico': historico}
