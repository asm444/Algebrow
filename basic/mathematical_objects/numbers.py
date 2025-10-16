import basic_operations

#Representação LaTeX
simbolo = {
    'parenteses_esquerda': "\\left(",
    'parenteses_direita' : "\\right)"
}
def em_chaves(objeto: str) -> str:
    """Retorna {algo}"""
    return '\{'+ objeto + '\}'

def frac_latex(numerador: str, denominador: str) -> str:
    """Retorna \\frac{numerador}{denominador}"""
    return "\\frac" + em_chaves(numerador) + em_chaves(denominador)

def exponencial_latex(base: str, expoente: str, coeficiente = ''):
    if '/' in base:
        numerador, denominador = base.split('/')
        return simbolo[parenteses_esquerda] + frac_latex(numerador,denominador) + simbolo[parenteses_direita] +'^' + em_chaves(expoente)
    else:
        return base + '^' + em_chaves(expoente)

def raiz_latex(radicando: str, indice: str, coeficiente = '') -> str:
    """Retorna coeficiente\\sqrt{radicando}{indice}"""
    return coeficiente + "\\sqrt" + em_chaves(radicando) + em_chaves(radicando)

def logaritmo_latex(base: str, logaritimando:str, coeficiente = '')-> str:
    """Retorna coeficiente\\log_{base}{logaritmando}"""
    return coeficiente + '\\log_' + em_chaves(base) + em_chaves(logaritimando)

## Definindo Exponencial, Raiz, Logaritmo
class Exponencial:
    def __init__(self, base, expoente):
        self.base = base
        self.expoente = expoente

    def representacao_latex(self):
        if '/' in self.base:
            self.base = basic_operations.reduz_fracao(self.base)          
        return exponencial(self.base, self.expoente)

    def numero_real(self):
        return basic_operations.inteiro(float(base)**float(expoente))

class Raiz:
    def __init__(self, indice, radicando):
        self.indice = indice
        self.radicando = radicando

    def representacao_latex(self):
        return raiz_latex(self.radicando, self.indice)

    def numero_real(self):
        if '/' in self.indice:
            numerador, denominador = self.expoente.split('/')
            numerador, denominador = float(numerador), float(denominador)
        else:
            numerador, denominador = float(self.expoente), 1

        return basic_operations.inteiro(float(self.base)**(denominador/numerador))

class Logaritmo:
    def __init__(self, base, logaritimando)
        self.base = base
        self.logaritimando = logaritimando

    def numero_real(self):
        from math import log
        return log(float(self.base), float(self.logaritimando))
    
    def representacao_latex(self):
        return logaritmo_latex(self.base, self.logaritimando)

