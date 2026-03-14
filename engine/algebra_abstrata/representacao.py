"""Representacoes matriciais de grupos."""
from engine.algebra_linear.matriz import Matriz
from engine.basic.passo import Passo, Historico
from engine.algebra_abstrata.grupo import Grupo


def representacao_regular(grupo: Grupo) -> dict:
    """Representacao regular: cada elemento -> matriz de permutacao."""
    hist = Historico()
    n = grupo.ordem()
    elems = grupo.elementos
    resultado = {}

    hist.adicionar(Passo(
        1, f"Construindo representacao regular de grupo de ordem {n}",
        regra="Representacao Regular"
    ))

    for g in elems:
        # Matriz de permutacao: M[i][j] = 1 se g * elems[j] == elems[i]
        dados = []
        for i in range(n):
            linha = []
            for j in range(n):
                if grupo.operar(g, elems[j]) == elems[i]:
                    linha.append('1')
                else:
                    linha.append('0')
            dados.append(linha)
        resultado[g] = Matriz(dados)

        hist.adicionar(Passo(
            2, f"Elemento {g} -> matriz {n}x{n}",
            latex_depois=Matriz(dados).representacao_latex(),
            regra="Permutacao"
        ))

    return resultado, hist


def representacao_trivial(grupo: Grupo) -> dict:
    """Representacao trivial: todos -> identidade 1x1."""
    hist = Historico()
    resultado = {}
    for g in grupo.elementos:
        resultado[g] = Matriz([['1']])

    hist.adicionar(Passo(
        1, "Representacao trivial: todos elementos mapeados para [1]",
        regra="Representacao Trivial"
    ))

    return resultado, hist


def caractere(representacao: dict) -> dict:
    """Tabela de caracteres: chi(g) = Tr(rho(g))."""
    resultado = {}
    for g, mat in representacao.items():
        # Traco = soma dos elementos diagonais
        traco = '0'
        from engine.basic.operacoes_basicas import soma
        for i in range(mat.linhas):
            traco = soma(traco, mat.dados[i][i])
        resultado[g] = traco
    return resultado


def tabela_caracteres(grupo: Grupo) -> tuple:
    """Tabela completa de caracteres (representacao regular).
    Retorna (tabela_latex: str, Historico)."""
    hist = Historico()

    rep, rep_hist = representacao_regular(grupo)
    # Transferir passos
    for p in rep_hist.todos():
        hist.adicionar(p)

    chars = caractere(rep)

    hist.adicionar(Passo(
        1, "Calculando caracteres: chi(g) = Tr(rho(g))",
        regra="Caractere"
    ))

    # Montar LaTeX
    elems = grupo.elementos
    header = " & ".join(str(e) for e in elems)
    vals = " & ".join(str(chars[e]) for e in elems)
    latex = (
        f"\\begin{{array}}{{{'c' * (len(elems) + 1)}}}\n"
        f"g & {header} \\\\ \\hline\n"
        f"\\chi_{{reg}} & {vals} \\\\\n"
        f"\\end{{array}}"
    )

    hist.adicionar(Passo(
        1, "Tabela de caracteres construida",
        latex_depois=latex,
        regra="Tabela de Caracteres"
    ))

    return latex, hist
