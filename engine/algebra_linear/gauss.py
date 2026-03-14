"""Eliminação de Gauss com passo-a-passo pedagógico."""

from engine.basic.operacoes_basicas import soma, diff, multi, div, reduz_fracao, converter_em_fracao
from engine.basic.passo import Passo, Historico
from engine.algebra_linear.matriz import Matriz


def _normalizar(valor: str) -> str:
    """Normaliza resultado de div: converte '1.0' -> '1', frações ficam como estão."""
    if '/' in valor:
        return reduz_fracao(valor)
    convertido = converter_em_fracao(valor)
    if '/' in convertido:
        return reduz_fracao(convertido)
    return convertido


def eliminacao_gaussiana(m: Matriz, b: list[str]) -> tuple:
    """Eliminação de Gauss com passo-a-passo pedagógico.

    Recebe a matriz de coeficientes (m) e o vetor de termos independentes (b).

    Retorna (solucoes: list[str], classificacao: str, historico: Historico)
    Classificação: 'determinado', 'indeterminado', 'impossivel'

    Cada operação elementar (Li <- Li - k*Lj) gera um Passo.
    """
    if m.linhas != len(b):
        raise ValueError(
            f"Número de linhas da matriz ({m.linhas}) difere do vetor b ({len(b)})"
        )

    historico = Historico(verbosidade=3)
    n = m.linhas
    cols = m.colunas

    # Construir matriz aumentada: copiar dados + coluna b
    aumentada = []
    for i in range(n):
        linha = list(m.dados[i]) + [b[i]]
        aumentada.append(linha)

    def _latex_aumentada():
        linhas_latex = []
        for i in range(n):
            partes = []
            for j in range(cols + 1):
                val = aumentada[i][j]
                if '/' in val:
                    num, den = val.split('/')
                    partes.append(f'\\frac{{{num}}}{{{den}}}')
                else:
                    partes.append(val)
            # Separar a última coluna com |
            coefs = ' & '.join(partes[:-1])
            termo = partes[-1]
            linhas_latex.append(f'{coefs} & {termo}')
        corpo = ' \\\\ '.join(linhas_latex)
        return f'\\left(\\begin{{array}}{{{"c" * cols}|c}} {corpo} \\end{{array}}\\right)'

    historico.adicionar(Passo(
        nivel=1,
        descricao='Montar matriz aumentada [A|b]',
        latex_depois=_latex_aumentada(),
        regra='Eliminação de Gauss'
    ))

    # Eliminação progressiva (escalonamento)
    pivot_row = 0
    for col in range(cols):
        if pivot_row >= n:
            break

        # Buscar pivô não-nulo na coluna
        pivot_found = -1
        for i in range(pivot_row, n):
            if aumentada[i][col] != '0':
                pivot_found = i
                break

        if pivot_found == -1:
            continue  # Coluna toda zero, pular

        # Trocar linhas se necessário
        if pivot_found != pivot_row:
            aumentada[pivot_row], aumentada[pivot_found] = aumentada[pivot_found], aumentada[pivot_row]
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Trocar L{pivot_row + 1} <-> L{pivot_found + 1}',
                latex_depois=_latex_aumentada(),
                regra='Troca de linhas'
            ))

        pivo = aumentada[pivot_row][col]

        # Eliminar elementos abaixo do pivô
        for i in range(pivot_row + 1, n):
            if aumentada[i][col] == '0':
                continue

            fator = _normalizar(div(aumentada[i][col], pivo))
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'L{i + 1} <- L{i + 1} - ({fator}) * L{pivot_row + 1}',
                latex_antes=_latex_aumentada(),
                regra='Operação elementar'
            ))

            for j in range(cols + 1):
                aumentada[i][j] = diff(aumentada[i][j], multi(fator, aumentada[pivot_row][j]))

            historico.adicionar(Passo(
                nivel=3,
                descricao=f'Resultado da operação em L{i + 1}',
                latex_depois=_latex_aumentada(),
                regra='Resultado da eliminação'
            ))

        pivot_row += 1

    historico.adicionar(Passo(
        nivel=1,
        descricao='Matriz escalonada',
        latex_depois=_latex_aumentada(),
        regra='Forma escalonada'
    ))

    # Classificar o sistema
    # Contar o posto (número de linhas não-nulas na parte dos coeficientes)
    posto = 0
    for i in range(n):
        linha_zero = all(aumentada[i][j] == '0' for j in range(cols))
        if not linha_zero:
            posto += 1

    # Verificar inconsistência: linha com coeficientes zeros e b != 0
    for i in range(n):
        coefs_zero = all(aumentada[i][j] == '0' for j in range(cols))
        if coefs_zero and aumentada[i][cols] != '0':
            historico.adicionar(Passo(
                nivel=1,
                descricao=f'Sistema impossível: L{i + 1} tem coeficientes nulos mas b != 0',
                regra='Classificação do sistema'
            ))
            return ([], 'impossivel', historico)

    if posto < cols:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Sistema indeterminado: posto ({posto}) < número de variáveis ({cols})',
            regra='Classificação do sistema'
        ))
        return ([], 'indeterminado', historico)

    # Sistema determinado: substituição regressiva
    historico.adicionar(Passo(
        nivel=1,
        descricao='Sistema determinado. Aplicar substituição regressiva.',
        regra='Substituição regressiva'
    ))

    solucoes = ['0'] * cols
    for i in range(cols - 1, -1, -1):
        # x_i = (b_i - sum(a_ij * x_j for j > i)) / a_ii
        rhs = aumentada[i][cols]
        for j in range(i + 1, cols):
            rhs = diff(rhs, multi(aumentada[i][j], solucoes[j]))

        solucoes[i] = _normalizar(div(rhs, aumentada[i][i]))

        historico.adicionar(Passo(
            nivel=2,
            descricao=f'x{i + 1} = {solucoes[i]}',
            regra='Substituição regressiva'
        ))

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Solução: {", ".join(f"x{i+1} = {s}" for i, s in enumerate(solucoes))}',
        regra='Resultado final'
    ))

    return (solucoes, 'determinado', historico)
