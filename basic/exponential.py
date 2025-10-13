import basic_operations

class Exponencial:

    def __init__(self, base, expoente,coeficiente):
        self.base = base
        self.expoente = expoente
        self.coeficiente = coeficiente

    def exponencial_em_numero(self):
        return basic_operations.inteiro(self.base)**basic_operations.inteiro(self.expoente)
    def multi_expo(self, exponencial):
        if exponencial.base == self.base:
            self.expoente = basic_operations.soma(self.expoente, exponencial.expoente)
            if self.expoente == '0':
                return '1'
        else:
            self.coeficiente = basic_operations.multi(self.coeficiente, exponencial.exponencial_em_numero())
            del exponencial
    def div_expo(self, exponencial):
        if exponencial.base == self.base:
            self.expoente = basic_operations.diff(self.expoente, exponencial.expoente)
            if self.expoente == '0':
                return '1'
        else:
            self.coeficiente = basic_operations.div(self.coeficiente, exponencial.exponencial_em_numero())
            del exponencial
    
print(basic_operations.reduz_fracao('5/1'))