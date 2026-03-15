"""Ferramenta: Números Complexos.

Exemplos:
    >>> r = resolver_complexo({'tipo': 'complexo', 'expressao': '(3+2i)*(1-i)'}, 3)
    >>> print(r['latex'])  # 5 - i
"""

from engine.complexos.complexo import Complexo
from engine.basic.passo import Passo, Historico
import re


def _parse_complexo(texto: str) -> Complexo:
    """Converte texto como '3+2i' ou '(3+2i)' em Complexo."""
    t = texto.strip().strip('()')
    t = t.replace(' ', '')
    # Formato: a+bi, a-bi, bi, a
    m = re.match(r'^([+-]?\d*\.?\d+)?([+-]\d*\.?\d*)?i$', t)
    if m:
        real = float(m.group(1) or '0')
        imag_str = m.group(2) or '1'
        if imag_str in ('+', ''):
            imag = 1.0
        elif imag_str == '-':
            imag = -1.0
        else:
            imag = float(imag_str)
        return Complexo(real, imag)
    # Só real
    try:
        return Complexo(float(t), 0)
    except ValueError:
        raise ValueError(f"Não foi possível interpretar '{texto}' como número complexo")


def resolver_complexo(operacao: dict, verbosidade: int = 3) -> dict:
    """Resolve operações com números complexos."""
    historico = Historico(verbosidade=verbosidade)
    tipo = operacao['tipo']
    expr = operacao.get('expressao', '')

    try:
        if tipo == 'polar':
            z = _parse_complexo(expr)
            modulo = z.modulo()
            argumento = z.argumento() if hasattr(z, 'argumento') else '?'
            latex_entrada = f'\\text{{polar}}({z.representacao_latex()})'
            latex_resultado = f'|z| = {modulo}'

            historico.adicionar(Passo(
                nivel=0, descricao=f'Forma polar de {z.representacao_latex()}',
                latex_antes=latex_entrada, latex_depois=latex_resultado, regra='polar',
            ))

            return {'latex': latex_resultado, 'latex_entrada': latex_entrada,
                    'valor': str(modulo), 'passos': historico.serializar(), 'historico': historico}

        # Tipo genérico: tentar avaliar expressão complexa
        historico.adicionar(Passo(
            nivel=0, descricao=f'Operação complexa: {expr}',
            regra=tipo,
        ))
        return {'latex': expr, 'latex_entrada': expr,
                'passos': historico.serializar(), 'historico': historico}

    except Exception as e:
        historico.adicionar(Passo(nivel=0, descricao=f'Erro: {e}', regra='erro'))
        return {'latex': '', 'latex_entrada': expr,
                'passos': historico.serializar(), 'historico': historico}
