"""Módulo para resolução de sistemas lineares por eliminação de Gauss."""

from engine.basic.operacoes_basicas import soma, diff, multi, div, reduz_fracao, converter_em_fracao
from engine.basic.passo import Passo, Historico


def _como_fracao(valor: str) -> str:
    """Garante que o valor esteja no formato de fração para aritmética exata."""
    if '/' in valor:
        return valor
    return converter_em_fracao(valor)


class SistemaLinear:
    """Resolve sistemas lineares 2x2 e 3x3 por eliminação de Gauss com passo-a-passo.

    Atributos:
        coeficientes: matriz de coeficientes como strings, ex: [['1','2'],['3','4']]
        constantes: vetor de constantes como strings, ex: ['5','6']
        n: dimensão do sistema
        variaveis: nomes das variáveis (x, y, z)
    """

    def __init__(self, coeficientes: list[list[str]], constantes: list[str]):
        self.coeficientes = [list(linha) for linha in coeficientes]
        self.constantes = list(constantes)
        self.n = len(constantes)
        self.variaveis = ['x', 'y', 'z'][:self.n]

    def _montar_matriz_aumentada(self) -> list[list[str]]:
        """Retorna a matriz aumentada [A|b]."""
        matriz = []
        for i in range(self.n):
            linha = list(self.coeficientes[i]) + [self.constantes[i]]
        return matriz

    def _formato_matriz_latex(self, matriz: list[list[str]]) -> str:
        """Gera representação LaTeX de uma matriz aumentada."""
        linhas = []
        for linha in matriz:
            coefs = ' & '.join(linha[:self.n])
            const = linha[self.n]
            linhas.append(f'{coefs} & | & {const}')
        corpo = ' \\\\ '.join(linhas)
        return f'\\left[\\begin{{array}}{{{" ".join(["c"] * self.n)}|c}}{corpo}\\end{{array}}\\right]'

    def resolver(self) -> tuple:
        """Resolve o sistema linear por eliminação de Gauss.

        Retorna:
            (solucoes, classificacao, historico) onde:
            - solucoes: dict[str, str] mapeando variável -> valor (fração exata)
            - classificacao: 'determinado', 'indeterminado' ou 'impossivel'
            - historico: Historico com os passos da resolução
        """
        historico = Historico(verbosidade=3)

        # Montar matriz aumentada
        matriz = []
        for i in range(self.n):
            linha = list(self.coeficientes[i]) + [self.constantes[i]]
            matriz.append(linha)

        latex_antes = self._formato_matriz_latex(matriz)
        historico.adicionar(Passo(
            nivel=1,
            descricao='Montar a matriz aumentada [A|b]',
            justificativa='Organizar o sistema na forma matricial para aplicar eliminação de Gauss',
            metodo='Matriz aumentada',
            latex_antes=latex_antes,
            latex_depois=latex_antes,
            regra='Representação matricial'
        ))

        # Eliminação de Gauss (escalonamento)
        for col in range(self.n):
            # Buscar pivô não-nulo
            pivo_linha = None
            for linha in range(col, self.n):
                if matriz[linha][col] != '0':
                    pivo_linha = linha
                    break

            if pivo_linha is None:
                # Coluna toda zero abaixo do pivô, continuar
                continue

            # Trocar linhas se necessário
            if pivo_linha != col:
                latex_antes = self._formato_matriz_latex(matriz)
                matriz[col], matriz[pivo_linha] = matriz[pivo_linha], matriz[col]
                latex_depois = self._formato_matriz_latex(matriz)
                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'Trocar L{col + 1} com L{pivo_linha + 1}',
                    justificativa='Colocar pivô não-nulo na posição diagonal',
                    metodo='Troca de linhas',
                    latex_antes=latex_antes,
                    latex_depois=latex_depois,
                    regra='Operação elementar: troca de linhas'
                ))

            # Eliminar variável das linhas abaixo
            for linha in range(col + 1, self.n):
                if matriz[linha][col] == '0':
                    continue

                latex_antes = self._formato_matriz_latex(matriz)
                fator = div(_como_fracao(matriz[linha][col]), _como_fracao(matriz[col][col]))

                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'Eliminar variável {self.variaveis[col]} da L{linha + 1}',
                    justificativa=f'Zerar o coeficiente da coluna {col + 1} na linha {linha + 1}',
                    metodo=f'L{linha + 1} <- L{linha + 1} - ({fator}) * L{col + 1}',
                    latex_antes=latex_antes,
                    latex_depois='',
                    regra='Operação elementar: combinação linear'
                ))

                for j in range(self.n + 1):
                    matriz[linha][j] = diff(matriz[linha][j], multi(fator, matriz[col][j]))

                latex_depois = self._formato_matriz_latex(matriz)
                historico.adicionar(Passo(
                    nivel=3,
                    descricao=f'Resultado da eliminação na L{linha + 1}',
                    justificativa='Aplicação da operação elementar',
                    metodo=f'L{linha + 1} atualizada',
                    latex_antes='',
                    latex_depois=latex_depois,
                    regra='Eliminação de Gauss'
                ))

        # Verificar classificação analisando a matriz escalonada
        for i in range(self.n):
            # Verificar se toda a linha de coeficientes é zero
            todos_zero = all(matriz[i][j] == '0' for j in range(self.n))
            if todos_zero:
                if matriz[i][self.n] != '0':
                    # 0 = k (k != 0) -> impossível
                    historico.adicionar(Passo(
                        nivel=1,
                        descricao='Sistema impossível detectado',
                        justificativa=f'Linha {i + 1} resulta em 0 = {matriz[i][self.n]}, que é uma contradição',
                        metodo='Análise da matriz escalonada',
                        latex_antes=self._formato_matriz_latex(matriz),
                        latex_depois='\\text{Sistema impossível}',
                        regra='Classificação de sistemas lineares'
                    ))
                    return ({}, 'impossivel', historico)
                else:
                    # 0 = 0 -> indeterminado
                    historico.adicionar(Passo(
                        nivel=1,
                        descricao='Sistema indeterminado detectado',
                        justificativa=f'Linha {i + 1} resulta em 0 = 0, indicando infinitas soluções',
                        metodo='Análise da matriz escalonada',
                        latex_antes=self._formato_matriz_latex(matriz),
                        latex_depois='\\text{Sistema indeterminado}',
                        regra='Classificação de sistemas lineares'
                    ))
                    return ({}, 'indeterminado', historico)

        # Substituição reversa
        historico.adicionar(Passo(
            nivel=1,
            descricao='Iniciar substituição reversa',
            justificativa='A matriz está escalonada, resolver de baixo para cima',
            metodo='Back substitution',
            latex_antes=self._formato_matriz_latex(matriz),
            latex_depois='',
            regra='Substituição reversa'
        ))

        solucoes = [''] * self.n
        for i in range(self.n - 1, -1, -1):
            valor = matriz[i][self.n]

            for j in range(i + 1, self.n):
                valor = diff(valor, multi(matriz[i][j], solucoes[j]))

            solucoes[i] = div(_como_fracao(valor), _como_fracao(matriz[i][i]))

            # Normalizar: reduzir fração se aplicável
            if '/' in solucoes[i]:
                solucoes[i] = reduz_fracao(solucoes[i])

            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Calcular {self.variaveis[i]} = {solucoes[i]}',
                justificativa=f'Substituição reversa na linha {i + 1}',
                metodo=f'{self.variaveis[i]} = {solucoes[i]}',
                latex_antes='',
                latex_depois=f'{self.variaveis[i]} = {solucoes[i]}',
                regra='Substituição reversa'
            ))

        resultado = {self.variaveis[i]: solucoes[i] for i in range(self.n)}

        historico.adicionar(Passo(
            nivel=0,
            descricao='Solução do sistema',
            justificativa='Sistema determinado resolvido por eliminação de Gauss',
            metodo='Eliminação de Gauss',
            latex_antes='',
            latex_depois=', '.join(f'{k} = {v}' for k, v in resultado.items()),
            regra='Resultado final'
        ))

        return (resultado, 'determinado', historico)
