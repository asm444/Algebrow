from basic import basic_operations

#Representação LaTeX
simbolo = {
    'parenteses_esquerda': "\\left(",
    'parenteses_direita' : "\\right)"
}
def em_chaves(objeto: str) -> str:
    """Retorna {algo}"""
    return '{'+ objeto + '}'

def frac_latex(numerador: str, denominador: str) -> str:
    """Retorna \\frac{numerador}{denominador}"""
    return "\\frac" + em_chaves(numerador) + em_chaves(denominador)

def exponencial_latex(base: str, expoente: str, coeficiente = ''):
    if '/' in base:
        numerador, denominador = base.split('/')
        return simbolo['parenteses_esquerda'] + frac_latex(numerador,denominador) + simbolo['parenteses_direita'] +'^' + em_chaves(expoente)
    else:
        return base + '^' + em_chaves(expoente)

def raiz_latex(radicando: str, indice: str, coeficiente = '') -> str:
    """Retorna coeficiente\\sqrt{radicando}{indice}"""
    return coeficiente + "\sqrt" + em_chaves(indice) + em_chaves(radicando)

def logaritmo_latex(base: str, logaritimando:str, coeficiente = '')-> str:
    """Retorna coeficiente \log_{base}{logaritmando}"""
    return coeficiente + '\log_' + em_chaves(base) + em_chaves(logaritimando)

## Definindo Exponencial, Raiz, Logaritmo, Fração
class Exponencial:
    def __init__(self, base, expoente, coeficiente ='1'):
        self.base = base
        self.expoente = expoente
        self.coeficiente = coeficiente
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
    def return_coeficiente(self):
        return self.coeficiente
    def return_tipo_de_numero(self):
        return self.tipo_de_numero

    #Modificando os dados internos
    def modify_base(self,nova_base):
        self.base = nova_base
    def modify_expoente(self, novo_expoente):
        self.expoente = novo_expoente
    def modify_coeficiente(self, novo_coeficiente):
        self.coeficiente = novo_coeficiente

    def representacao_latex(self):
        if self.coeficiente =='1'         :
            return exponencial_latex(self.base, self.expoente)
        else:
            return exponencial_latex(self.base, self.expoente, self.coeficiente)

    def numero_real(self):
        return basic_operations.inteiro(float(self.base)**float(self.expoente))

class Raiz:
    def __init__(self, indice, radicando, coeficiente ='1'):
        self.indice = indice
        self.radicando = radicando
        self.coeficiente = coeficiente
        self.tipo_de_numero = 'raiz'

    def representacao_latex(self):
        if self.coeficiente=='1':
            return raiz_latex(self.radicando, self.indice)
        else:
            return raiz_latex(self.radicando, self.indice, self.coeficiente)
    
    #Acessando os dados internos
    def return_indice(self):
        return self.indice
    def return_radicando(self):
        return self.radicando
    def return_coeficiente(self):
        return self.coeficiente    
    def return_tipo_de_numero(self):
        return self.tipo_de_numero

    #Modificando os dados internos
    def modify_indice(self,novo_indice):
        self.indice = novo_indice
    def modify_radicando(self, novo_radicando):
        self.radicando = novo_radicando
    def modify_coeficiente(self, novo_coeficiente):
        self.coeficiente = novo_coeficiente

    def numero_real(self):
        return float(self.radicando) ** (1 / float(self.indice))

class Logaritmo:
    def __init__(self, base, logaritimando, coeficiente ='1'):
        self.base = base
        self.logaritimando = logaritimando
        self.tipo_de_numero = 'logaritmo'
        self.coeficiente = coeficiente
    #Acessando os dados internos
    def return_base(self):
        return self.base
    def return_logaritmando(self):
        return self.logaritimando
    def return_coeficiente(self):
        return self.coeficiente    
    def return_tipo_de_numero(self):
        return self.tipo_de_numero

    #Modificando os dados internos
    def modify_base(self,nova_base):
        self.base = nova_base
    def modify_logaritmando(self, novo_logaritimando):
        self.logaritimando = novo_logaritimando
    def modify_coeficiente(self, novo_coeficiente):
        self.coeficiente = novo_coeficiente       

    def numero_real(self):
        from math import log
        return log(float(self.base), float(self.logaritimando))

    def representacao_latex(self):
        if self.coeficiente=='1':
            return logaritmo_latex(self.base, self.logaritimando)
        else:
            return logaritmo_latex(self.base, self.logaritimando, self.coeficiente)

class Racional:
    def __init__(self, numerador, denominador, coeficiente ='1'):
        self.numerador = numerador
        self.denominador = denominador
        self.tipo_de_numero = 'fracao'
        self.coeficiente = coeficiente
    
    #Acessando os dados internos
    def return_numerador(self):
        return self.numerador
    def return_denominador(self):
        return self.denominador

    #Modificando os dados internos
    def modify_numerador(self,nova_numerador):
        self.numerador = nova_numerador
    def modify_denominador(self, novo_denominador):
        self.denominador = novo_denominador
    
    def representacao_latex(self):
        return frac_latex(self.numerador, self.denominador)

    def numero_real(self):
        return basic_operations.div(self.numerador,self.denominador)

class Inteiro:
    def __init__(self, number):
        self.number = number
        self.tipo_de_numero = 'inteiro'
    def representacao_latex(self):
        return self.number
    def number(self):
        return self.number
    
### Capacidade de potencia (36 -> 6^2; 144)
def number_to_potencia(number):
    multiplos_contados = {}
    novo_numero = number
    while novo_numero!=1:
        multiplos_comuns = basic_operations.multiplos_comuns(novo_numero)
        if not multiplos_comuns:
            break
        else:
            multiplo = str(multiplos_comuns[0])
        if multiplo in multiplos_contados:
            multiplos_contados[multiplo] +=1
        else:
            multiplos_contados[multiplo] =1

        novo_numero = str(int(float(basic_operations.div(novo_numero, multiplo))))

    for base in multiplos_contados.keys(): #Ps o algoritmo só trabalha com string.
        multiplos_contados[base] = str(multiplos_contados[base]) 

    return multiplos_contados

number_to_potencia('64')
### Simplificação
def simplificar(objeto):

    if objeto.tipo_de_numero =='fracao':
        fracao = basic_operations.reduz_fracao(objeto.numerador+'/'+objeto.denominador)
        numerador, denominador = fracao.split('/')

        objeto.modify_numerador(numerador)
        objeto.modify_denominador(denominador)

        return objeto
    
    elif objeto.tipo_de_numero == 'raiz': #Testar todo tipo de comportamento inesperado
        radicando = objeto.return_radicando()
        if radicando=='1' or radicando=='0':
            return Inteiro(radicando)

        radicando = number_to_potencia(radicando)
        indice = objeto.return_indice()
        if indice=='0':
            raise ZeroDivisionError("base^{expoente/0} está ocorrendo, alfgo de muito errado está ocorrendo.")
        else:
            coeficiente_total = '1'
            radicando_total = '1'
            #Verificando se radicando sai da raiz ou parte dele
            for base in radicando.keys():
                num, den = int(radicando[base]), int(indice) #numerador, denominador
                inteiro = 0
                while num>= den:
                    inteiro+=1
                    num-=den
                if inteiro==0:
                    radicando_total = basic_operations.multi(radicando_total,str(int(base)**num))
                else:
                    expoente_temporario = basic_operations.diff(radicando[base],basic_operations.multi(str(inteiro),indice))

                    coeficiente_total = basic_operations.multi(coeficiente_total,str(int(base)**inteiro))
                    radicando_total = basic_operations.multi(radicando_total,str(int(base)**int(expoente_temporario)))    
                
            #Devolvendo o objeto simplificado
            if radicando_total=='1':
                return Inteiro(coeficiente_total)
            elif radicando_total=='0':
                return Inteiro('0')
            else:
                objeto.modify_radicando(radicando_total)
                objeto.modify_coeficiente(coeficiente_total)

                return objeto

    elif objeto.tipo_de_numero == 'exponencial':

        base_total = '1'
        
        base = objeto.return_base()
        expoente = objeto.return_expoente()

        if base=='1':
            return Inteiro(objeto.coeficiente)
        elif base=='0':
            return Inteiro('0')
        elif expoente=='0':
            return Inteiro('1')
        else:
            multiplos = number_to_potencia(base)
            if '1' in multiplos.values():
                return objeto

            minimo = min(multiplos.values())
            expoente_total = basic_operations.multi(minimo, expoente)
            for base in multiplos.keys():
                expoente_temporario = int(multiplos[base])//int(minimo)
                if expoente_temporario==0:
                    return objeto
                base_total = basic_operations.multi(base_total, str(int(base)**int(expoente_temporario) ))

            objeto.modify_base(base_total)
            objeto.modify_expoente(expoente_total)

            return objeto

    elif objeto.tipo_de_numero == 'logaritmo':
        
        logaritmando = objeto.return_logaritmando()
        base = objeto.return_base()

        logaritmando_total = '1'
        if base=='1' or base=='0':
            raise ValueError("A função logaritmica não é definida quando constituida com base igual a 1 ou 0.")
        elif logaritmando=='0':
            raise ValueError("A função logaritmica está explodindo para o infinito, logaritmando=0.")
        elif logaritmando=='1':
            return Inteiro('0')
        elif logaritmando==base:
            return Inteiro('1')
        else:
            multiplos = number_to_potencia(logaritmando)
            if '1' in multiplos.values():
                return objeto
            
            logaritmando_total='1'
            coeficiente_total='1'

            minimo = min(multiplos.values())

            for base in multiplos.keys():
                expoente_temporario = int(multiplos[base])//int(minimo)
                if expoente_temporario==0:
                    return objeto
                logaritmando_total = basic_operations.multi(logaritmando_total, str(int(base)**int(expoente_temporario) ))

            coeficiente_total = basic_operations.multi(coeficiente_total, minimo)
            if logaritmando_total==base:
                return Inteiro(coeficiente_total)

            objeto.modify_logaritmando(logaritmando_total)
            objeto.modify_coeficiente(coeficiente_total)

            return objeto