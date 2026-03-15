"""Ferramenta: Aplicacoes do Calculo.

Exemplos:
    >>> r = resolver_aplicacao({'tipo': 'maxmin', 'expressao': 'x^3 - 3*x', 'variavel': 'x', 'a': '-5', 'b': '5'})
    >>> print(r['latex'])  # maximo em x=-1, minimo em x=1
"""

from engine.parser_simbolico import parsear_simbolico
from engine.calculo.aplicacoes import encontrar_criticos, volume_disco, comprimento_arco
from engine.basic.passo import Passo, Historico


def resolver_aplicacao(operacao: dict, verbosidade: int = 3) -> dict:
    """Resolve aplicacoes do calculo: max/min, volume, comprimento de arco."""
    historico = Historico(verbosidade=verbosidade)
    tipo = operacao['tipo']

    try:
        no = parsear_simbolico(operacao['expressao'])
        var = operacao.get('variavel', 'x')
        a = float(operacao.get('a', '-5'))
        b = float(operacao.get('b', '5'))
        latex_entrada = no.representacao_latex()

        if tipo == 'maxmin':
            historico.adicionar(Passo(
                nivel=1, descricao=f'Encontrar maximos e minimos de {latex_entrada} em [{a}, {b}]',
                regra='maxmin',
            ))
            criticos = encontrar_criticos(no, var, (a, b))
            partes = []
            for c in criticos:
                partes.append(f'{c["tipo"]} em x={c["x"]:.4f}, f(x)={c["fx"]:.4f}')
            latex_resultado = '; '.join(partes) if partes else 'Sem pontos criticos no intervalo'

            historico.adicionar(Passo(
                nivel=0, descricao='Pontos criticos encontrados',
                latex_depois=latex_resultado, regra='resultado',
            ))
            return {'latex': latex_resultado, 'latex_entrada': latex_entrada,
                    'valor': latex_resultado, 'passos': historico.serializar(), 'historico': historico}

        if tipo == 'volume_revolucao':
            historico.adicionar(Passo(
                nivel=1, descricao=f'Volume de revolucao de {latex_entrada} em [{a}, {b}]',
                regra='volume',
            ))
            vol = volume_disco(no, var, a, b)
            valor_str = f'{vol:.6f}'

            historico.adicionar(Passo(
                nivel=0, descricao=f'Volume = {valor_str}',
                latex_depois=valor_str, regra='resultado',
            ))
            return {'latex': valor_str, 'latex_entrada': latex_entrada,
                    'valor': valor_str, 'passos': historico.serializar(), 'historico': historico}

        if tipo == 'comprimento_arco':
            historico.adicionar(Passo(
                nivel=1, descricao=f'Comprimento de arco de {latex_entrada} em [{a}, {b}]',
                regra='arco',
            ))
            comp = comprimento_arco(no, var, a, b)
            valor_str = f'{comp:.6f}'

            historico.adicionar(Passo(
                nivel=0, descricao=f'Comprimento = {valor_str}',
                latex_depois=valor_str, regra='resultado',
            ))
            return {'latex': valor_str, 'latex_entrada': latex_entrada,
                    'valor': valor_str, 'passos': historico.serializar(), 'historico': historico}

    except Exception as e:
        historico.adicionar(Passo(nivel=0, descricao=f'Erro: {e}', regra='erro'))
        return {'latex': '', 'latex_entrada': operacao.get('expressao', ''),
                'passos': historico.serializar(), 'historico': historico}

    return {'latex': '', 'latex_entrada': '', 'passos': [], 'historico': historico}
