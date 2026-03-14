"""Módulo para resolução de inequações do 1º grau."""

from engine.basic.operacoes_basicas import div, diff, reduz_fracao, converter_em_fracao
from engine.basic.passo import Passo, Historico


def _como_fracao(valor: str) -> str:
    """Garante que o valor esteja no formato de fração para aritmética exata."""
    if '/' in valor:
        return valor
    return converter_em_fracao(valor)


class Inequacao1Grau:
    """Resolve inequações do tipo a*x + b {operador} 0.

    Atributos:
        a: coeficiente de x (string)
        b: termo independente (string)
        operador: um de '>', '<', '>=', '<='
    """

    OPERADORES_VALIDOS = ('>', '<', '>=', '<=')
    OPERADOR_INVERTIDO = {
        '>': '<',
        '<': '>',
        '>=': '<=',
        '<=': '>=',
    }

    def __init__(self, a: str, b: str, operador: str):
        if operador not in self.OPERADORES_VALIDOS:
            raise ValueError(f"Operador inválido: '{operador}'. Use um de {self.OPERADORES_VALIDOS}")
        self.a = a
        self.b = b
        self.operador = operador

    def _eh_negativo(self, valor: str) -> bool:
        """Verifica se um valor string representa um número negativo."""
        if '/' in valor:
            num, den = valor.split('/')
            num_neg = num.strip().startswith('-')
            den_neg = den.strip().startswith('-')
            return num_neg ^ den_neg
        return valor.strip().startswith('-')

    def resolver(self) -> tuple:
        """Resolve a inequação a*x + b {operador} 0.

        Retorna:
            (conjunto_solucao, historico) onde:
            - conjunto_solucao: string como 'x > 3' ou 'x <= -2/3'
            - historico: Historico com os passos da resolução
        """
        historico = Historico(verbosidade=3)

        # Passo 1: Apresentar a inequação
        latex_ineq = f'{self.a}x + {self.b} {self.operador} 0'
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Resolver a inequação: {self.a}x + {self.b} {self.operador} 0',
            justificativa='Isolar x para encontrar o conjunto solução',
            metodo='Resolução de inequação do 1º grau',
            latex_antes=latex_ineq,
            latex_depois='',
            regra='Inequação do 1º grau'
        ))

        if self.a == '0':
            # Caso degenerado: b {op} 0
            b_neg = self._eh_negativo(self.b)
            b_zero = self.b == '0'

            if self.operador == '>':
                valido = not b_zero and not b_neg  # b > 0
            elif self.operador == '<':
                valido = b_neg  # b < 0
            elif self.operador == '>=':
                valido = b_zero or not b_neg  # b >= 0
            elif self.operador == '<=':
                valido = b_zero or b_neg  # b <= 0

            if valido:
                resultado = 'x ∈ ℝ'
            else:
                resultado = 'x ∈ ∅'

            historico.adicionar(Passo(
                nivel=1,
                descricao=f'Coeficiente de x é zero: {self.b} {self.operador} 0',
                justificativa='A inequação não depende de x',
                metodo='Análise direta',
                latex_antes=f'{self.b} {self.operador} 0',
                latex_depois=resultado,
                regra='Inequação degenerada'
            ))
            return (resultado, historico)

        # Passo 2: Passar b para o outro lado
        neg_b = diff('0', self.b)
        if '/' in neg_b:
            neg_b = reduz_fracao(neg_b)

        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Subtrair {self.b} de ambos os lados',
            justificativa='Isolar o termo com x',
            metodo=f'{self.a}x {self.operador} {neg_b}',
            latex_antes=f'{self.a}x + {self.b} {self.operador} 0',
            latex_depois=f'{self.a}x {self.operador} {neg_b}',
            regra='Transposição de termos'
        ))

        # Passo 3: Dividir por a (atenção ao sinal!)
        a_negativo = self._eh_negativo(self.a)
        operador_final = self.operador

        if a_negativo:
            operador_final = self.OPERADOR_INVERTIDO[self.operador]
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Dividir ambos os lados por {self.a} (negativo: inverter o sinal)',
                justificativa='Ao dividir por número negativo, o sentido da desigualdade se inverte',
                metodo=f'x {operador_final} {neg_b} / {self.a}',
                latex_antes=f'{self.a}x {self.operador} {neg_b}',
                latex_depois='',
                regra='Inversão do sinal da desigualdade'
            ))
        else:
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Dividir ambos os lados por {self.a}',
                justificativa='Isolar x dividindo pelo coeficiente',
                metodo=f'x {operador_final} {neg_b} / {self.a}',
                latex_antes=f'{self.a}x {self.operador} {neg_b}',
                latex_depois='',
                regra='Divisão por coeficiente'
            ))

        valor = div(_como_fracao(neg_b), _como_fracao(self.a))
        if '/' in valor:
            valor = reduz_fracao(valor)

        conjunto_solucao = f'x {operador_final} {valor}'

        historico.adicionar(Passo(
            nivel=0,
            descricao=f'Conjunto solução: {conjunto_solucao}',
            justificativa='Inequação resolvida',
            metodo='Resolução de inequação do 1º grau',
            latex_antes='',
            latex_depois=conjunto_solucao,
            regra='Resultado final'
        ))

        return (conjunto_solucao, historico)
