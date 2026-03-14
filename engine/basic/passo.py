class Passo:
    """Representa um passo individual de uma resolução matemática.

    Atributos:
        nivel: int de 0 a 4, indica o grau de detalhe deste passo.
            0 = resultado final apenas
            1 = passos principais (ex: 'Fatorar radicando')
            2 = passos intermediários (ex: 'Extrair fatores do radical')
            3 = detalhes aritméticos (ex: '216 = 2³ × 3³')
            4 = micro-operações (ex: '216 ÷ 2 = 108')
        descricao: texto em PT-BR descrevendo o que foi feito
        justificativa: porquê este passo foi necessário
        metodo: como a operação foi realizada
        latex_antes: representação LaTeX antes da transformação
        latex_depois: representação LaTeX depois da transformação
        regra: nome da regra matemática aplicada
    """

    def __init__(self, nivel, descricao, latex_antes='', latex_depois='',
                 regra='', justificativa='', metodo=''):
        self.nivel = nivel
        self.descricao = descricao
        self.justificativa = justificativa
        self.metodo = metodo
        self.latex_antes = latex_antes
        self.latex_depois = latex_depois
        self.regra = regra

    def __repr__(self):
        return f"Passo(nivel={self.nivel}, regra='{self.regra}', descricao='{self.descricao}')"

    def serializar(self):
        resultado = {
            'nivel': self.nivel,
            'descricao': self.descricao,
            'regra': self.regra,
        }
        if self.justificativa:
            resultado['justificativa'] = self.justificativa
        if self.metodo:
            resultado['metodo'] = self.metodo
        if self.latex_antes:
            resultado['latex_antes'] = self.latex_antes
        if self.latex_depois:
            resultado['latex_depois'] = self.latex_depois
        return resultado


class Historico:
    """Acumula passos durante uma resolução e filtra por verbosidade.

    Níveis de verbosidade:
        0 = Apenas resultado final (sem passos)
        1 = Passos principais (interpretar, resultado)
        2 = Passos intermediários (fatoração, extração, propriedades)
        3 = Detalhes aritméticos (fatoração prima, cálculos)
        4 = Micro-operações (cada divisão, cada multiplicação)
    """

    def __init__(self, verbosidade=3):
        self.verbosidade = verbosidade
        self._passos = []

    def adicionar(self, passo):
        self._passos.append(passo)

    def filtrar(self):
        return [p for p in self._passos if p.nivel <= self.verbosidade]

    def todos(self):
        return list(self._passos)

    def limpar(self):
        self._passos.clear()

    def serializar(self):
        return [p.serializar() for p in self.filtrar()]

    def __len__(self):
        return len(self._passos)

    def __repr__(self):
        return f"Historico(verbosidade={self.verbosidade}, total={len(self._passos)}, visiveis={len(self.filtrar())})"
