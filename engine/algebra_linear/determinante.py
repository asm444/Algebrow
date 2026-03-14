"""Cálculo de determinante com passo-a-passo pedagógico."""

from engine.basic.operacoes_basicas import soma, diff, multi
from engine.basic.passo import Passo, Historico
from engine.algebra_linear.matriz import Matriz


def _submatriz(m: Matriz, linha_excluir: int, coluna_excluir: int) -> Matriz:
    """Retorna a submatriz eliminando a linha e coluna indicadas."""
    novos_dados = []
    for i in range(m.linhas):
        if i == linha_excluir:
            continue
        linha = []
        for j in range(m.colunas):
            if j == coluna_excluir:
                continue
            linha.append(m.dados[i][j])
        novos_dados.append(linha)
    return Matriz(novos_dados)


def determinante(m: Matriz) -> tuple:
    """Calcula o determinante com passo-a-passo.

    - 1x1: o próprio elemento
    - 2x2: ad - bc
    - 3x3: Regra de Sarrus
    - nxn: Expansão de Laplace pela primeira linha

    Retorna (valor: str, historico: Historico)
    """
    if m.linhas != m.colunas:
        raise ValueError(
            f"Determinante só é definido para matrizes quadradas. "
            f"Dimensões: {m.linhas}x{m.colunas}"
        )

    historico = Historico(verbosidade=3)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calcular determinante de matriz {m.linhas}x{m.colunas}',
        latex_antes=m.representacao_latex(),
        regra='Determinante'
    ))

    valor = _determinante_recursivo(m, historico)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Determinante = {valor}',
        latex_depois=f'\\det(A) = {valor}',
        regra='Resultado final'
    ))

    return (valor, historico)


def _determinante_recursivo(m: Matriz, historico: Historico) -> str:
    """Calcula o determinante recursivamente."""
    n = m.linhas

    if n == 1:
        return m.dados[0][0]

    if n == 2:
        a, b = m.dados[0][0], m.dados[0][1]
        c, d = m.dados[1][0], m.dados[1][1]

        ad = multi(a, d)
        bc = multi(b, c)
        resultado = diff(ad, bc)

        historico.adicionar(Passo(
            nivel=2,
            descricao=f'det 2x2: ({a})({d}) - ({b})({c}) = {ad} - {bc} = {resultado}',
            latex_antes=m.representacao_latex(),
            latex_depois=f'{resultado}',
            regra='Determinante 2x2: ad - bc'
        ))

        return resultado

    if n == 3:
        # Regra de Sarrus
        a = m.dados
        # Diagonais principais
        d1 = multi(multi(a[0][0], a[1][1]), a[2][2])
        d2 = multi(multi(a[0][1], a[1][2]), a[2][0])
        d3 = multi(multi(a[0][2], a[1][0]), a[2][1])
        soma_positiva = soma(soma(d1, d2), d3)

        # Diagonais secundárias
        d4 = multi(multi(a[0][2], a[1][1]), a[2][0])
        d5 = multi(multi(a[0][0], a[1][2]), a[2][1])
        d6 = multi(multi(a[0][1], a[1][0]), a[2][2])
        soma_negativa = soma(soma(d4, d5), d6)

        resultado = diff(soma_positiva, soma_negativa)

        historico.adicionar(Passo(
            nivel=2,
            descricao=(
                f'Regra de Sarrus:\n'
                f'  (+) {a[0][0]}*{a[1][1]}*{a[2][2]} + {a[0][1]}*{a[1][2]}*{a[2][0]} + {a[0][2]}*{a[1][0]}*{a[2][1]} = {soma_positiva}\n'
                f'  (-) {a[0][2]}*{a[1][1]}*{a[2][0]} + {a[0][0]}*{a[1][2]}*{a[2][1]} + {a[0][1]}*{a[1][0]}*{a[2][2]} = {soma_negativa}\n'
                f'  det = {soma_positiva} - {soma_negativa} = {resultado}'
            ),
            latex_antes=m.representacao_latex(),
            latex_depois=f'{resultado}',
            regra='Regra de Sarrus (3x3)'
        ))

        return resultado

    # nxn: Expansão de Laplace pela primeira linha
    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Expansão de Laplace pela primeira linha (matriz {n}x{n})',
        latex_antes=m.representacao_latex(),
        regra='Expansão de Laplace'
    ))

    resultado = '0'
    for j in range(n):
        cofator_sinal = '1' if j % 2 == 0 else '-1'
        sub = _submatriz(m, 0, j)
        det_sub = _determinante_recursivo(sub, historico)
        termo = multi(multi(cofator_sinal, m.dados[0][j]), det_sub)

        historico.adicionar(Passo(
            nivel=3,
            descricao=(
                f'Cofator C(0,{j}): ({cofator_sinal}) * {m.dados[0][j]} * det(submatriz) = '
                f'({cofator_sinal}) * {m.dados[0][j]} * {det_sub} = {termo}'
            ),
            regra='Cofator'
        ))

        resultado = soma(resultado, termo)

    return resultado
