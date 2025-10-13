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

class Exponencial:
    def __init__(self, base, expoente,coeficiente):
        self.base = base
        self.expoente = expoente
        self.coeficiente = coeficiente

    def numero_real(self):
        if '/' in self.coeficiente:
            numerador, denominador = self.coeficiente.split('/')
            expoente = basic_operations.div(numerador,denominador)
        else:
            expoente = float(self.expoente)
        return str(float(self.base)**self.expoente)

    def is_exponencial_puro(self):
        if self.coeficiente=='1':
            return True
        else:
            return False
    
    def multi_expo(self, exponencial):
        if not isinstance(exponencial, Exponencial):
            self.coeficiente = basic_operations.multi(self.coeficiente, exponencial.coeficiente)
            return self, exponencial.c
        if exponencial.base == self.base:
            self.expoente = basic_operations.soma(self.expoente, exponencial.expoente)
            if self.expoente == '0':
                return '1'
        else:
            self.coeficiente = basic_operations.multi(self.coeficiente, exponencial.exponencial_em_numero())
            exponencial.coeficiente = '1'

    def div_expo(self, exponencial):
        if exponencial.base == self.base:
            self.expoente = basic_operations.diff(self.expoente, exponencial.expoente)
            if self.expoente == '0':
                return Numero('1')
        else:
            self.coeficiente = basic_operations.div(self.coeficiente, exponencial.exponencial_em_numero())
            exponencial.coeficiente = '1'

    def representacao(self):
        if '/' in self.base:
            return f'\\left({self.base}\\right)^{self.coeficiente}'
        else:
            return f'{self.base}^{self.coeficiente}'
        
    def exponencial_em_raiz(self):
        if '/' not in self.expoente:
            numerador, denominador = basic_operations.converter_em_fracao(self.expoente).split('/')
        else:
            numerador, denominador = self.coeficiente.split('/')

        if denominador=='1':
            raise ValueError(f'Não é possível converter em raiz quadrada, o expoente é {self.coeficiente}')
        elif numerador=='1':
            return Raiz(self.base, denominador)
        else:
            self.expoente = basic_operations.reduz_fracao(self.expoente)
            if '/' not in self.expoente: 
                raise ValueError(f'Não é possível converter em raiz quadrada, o expoente é {self.coeficiente}')
            



        
        

            

class Raiz:
    def __init__(self, radicando, raiz):
        self.raiz = raiz
        self.radicando =radicando