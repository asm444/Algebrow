import basic_operations

class Numero:
    def __init__(self, coeficiente):
        self.coeficiente = coeficiente
    def numero(self):
        return f'{self.coeficiente}'
    def numerador(self):
        return basic_operations.converter_em_fracao(self.coeficiente)[0]
    def denominador(self):
        return basic_operations.converter_em_fracao(self.coeficiente)[1]

class Exponencial:
    def __init__(self, base, expoente,coeficiente):
        self.base = base
        self.expoente = expoente
        self.coeficiente = coeficiente

    def exponencial_em_numero(self):
        if '/' in self.coeficiente:
            numerador, denominador = self.coeficiente.split('/')
            expoente = basic_operations.div(numerador,denominador)
        else:
            expoente = float(self.expoente)
        return float(self.base)**expoente
    
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
        
    def exponencial_to_raiz(self):
        if '/' not in self.expoente:
            raise ValueError(f'Não é possível converter em raiz quadrada, o expoente é {self.coeficiente}')
        else:
            pass

class Raiz:
    def __init__(self, radicando, raiz):
        self.raiz = raiz
        self.radicando =radicando