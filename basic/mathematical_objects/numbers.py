import basic_operations

class Numero:
    def __init__(self, coeficiente):
        self.coeficiente = coeficiente
        if '/' not in self.coeficiente:
            self.fracao = basic_operations.converter_em_fracao(coeficiente)
            self.numerador, self.denominador = self.fracao.split('/')
        else:
            self.numerador, self.denominador = coeficiente.split('/')
            self.fracao = coeficiente
    def numero_real(self):
        if '/' not in self.coeficiente:
            return self.coeficiente
        else:
            return basic_operations.div(*self.fracao.split('/'))
    def numerador(self):
        return self.numerador
    def denominador(self):
        return self.denominador
    def retornar_fracao(self):
        return self.fracao
    def representacao_latex(self,fracao=False):
        if fracao or '/' in self.coeficiente:
            return "\\frac{"+self.numerador+"}{"+self.denominador+"}"
        else:
            return self.coeficiente