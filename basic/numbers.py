from basic_operations

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

## Definindo Exponencial, Raiz, Logaritmo, Fração
class Exponencial:
    def __init__(self, base, expoente):
        self.base = base
        self.expoente = expoente
        self.tipo_de_numero = 'exponencial'

        if expoente in '/':
            self.converte_para_raiz = True
        else:
            self.converte_para_raiz = False

    #Acessando os dados internos
    def return_base(self):
        return self.base
    def return_expoente(self):
        return self.expoente
    def return_tipo_de_numero(self):
        return self.tipo_de_numero

    #Modificando os dados internos
    def modify_base(self,nova_base):
        self.base = nova_base
    def modify_expoente(self, novo_expoente):
        self.expoente = novo_expoente

    def representacao_latex(self):
        if '/' in self.base:
            self.base = basic_operations.reduz_fracao(self.base)          
        return exponencial(self.base, self.expoente)

    def numero_real(self):
        return basic basic_operations.inteiro(float(base)**float(expoente))

class Raiz:
    def __init__(self, indice, radicando):
        self.indice = indice
        self.radicando = radicando
        self.tipo_de_numero = 'raiz'

    def representacao_latex(self):
        return raiz_latex(self.radicando, self.indice)
    
    #Acessando os dados internos
    def return_indice(self):
        return self.indice
    def return_radicando(self):
        return self.radicando
    def return_tipo_de_numero(self):
        return self.tipo_de_numero

    #Modificando os dados internos
    def modify_indice(self,novo_indice):
        self.indice = nova_indice
    def modify_radicando(self, novo_radicando):
        self.radicando = novo_radicando


    def numero_real(self):
        if '/' in self.indice:
            numerador, denominador = self.expoente.split('/')
            numerador, denominador = float(numerador), float(denominador)
        else:
            numerador, denominador = float(self.expoente), 1

        return basic_operations.inteiro(float(self.base)**(denominador/numerador))

class Logaritmo:
    def __init__(self, base, logaritimando):
        self.base = base
        self.logaritimando = logaritimando
        self.tipo_de_numero = 'logaritmo'

    #Acessando os dados internos
    def return_base(self):
        return self.base
    def return_logaritimando(self):
        return self.logaritimando
    def return_tipo_de_numero(self):
        return self.tipo_de_numero

    #Modificando os dados internos
    def modify_base(self,nova_base):
        self.base = nova_base
    def modify_logaritimando(self, novo_logaritimando):
        self.logaritimando = novo_logaritimando

    def numero_real(self):
        from math import log
        return log(self.logaritimando, self.logaritimando)

    def representacao_latex(self):
        return logaritmo_latex(self.base, self.logaritimando)

class Fracao:
    def __init__(self, numerador, denominador):
        self.numerador = numerador
        self.denominador = denominador
    
    #Acessando os dados internos
    def return_numerador(self):
        return self.numerador
    def return_denominador(self):
        return self.denominador = denominador

    #Modificando os dados internos
    def modify_numerador(self,nova_numerador):
        self.numerador = nova_numerador
    def modify_denominador(self, novo_denominador):
        self.denominador = novo_denominador
    
    def representacao_latex(self):
        return frac_latex(self.numerador, self.denominador)

    def 

### Simplificação

def simplificar(objeto):

    if objeto.tipo