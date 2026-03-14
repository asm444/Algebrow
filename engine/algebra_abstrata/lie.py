"""Álgebras de Lie e grupos de Lie clássicos."""

import math
from engine.algebra_linear.matriz import Matriz
from engine.basic import operacoes_basicas as ops
from engine.basic.passo import Passo, Historico


def comutador(A: Matriz, B: Matriz) -> tuple:
    """[A, B] = AB - BA. Retorna (Matriz, Historico)."""
    historico = Historico()
    ab = A.multiplicar(B)
    ba = B.multiplicar(A)
    resultado = ab.subtrair(ba)
    historico.adicionar(Passo(
        nivel=1, descricao='Comutador [A, B] = AB - BA',
        latex_antes=f'[A, B]', latex_depois=resultado.representacao_latex(),
        regra='comutador',
        justificativa='O comutador mede quanto A e B falham em comutar',
        metodo='Calcular AB, calcular BA, subtrair'
    ))
    return resultado, historico


def so3_geradores() -> tuple:
    """Geradores de SO(3): Lx, Ly, Lz (matrizes 3×3 antissim)."""
    historico = Historico()
    Lx = Matriz([['0', '0', '0'], ['0', '0', '-1'], ['0', '1', '0']])
    Ly = Matriz([['0', '0', '1'], ['0', '0', '0'], ['-1', '0', '0']])
    Lz = Matriz([['0', '-1', '0'], ['1', '0', '0'], ['0', '0', '0']])
    historico.adicionar(Passo(
        nivel=1, descricao='Geradores de SO(3)',
        regra='so3', justificativa='Base da álgebra de Lie so(3)',
        metodo='Matrizes antissimétrica 3×3 reais'
    ))
    return Lx, Ly, Lz, historico


def rotacao_2d(angulo_rad: float) -> Matriz:
    """R(θ) = [[cos θ, -sin θ], [sin θ, cos θ]]."""
    c = str(round(math.cos(angulo_rad), 10))
    s = str(round(math.sin(angulo_rad), 10))
    neg_s = ops.multi('-1', s)
    return Matriz([[c, neg_s], [s, c]])


def exponencial_matricial(A: Matriz, n_termos: int = 10) -> tuple:
    """exp(A) = I + A + A²/2! + A³/3! + ..."""
    historico = Historico()
    n = A.linhas
    # Identidade
    dados_id = [['1' if i == j else '0' for j in range(n)] for i in range(n)]
    resultado = Matriz(dados_id)
    potencia = Matriz(dados_id)  # A^0 = I
    fatorial = 1

    for k in range(1, n_termos + 1):
        potencia = potencia.multiplicar(A)
        fatorial *= k
        termo = potencia.multiplicar_escalar(ops.reduz_fracao(f'1/{fatorial}'))
        resultado = resultado.somar(termo)

    historico.adicionar(Passo(
        nivel=1, descricao=f'Exponencial matricial com {n_termos} termos',
        regra='exp_matricial',
        justificativa='exp(A) = Σ A^k/k!',
        metodo=f'Soma dos primeiros {n_termos} termos da série'
    ))
    return resultado, historico


def gram_schmidt(vetores: list[list[str]]) -> tuple:
    """Ortogonalização de Gram-Schmidt com aritmética exata."""
    historico = Historico()
    ortonormais = []

    for i, v in enumerate(vetores):
        u = list(v)
        for j, uj in enumerate(ortonormais):
            # proj = (u·uj / uj·uj) * uj
            dot_u_uj = float(_dot(u, uj))
            dot_uj_uj = float(_dot(uj, uj))
            if abs(dot_uj_uj) < 1e-15:
                continue
            coef = dot_u_uj / dot_uj_uj
            for k in range(len(u)):
                u[k] = str(float(u[k]) - coef * float(uj[k]))

        # Normalizar
        norma_sq = _dot(u, u)
        if norma_sq != '0':
            norma = str(math.sqrt(float(norma_sq)))
            u_norm = [ops.reduz_fracao(f'{c}/{norma}') if '.' not in norma
                      else str(float(c) / float(norma)) for c in u]
            ortonormais.append(u_norm)
            historico.adicionar(Passo(
                nivel=2, descricao=f'Vetor {i+1} ortogonalizado e normalizado',
                regra='gram_schmidt'
            ))

    return ortonormais, historico


def _dot(a: list[str], b: list[str]) -> str:
    resultado = '0'
    for ai, bi in zip(a, b):
        resultado = ops.soma(resultado, ops.multi(ai, bi))
    return resultado
