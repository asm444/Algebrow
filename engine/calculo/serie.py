"""Series matematicas: Taylor, geometrica, serie p."""

import math

from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.derivada import derivar, simplificar_no
from engine.basic.passo import Passo, Historico


def _fatorial(n: int) -> int:
    """Calcula fatorial de n."""
    if n <= 1:
        return 1
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado


def serie_taylor(f: NoExpressao, centro: float = 0, n_termos: int = 6,
                 variavel: str = 'x') -> tuple:
    """Calcula a serie de Taylor/Maclaurin de f em torno de 'centro' com n termos.

    T(x) = sum f^(k)(a)/k! * (x-a)^k, k=0..n-1

    Retorna (NoExpressao da serie, Historico com passos)
    Cada derivada gera um passo explicativo.
    """
    historico = Historico(verbosidade=3)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calculando serie de Taylor de {f.representacao_latex()} '
                  f'em torno de a={centro} com {n_termos} termos',
        regra='Serie de Taylor',
    ))

    # Calcular derivadas sucessivas e avaliar no centro
    derivada_atual = f
    termos = []

    for k in range(n_termos):
        # Avaliar derivada no centro
        try:
            valor_derivada = derivada_atual.avaliar({variavel: centro})
        except (ValueError, ZeroDivisionError):
            valor_derivada = 0.0

        fat_k = _fatorial(k)
        coef = valor_derivada / fat_k

        historico.adicionar(Passo(
            nivel=2,
            descricao=f'f^({k})({centro}) = {valor_derivada}, '
                      f'coeficiente = {valor_derivada}/{fat_k} = {coef}',
            regra=f'Derivada de ordem {k}',
        ))

        if abs(coef) > 1e-15:
            # Construir termo: coef * (x - centro)^k
            if k == 0:
                termo = num(str(coef))
            else:
                if centro == 0:
                    base = var(variavel)
                else:
                    base = op('-', var(variavel), num(str(centro)))

                if k == 1:
                    potencia = base
                else:
                    potencia = op('^', base, num(str(k)))

                if abs(coef - 1.0) < 1e-15:
                    termo = potencia
                elif abs(coef - (-1.0)) < 1e-15:
                    termo = op('*', num('-1'), potencia)
                else:
                    termo = op('*', num(str(coef)), potencia)

            termos.append(termo)

        # Calcular proxima derivada
        if k < n_termos - 1:
            derivada_atual = simplificar_no(derivar(derivada_atual, variavel))

    # Montar expressao somando termos
    if not termos:
        resultado = num('0')
    else:
        resultado = termos[0]
        for t in termos[1:]:
            resultado = op('+', resultado, t)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Serie de Taylor com {n_termos} termos calculada',
        latex_depois=resultado.representacao_latex(),
        regra='Serie de Taylor',
    ))

    return resultado, historico


def serie_geometrica(razao: NoExpressao,
                     primeiro_termo: NoExpressao = None) -> tuple:
    """Soma da serie geometrica infinita: a/(1-r) se |r| < 1.
    Retorna (soma ou 'diverge', Historico)
    """
    historico = Historico(verbosidade=3)

    if primeiro_termo is None:
        primeiro_termo = num('1')

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Serie geometrica com razao r = {razao.representacao_latex()} '
                  f'e primeiro termo a = {primeiro_termo.representacao_latex()}',
        regra='Serie Geometrica',
    ))

    # Avaliar razao numericamente
    try:
        r_val = razao.avaliar({})
    except ValueError:
        # Razao contem variavel — retornar expressao simbolica
        historico.adicionar(Passo(
            nivel=2,
            descricao='Razao contem variavel, retornando expressao simbolica a/(1-r)',
            regra='Serie Geometrica',
        ))
        soma = op('/', primeiro_termo, op('-', num('1'), razao))
        return soma, historico

    if abs(r_val) >= 1:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'|r| = {abs(r_val)} >= 1, serie diverge',
            justificativa='Condicao de convergencia: |r| < 1',
            regra='Teste de convergencia geometrica',
        ))
        return 'diverge', historico

    # Convergente: S = a / (1 - r)
    try:
        a_val = primeiro_termo.avaliar({})
    except ValueError:
        a_val = None

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'|r| = {abs(r_val)} < 1, serie converge',
        justificativa='Condicao de convergencia satisfeita',
        regra='Teste de convergencia geometrica',
    ))

    soma_expr = op('/', primeiro_termo, op('-', num('1'), razao))

    if a_val is not None:
        soma_val = a_val / (1 - r_val)
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'S = a/(1-r) = {a_val}/({1 - r_val}) = {soma_val}',
            latex_depois=str(soma_val),
            regra='Soma da serie geometrica',
        ))
        return soma_expr, historico

    return soma_expr, historico


def serie_p(p: float) -> tuple:
    """Serie p: sum 1/n^p. Converge se p > 1.
    Retorna (convergencia: str, Historico com justificativa)
    """
    historico = Historico(verbosidade=3)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Analisando serie p com p = {p}: sum 1/n^{p}',
        regra='Serie p',
    ))

    if p > 1:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'p = {p} > 1, portanto a serie converge',
            justificativa='Pelo teste da serie p (integral de 1/x^p converge para p > 1)',
            regra='Teste da serie p',
        ))
        return 'converge', historico
    else:
        descricao = f'p = {p} <= 1, portanto a serie diverge'
        if p == 1:
            descricao = f'p = {p} (serie harmonica), diverge'
        historico.adicionar(Passo(
            nivel=2,
            descricao=descricao,
            justificativa='Pelo teste da serie p (integral de 1/x^p diverge para p <= 1)',
            regra='Teste da serie p',
        ))
        return 'diverge', historico
