"""Sequencias e convergencia de series — reexporta de serie.py."""

# As funcoes de sequencia estao em serie.py junto com as series,
# pois compartilham a mesma infraestrutura.
# Este modulo reexporta para manter a API solicitada.

from engine.calculo.serie import (
    serie_taylor,
    serie_geometrica,
    serie_p,
)

# Funcoes especificas de sequencia estao neste modulo
from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.derivada import simplificar_no
from engine.basic.passo import Passo, Historico

import math


def _substituir_variavel(no: NoExpressao, variavel: str,
                         valor: NoExpressao) -> NoExpressao:
    """Substitui uma variavel por uma expressao na arvore."""
    if no.tipo == 'variavel' and no.valor == variavel:
        return valor
    if no.tipo == 'numero':
        return no
    if no.tipo == 'variavel':
        return no
    novos_filhos = [_substituir_variavel(f, variavel, valor) for f in no.filhos]
    return NoExpressao(no.tipo, no.valor, novos_filhos)


def _avaliar_limite_infinito(no: NoExpressao, variavel: str) -> float:
    """Tenta avaliar o limite de uma expressao quando variavel -> infinito.

    Usa avaliacao numerica com valores grandes crescentes.
    """
    valores_teste = [100, 1000, 10000, 100000]
    resultados = []
    for v in valores_teste:
        try:
            r = no.avaliar({variavel: float(v)})
            resultados.append(r)
        except (ValueError, ZeroDivisionError, OverflowError):
            return float('nan')

    if not resultados:
        return float('nan')

    ultimo = resultados[-1]
    penultimo = resultados[-2] if len(resultados) > 1 else ultimo

    if math.isinf(ultimo) or math.isinf(penultimo):
        return float('inf') if ultimo > 0 else float('-inf')

    # Verificar se os valores estao crescendo sem limite
    if len(resultados) >= 3:
        diffs = [abs(resultados[i+1]) - abs(resultados[i]) for i in range(len(resultados)-1)]
        if all(d > 0 for d in diffs) and abs(resultados[-1]) > 1e6:
            return float('inf') if ultimo > 0 else float('-inf')

    if abs(ultimo) > 1e-10 and abs(penultimo) > 1e-10:
        if abs(ultimo - penultimo) / max(abs(ultimo), 1e-15) < 0.01:
            return ultimo
    elif abs(ultimo) < 1e-10 and abs(penultimo) < 1e-10:
        return 0.0

    if abs(ultimo) > 1e10:
        return float('inf') if ultimo > 0 else float('-inf')

    return ultimo


def _detectar_graus_polinomio(no: NoExpressao, variavel: str) -> int:
    """Tenta detectar o grau de um polinomio na variavel dada."""
    if no.tipo == 'numero':
        return 0
    if no.tipo == 'variavel':
        return 1 if no.valor == variavel else 0
    if no.tipo == 'operacao':
        if no.valor == '^':
            if (no.filhos[0].tipo == 'variavel' and no.filhos[0].valor == variavel
                    and no.filhos[1].tipo == 'numero'):
                return int(float(no.filhos[1].valor))
        if no.valor in ('+', '-'):
            g_esq = _detectar_graus_polinomio(no.filhos[0], variavel)
            g_dir = _detectar_graus_polinomio(no.filhos[1], variavel)
            if g_esq >= 0 and g_dir >= 0:
                return max(g_esq, g_dir)
        if no.valor == '*':
            g_esq = _detectar_graus_polinomio(no.filhos[0], variavel)
            g_dir = _detectar_graus_polinomio(no.filhos[1], variavel)
            if g_esq >= 0 and g_dir >= 0:
                return g_esq + g_dir
    return -1


def limite_sequencia(expressao: NoExpressao, variavel: str = 'n') -> tuple:
    """Calcula o limite de uma sequencia quando n -> infinito.

    Tecnicas:
    1. Substituicao direta (se converge)
    2. Squeeze theorem
    3. Razao de polinomios: grau do numerador vs denominador

    Retorna (limite: str, Historico)
    """
    historico = Historico(verbosidade=3)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Calculando lim(n->inf) de {expressao.representacao_latex()}',
        regra='Limite de sequencia',
    ))

    # Tecnica 3: Razao de polinomios
    if expressao.tipo == 'operacao' and expressao.valor == '/':
        num_expr = expressao.filhos[0]
        den_expr = expressao.filhos[1]
        grau_num = _detectar_graus_polinomio(num_expr, variavel)
        grau_den = _detectar_graus_polinomio(den_expr, variavel)

        if grau_num >= 0 and grau_den >= 0:
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Razao de polinomios: grau numerador = {grau_num}, '
                          f'grau denominador = {grau_den}',
                regra='Comparacao de graus',
            ))

            if grau_num < grau_den:
                historico.adicionar(Passo(
                    nivel=2,
                    descricao='Grau do numerador < denominador, limite = 0',
                    regra='Razao de polinomios',
                ))
                return '0', historico
            elif grau_num > grau_den:
                historico.adicionar(Passo(
                    nivel=2,
                    descricao='Grau do numerador > denominador, limite = infinito',
                    regra='Razao de polinomios',
                ))
                return 'infinito', historico
            else:
                # Graus iguais: limite = razao dos coeficientes lideres
                # Avaliar numericamente para obter o valor
                val = _avaliar_limite_infinito(expressao, variavel)
                if not math.isnan(val) and math.isfinite(val):
                    if abs(val - round(val)) < 1e-4:
                        val = round(val)
                    historico.adicionar(Passo(
                        nivel=2,
                        descricao=f'Graus iguais, limite = razao dos coeficientes lideres = {val}',
                        regra='Razao de polinomios',
                    ))
                    return str(val), historico

    # Tecnica 1: Avaliacao numerica
    limite_val = _avaliar_limite_infinito(expressao, variavel)

    if math.isnan(limite_val):
        historico.adicionar(Passo(
            nivel=2,
            descricao='Nao foi possivel determinar o limite numericamente',
            regra='Avaliacao numerica',
        ))
        return 'indeterminado', historico

    if math.isinf(limite_val):
        sinal = '+infinito' if limite_val > 0 else '-infinito'
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Sequencia diverge para {sinal}',
            regra='Avaliacao numerica',
        ))
        return sinal, historico

    if abs(limite_val - round(limite_val)) < 1e-6:
        limite_val = round(limite_val)

    resultado = str(limite_val)

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Limite avaliado numericamente: {resultado}',
        regra='Avaliacao numerica',
    ))

    return resultado, historico


def convergencia_serie(termos: NoExpressao, variavel: str = 'n') -> tuple:
    """Testa convergencia de uma serie sum a_n.

    Testes em ordem:
    1. Teste do termo geral (a_n -> 0 eh necessario)
    2. Teste da razao (|a_{n+1}/a_n| < 1)
    3. Teste da raiz (|a_n|^(1/n) < 1)
    4. Teste da comparacao
    5. Teste da integral

    Retorna (resultado: str, teste_usado: str, Historico)
    """
    historico = Historico(verbosidade=3)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Testando convergencia de sum {termos.representacao_latex()}',
        regra='Convergencia de serie',
    ))

    # Teste 1: Termo geral
    limite_val = _avaliar_limite_infinito(termos, variavel)

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Teste do termo geral: lim a_n = {limite_val}',
        regra='Teste do termo geral',
    ))

    if not math.isnan(limite_val) and abs(limite_val) > 1e-10:
        historico.adicionar(Passo(
            nivel=2,
            descricao=f'lim a_n = {limite_val} != 0, serie diverge',
            justificativa='Se lim a_n != 0, a serie diverge',
            regra='Teste do termo geral',
        ))
        return 'diverge', 'teste do termo geral', historico

    # Teste 2: Teste da razao
    n_mais_1 = op('+', var(variavel), num('1'))
    a_n_mais_1 = _substituir_variavel(termos, variavel, n_mais_1)
    razao_expr = op('/', a_n_mais_1, termos)
    razao_limite = _avaliar_limite_infinito(razao_expr, variavel)

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Teste da razao: lim |a_{{n+1}}/a_n| = '
                  f'{abs(razao_limite) if not math.isnan(razao_limite) else "indeterminado"}',
        regra='Teste da razao',
    ))

    if not math.isnan(razao_limite):
        razao_abs = abs(razao_limite)
        if razao_abs < 1 - 1e-10:
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'|razao| = {razao_abs} < 1, serie converge absolutamente',
                regra='Teste da razao',
            ))
            return 'converge', 'teste da razao', historico
        elif razao_abs > 1 + 1e-10:
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'|razao| = {razao_abs} > 1, serie diverge',
                regra='Teste da razao',
            ))
            return 'diverge', 'teste da razao', historico

    # Teste 3: Teste da raiz
    raiz_expr = op('^', func('abs', termos), op('/', num('1'), var(variavel)))
    raiz_limite = _avaliar_limite_infinito(raiz_expr, variavel)

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Teste da raiz: lim |a_n|^(1/n) = '
                  f'{raiz_limite if not math.isnan(raiz_limite) else "indeterminado"}',
        regra='Teste da raiz',
    ))

    if not math.isnan(raiz_limite):
        if raiz_limite < 1 - 1e-10:
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Raiz = {raiz_limite} < 1, serie converge absolutamente',
                regra='Teste da raiz',
            ))
            return 'converge', 'teste da raiz', historico
        elif raiz_limite > 1 + 1e-10:
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Raiz = {raiz_limite} > 1, serie diverge',
                regra='Teste da raiz',
            ))
            return 'diverge', 'teste da raiz', historico

    historico.adicionar(Passo(
        nivel=2,
        descricao='Testes inconclusivos',
        regra='Convergencia',
    ))

    return 'inconclusivo', 'nenhum teste conclusivo', historico


def serie_potencias(coeficientes: list, centro: float = 0) -> tuple:
    """Determina raio de convergencia de uma serie de potencias.
    sum a_n (x-c)^n

    Raio = lim |a_n/a_{n+1}| ou 1/lim |a_n|^(1/n)

    Retorna (raio: str, intervalo: str, Historico)
    """
    historico = Historico(verbosidade=3)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Determinando raio de convergencia da serie de potencias '
                  f'com centro c = {centro}',
        regra='Serie de potencias',
    ))

    n = len(coeficientes)
    if n < 2:
        historico.adicionar(Passo(
            nivel=2,
            descricao='Coeficientes insuficientes para determinar raio',
            regra='Serie de potencias',
        ))
        return 'infinito', '(-infinito, +infinito)', historico

    # Metodo 1: Teste da razao — R = lim |a_n / a_{n+1}|
    razoes = []
    for i in range(n - 1):
        if abs(coeficientes[i + 1]) > 1e-15:
            razoes.append(abs(coeficientes[i] / coeficientes[i + 1]))

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Calculando razoes |a_n/a_{{n+1}}|: '
                  f'{[round(r, 6) for r in razoes[-5:]]}',
        regra='Teste da razao para raio',
    ))

    if razoes and len(razoes) >= 2:
        ultimo = razoes[-1]
        penultimo = razoes[-2]
        if abs(ultimo) > 1e-15 and abs(ultimo - penultimo) / max(abs(ultimo), 1e-15) < 0.1:
            raio = ultimo
            if abs(raio - round(raio)) < 1e-6:
                raio = round(raio)

            raio_str = str(raio)
            intervalo = f'({centro - raio}, {centro + raio})'

            historico.adicionar(Passo(
                nivel=1,
                descricao=f'Raio de convergencia R = {raio_str}',
                latex_depois=f'R = {raio_str}',
                regra='Raio de convergencia',
            ))

            return raio_str, intervalo, historico

    # Metodo 2: Teste da raiz
    raizes = []
    for i in range(1, n):
        if abs(coeficientes[i]) > 1e-15:
            raizes.append(abs(coeficientes[i]) ** (1.0 / i))

    if raizes and len(raizes) >= 2:
        L = raizes[-1]
        if abs(L) > 1e-15:
            raio = 1.0 / L
            if abs(raio - round(raio)) < 1e-6:
                raio = round(raio)

            raio_str = str(raio)
            intervalo = f'({centro - raio}, {centro + raio})'

            historico.adicionar(Passo(
                nivel=1,
                descricao=f'Raio de convergencia pelo teste da raiz: R = {raio_str}',
                regra='Raio de convergencia (raiz)',
            ))

            return raio_str, intervalo, historico

    if all(abs(c) < 1e-15 for c in coeficientes[1:]):
        historico.adicionar(Passo(
            nivel=1,
            descricao='Todos os coeficientes sao zero, raio infinito',
            regra='Serie de potencias trivial',
        ))
        return 'infinito', '(-infinito, +infinito)', historico

    historico.adicionar(Passo(
        nivel=2,
        descricao='Nao foi possivel determinar raio de convergencia',
        regra='Serie de potencias',
    ))

    return 'indeterminado', 'indeterminado', historico
