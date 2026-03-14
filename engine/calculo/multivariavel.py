"""Calculo multivariavel — Volume 3 do Guidorizzi.

Operadores diferenciais sobre campos escalares e vetoriais,
matrizes Jacobiana e Hessiana, pontos criticos e multiplicadores de Lagrange.
Toda manipulacao simbolica via NoExpressao, sem dependencias externas (sympy).
"""

from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.derivada import derivar, simplificar_no
from engine.basic.passo import Passo, Historico


# ---------------------------------------------------------------------------
# Derivada parcial
# ---------------------------------------------------------------------------

def derivada_parcial(f: NoExpressao, variavel: str,
                     historico: Historico = None) -> NoExpressao:
    """Derivada parcial: trata todas as outras variaveis como constante.

    ∂f/∂x — usa derivar() internamente; variaveis que nao sao *variavel*
    ja retornam 0 na funcao derivar (comportamento padrao).
    """
    if historico is None:
        historico = Historico()

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calculando derivada parcial em relacao a {variavel}',
        latex_antes=f'\\frac{{\\partial}}{{\\partial {variavel}}}({f.representacao_latex()})',
        regra='Derivada parcial',
    ))

    resultado = derivar(f, variavel, historico)
    resultado = simplificar_no(resultado)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Resultado da derivada parcial em relacao a {variavel}',
        latex_depois=resultado.representacao_latex(),
        regra='Derivada parcial',
    ))

    return resultado


# ---------------------------------------------------------------------------
# Gradiente
# ---------------------------------------------------------------------------

def gradiente(f: NoExpressao, variaveis: list[str]) -> tuple:
    """Vetor gradiente: nabla f = (∂f/∂x1, ∂f/∂x2, ..., ∂f/∂xn).

    Retorna (lista de NoExpressao, Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calculando gradiente em relacao a {variaveis}',
        regra='Gradiente',
    ))

    componentes = []
    for v in variaveis:
        comp = derivada_parcial(f, v, historico)
        componentes.append(comp)

    historico.adicionar(Passo(
        nivel=1,
        descricao='Gradiente calculado',
        latex_depois='\\nabla f = ('
                     + ', '.join(c.representacao_latex() for c in componentes)
                     + ')',
        regra='Gradiente',
    ))

    return componentes, historico


# ---------------------------------------------------------------------------
# Divergente
# ---------------------------------------------------------------------------

def divergente(campo: list[NoExpressao], variaveis: list[str]) -> tuple:
    """Divergente: div(F) = ∂F1/∂x1 + ∂F2/∂x2 + ...

    Retorna (NoExpressao, Historico).
    """
    if len(campo) != len(variaveis):
        raise ValueError('O campo e a lista de variaveis devem ter o mesmo tamanho')

    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Calculando divergente do campo vetorial',
        regra='Divergente',
    ))

    termos = []
    for fi, vi in zip(campo, variaveis):
        di = derivada_parcial(fi, vi, historico)
        termos.append(di)

    # Soma todos os termos
    resultado = termos[0]
    for t in termos[1:]:
        resultado = simplificar_no(op('+', resultado, t))

    historico.adicionar(Passo(
        nivel=1,
        descricao='Divergente calculado',
        latex_depois=resultado.representacao_latex(),
        regra='Divergente',
    ))

    return resultado, historico


# ---------------------------------------------------------------------------
# Rotacional (3D)
# ---------------------------------------------------------------------------

def rotacional(campo: list[NoExpressao],
               variaveis: list[str] = None) -> tuple:
    """Rotacional (3D): rot(F) = nabla x F.

    Retorna ([NoExpressao, NoExpressao, NoExpressao], Historico).
    """
    if variaveis is None:
        variaveis = ['x', 'y', 'z']

    if len(campo) != 3 or len(variaveis) != 3:
        raise ValueError('Rotacional requer exatamente 3 componentes e 3 variaveis')

    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Calculando rotacional do campo vetorial 3D',
        regra='Rotacional',
    ))

    F1, F2, F3 = campo
    x, y, z = variaveis

    # rot(F) = ( ∂F3/∂y - ∂F2/∂z,
    #            ∂F1/∂z - ∂F3/∂x,
    #            ∂F2/∂x - ∂F1/∂y )
    comp_i = simplificar_no(op('-',
        derivada_parcial(F3, y, historico),
        derivada_parcial(F2, z, historico),
    ))
    comp_j = simplificar_no(op('-',
        derivada_parcial(F1, z, historico),
        derivada_parcial(F3, x, historico),
    ))
    comp_k = simplificar_no(op('-',
        derivada_parcial(F2, x, historico),
        derivada_parcial(F1, y, historico),
    ))

    resultado = [comp_i, comp_j, comp_k]

    historico.adicionar(Passo(
        nivel=1,
        descricao='Rotacional calculado',
        latex_depois='\\nabla \\times F = ('
                     + ', '.join(c.representacao_latex() for c in resultado)
                     + ')',
        regra='Rotacional',
    ))

    return resultado, historico


# ---------------------------------------------------------------------------
# Laplaciano
# ---------------------------------------------------------------------------

def laplaciano(f: NoExpressao, variaveis: list[str]) -> tuple:
    """Laplaciano: Delta f = ∂²f/∂x² + ∂²f/∂y² + ...

    Retorna (NoExpressao, Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calculando laplaciano em relacao a {variaveis}',
        regra='Laplaciano',
    ))

    termos = []
    for v in variaveis:
        # Segunda derivada parcial: ∂²f/∂v²
        primeira = derivada_parcial(f, v, historico)
        segunda = derivada_parcial(primeira, v, historico)
        termos.append(segunda)

    resultado = termos[0]
    for t in termos[1:]:
        resultado = simplificar_no(op('+', resultado, t))

    historico.adicionar(Passo(
        nivel=1,
        descricao='Laplaciano calculado',
        latex_depois=resultado.representacao_latex(),
        regra='Laplaciano',
    ))

    return resultado, historico


# ---------------------------------------------------------------------------
# Jacobiana
# ---------------------------------------------------------------------------

def jacobiana(funcoes: list[NoExpressao], variaveis: list[str]) -> tuple:
    """Matriz Jacobiana: J[i][j] = ∂fi/∂xj.

    Retorna (lista de listas de NoExpressao, Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calculando matriz Jacobiana {len(funcoes)}x{len(variaveis)}',
        regra='Jacobiana',
    ))

    matriz = []
    for i, fi in enumerate(funcoes):
        linha = []
        for j, vj in enumerate(variaveis):
            entrada = derivada_parcial(fi, vj, historico)
            linha.append(entrada)
        matriz.append(linha)

    historico.adicionar(Passo(
        nivel=1,
        descricao='Matriz Jacobiana calculada',
        regra='Jacobiana',
    ))

    return matriz, historico


# ---------------------------------------------------------------------------
# Hessiana
# ---------------------------------------------------------------------------

def hessiana(f: NoExpressao, variaveis: list[str]) -> tuple:
    """Matriz Hessiana: H[i][j] = ∂²f/∂xi∂xj.

    Retorna (lista de listas de NoExpressao, Historico).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calculando matriz Hessiana {len(variaveis)}x{len(variaveis)}',
        regra='Hessiana',
    ))

    matriz = []
    for i, vi in enumerate(variaveis):
        linha = []
        # Primeira derivada parcial em relacao a xi
        df_dxi = derivada_parcial(f, vi, historico)
        for j, vj in enumerate(variaveis):
            # Segunda derivada parcial: ∂²f/∂xi∂xj
            entrada = derivada_parcial(df_dxi, vj, historico)
            linha.append(entrada)
        matriz.append(linha)

    historico.adicionar(Passo(
        nivel=1,
        descricao='Matriz Hessiana calculada',
        regra='Hessiana',
    ))

    return matriz, historico


# ---------------------------------------------------------------------------
# Pontos criticos
# ---------------------------------------------------------------------------

def ponto_critico(f: NoExpressao, variaveis: list[str]) -> tuple:
    """Encontra pontos criticos: nabla f = 0.

    Classifica: maximo, minimo, sela (via Hessiana).
    Retorna (pontos: list, classificacoes: list, Historico).

    Nota: resolucao simbolica limitada a casos simples (lineares).
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Buscando pontos criticos (nabla f = 0)',
        regra='Pontos criticos',
    ))

    grad, _ = gradiente(f, variaveis)

    # Tentativa de resolver sistema simples: cada componente do gradiente = 0
    # Para casos lineares em cada variavel, avalia em 0 para encontrar raiz
    # (Implementacao basica — sistemas nao-lineares requerem metodos numericos)
    ponto = {}
    for v, comp in zip(variaveis, grad):
        # Tenta avaliar: se a componente eh uma constante, verificar se eh 0
        try:
            val = comp.avaliar({vi: 0 for vi in variaveis})
            if abs(val) < 1e-12:
                ponto[v] = 0.0
            else:
                # Nao conseguimos resolver simbolicamente
                ponto[v] = None
        except Exception:
            ponto[v] = None

    pontos = [ponto] if all(v is not None for v in ponto.values()) else []

    # Classificacao via Hessiana (para pontos encontrados)
    classificacoes = []
    if pontos:
        H, _ = hessiana(f, variaveis)
        for pt in pontos:
            classificacao = _classificar_ponto_critico(H, pt, variaveis)
            classificacoes.append(classificacao)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Pontos criticos encontrados: {pontos}, classificacoes: {classificacoes}',
        regra='Pontos criticos',
    ))

    return pontos, classificacoes, historico


def _classificar_ponto_critico(H: list, ponto: dict,
                               variaveis: list[str]) -> str:
    """Classifica ponto critico via Hessiana (2D: teste da segunda derivada)."""
    n = len(variaveis)

    # Avaliar Hessiana no ponto
    try:
        H_val = []
        for i in range(n):
            linha = []
            for j in range(n):
                val = H[i][j].avaliar(ponto)
                linha.append(val)
            H_val.append(linha)
    except Exception:
        return 'indeterminado'

    if n == 2:
        # Teste para 2 variaveis: D = H11*H22 - H12^2
        H11, H12 = H_val[0][0], H_val[0][1]
        H21, H22 = H_val[1][0], H_val[1][1]
        D = H11 * H22 - H12 * H21

        if D > 0:
            if H11 > 0:
                return 'minimo'
            else:
                return 'maximo'
        elif D < 0:
            return 'sela'
        else:
            return 'inconclusivo'

    # Caso geral: verificar autovalores (simplificado para diagonal)
    # Verificar se todos os elementos diagonais tem mesmo sinal
    diag = [H_val[i][i] for i in range(n)]
    if all(d > 0 for d in diag):
        return 'minimo (aproximado)'
    elif all(d < 0 for d in diag):
        return 'maximo (aproximado)'
    elif any(d > 0 for d in diag) and any(d < 0 for d in diag):
        return 'sela (aproximado)'
    return 'inconclusivo'


# ---------------------------------------------------------------------------
# Multiplicadores de Lagrange
# ---------------------------------------------------------------------------

def multiplicadores_lagrange(f: NoExpressao, restricao: NoExpressao,
                             variaveis: list[str]) -> tuple:
    """Otimizacao com restricao: nabla f = lambda * nabla g.

    Retorna (pontos: list, Historico).

    Nota: resolucao simbolica limitada a casos simples.
    Monta o sistema nabla f = lambda * nabla g e g = 0.
    """
    historico = Historico()
    historico.adicionar(Passo(
        nivel=1,
        descricao='Aplicando metodo dos multiplicadores de Lagrange',
        latex_antes=f'\\nabla f = \\lambda \\nabla g',
        regra='Multiplicadores de Lagrange',
    ))

    grad_f, _ = gradiente(f, variaveis)
    grad_g, _ = gradiente(restricao, variaveis)

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Gradiente de f: ({", ".join(c.representacao_latex() for c in grad_f)})',
        regra='Multiplicadores de Lagrange',
    ))
    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Gradiente de g: ({", ".join(c.representacao_latex() for c in grad_g)})',
        regra='Multiplicadores de Lagrange',
    ))

    # Sistema: grad_f[i] = lambda * grad_g[i] para cada i, e g = 0
    # Resolucao simbolica basica para casos lineares
    historico.adicionar(Passo(
        nivel=1,
        descricao='Sistema montado: nabla f = lambda * nabla g, g(x) = 0',
        regra='Multiplicadores de Lagrange',
    ))

    # Retorna os gradientes para analise manual (resolucao completa requer
    # solver simbolico mais avancado)
    return [], historico
