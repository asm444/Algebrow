"""Ferramenta: Álgebra Linear.

Exemplos:
    >>> r = calcular_determinante("[[1,2],[3,4]]")
    >>> print(r['valor'])  # -2
"""

import ast
from engine.algebra_linear.matriz import Matriz
from engine.algebra_linear.determinante import determinante_laplace
from engine.algebra_linear.autovalor import autovalores_2x2
from engine.basic.passo import Passo, Historico


def _parse_matriz(texto: str) -> Matriz:
    """Converte '[[1,2],[3,4]]' em Matriz usando ast.literal_eval (seguro)."""
    dados = ast.literal_eval(texto.strip())
    linhas = [[str(e) for e in linha] for linha in dados]
    return Matriz(linhas)


def calcular_determinante(matriz_texto: str, verbosidade: int = 3) -> dict:
    """Calcula o determinante de uma matriz."""
    historico = Historico(verbosidade=verbosidade)
    try:
        m = _parse_matriz(matriz_texto)
        latex_entrada = f'\\det{m.representacao_latex()}'

        historico.adicionar(Passo(
            nivel=1, descricao=f'Calcular determinante de matriz {m.linhas}x{m.colunas}',
            latex_antes=latex_entrada, regra='determinante',
        ))

        valor = determinante_laplace(m, historico)

        historico.adicionar(Passo(
            nivel=0, descricao='Resultado do determinante',
            latex_antes=latex_entrada, latex_depois=str(valor), regra='resultado',
        ))

        return {'latex': str(valor), 'latex_entrada': latex_entrada,
                'valor': str(valor), 'passos': historico.serializar(), 'historico': historico}
    except Exception as e:
        historico.adicionar(Passo(nivel=0, descricao=f'Erro: {e}', regra='erro'))
        return {'latex': '', 'latex_entrada': matriz_texto,
                'valor': '', 'passos': historico.serializar(), 'historico': historico}


def calcular_autovalores(matriz_texto: str, verbosidade: int = 3) -> dict:
    """Calcula autovalores de uma matriz 2x2."""
    historico = Historico(verbosidade=verbosidade)
    try:
        m = _parse_matriz(matriz_texto)
        latex_entrada = f'\\text{{autovalores}}{m.representacao_latex()}'

        historico.adicionar(Passo(
            nivel=1, descricao='Calcular autovalores via polinômio característico',
            latex_antes=latex_entrada, regra='autovalores',
        ))

        resultado = autovalores_2x2(m, historico)
        latex_resultado = str(resultado)

        return {'latex': latex_resultado, 'latex_entrada': latex_entrada,
                'passos': historico.serializar(), 'historico': historico}
    except Exception as e:
        historico.adicionar(Passo(nivel=0, descricao=f'Erro: {e}', regra='erro'))
        return {'latex': '', 'latex_entrada': matriz_texto,
                'passos': historico.serializar(), 'historico': historico}
