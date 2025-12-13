from basic import basic_operations, numbers
from math import log

class Expressao:
    def __init__(self, termos):
        pass
    def organizar():
        pass
    def simplificar():
        pass
    def representacao_latex():
        pass

#Soma mista de racionais e irracionais (começando pelo mais simples)
# Ordem de expressar Racional > Exponencial > Raiz > Logaritmo

# Definir simbolos que separam eles, uma pseudolinguagem para diminuir a quantidade de código
# Porém a saida será toda organizadas em latex 
# (ou não, tentarei a primeira possibilidade antes de se render para isso)
#
#Definir uma interacao por vez
def soma(numero1, numero2):
    numero1, numero2 = numero1.simplificar(), numero2.simplificar()
    if numero1.tipo_de_numero=='racional':

        if numero2.tipo_de_numero=='racional':
            return numbers.Racional(basic_operations.soma(numero1.number, numero2.number))
        
        else:
            return Expressao(items=[numero1,numero2])

    elif numero1.tipo_de_numero=='raiz':

        if numero2.tipo_de_numero=='raiz':
           
            if numero1.return_indice!=numero2.return_indice:
                return Expressao(items=[numero1, numero2])
            else:
                if numero1.return_radicando!=numero2.radicando:
                    return Expressao(items=[numero1, numero2])
                else:
                    numero1.modify(basic_operations.soma(numero1.coeficiente, numero2.coeficiente))
                    if numero1.coeficiente=='0':
                        return numbers.Racional('0')
                    return numero1 #Soma dos coeficientes here
        else:
            return Expressao(items=[numero1, numero2])

    elif numero1.tipo_de_numero=='exponencial':

        if numero2.tipo_de_numero=='exponencial':
            
            if numero1.tipo_de_numero=='exponencial' and numero2.tipo_de_numero=='exponencial':

                if numero1.return_base!=numero2.return_base:
                    return Expressao(items=[numero1, numero2])
                else:
                    if numero1.return_expoente!=numero2.expoente:
                        return Expressao(items=[numero1, numero2])
                    else:
                        numero1.modify(basic_operations.soma(numero1.coeficiente, numero2.coeficiente))
                        if numero1.coeficiente=='0':
                            return numbers.Racional('0')
                        return numero1 #Soma dos coeficientes here
            else:
                return Expressao(items=[numero1, numero2])
        
    elif numero1.tipo_de_numero=='logaritmo':

        if numero2.tipo_de_numero=='logaritmo':
            
            if numero1.tipo_de_numero=='logaritmo' and numero2.tipo_de_numero=='logaritmo':

                if numero1.return_base!=numero2.return_base:
                    return Expressao(items=[numero1, numero2])
                else:
                    if numero1.return_logaritmando!=numero2.logaritmando:
                        return Expressao(items=[numero1, numero2])
                    else:
                        numero1.modify(basic_operations.soma(numero1.coeficiente, numero2.coeficiente))
                        if numero1.coeficiente=='0':
                            return numbers.Racional('0')
                        return numero1 #Soma dos coeficientes here
            else:
                return Expressao(items=[numero1, numero2])
            
def subtracao(numero1, numero2):
    numero2.modify(basic_operations.multi('-1', numero2.coeficiente))   # A Lógica é igual, muda apenas o sinal do segundo número, foi o que fiz.
    soma(numero1, numero2)

def multiplicacao(numero1, numero2):
    numero1, numero2 = numero1.simplificar(), numero2.simplificar()

    if numero1.tipo_de_numero=='racional':

        if numero2.tipo_de_numero=='racional':
            return numbers.Racional(basic_operations.multi(numero1.number, numero2.number))
        else:
            numero2.modify_coeficiente(basic_operations.multi(numero1.number, numero2.coeficiente))
            return numero2
    
    elif numero1.tipo_de_numero=='exponencial':
        if numero2.tipo_de_numero=='racional':
            numero1.modify_coeficiente(basic_operations.multi(numero2.number, numero1.coeficiente))
            return numero1
        else:
            coeficiente = basic_operations.multi(numero1.coeficiente, numero2.coeficiente)

            if numero2.tipo_de_numero=='exponencial':
                if numero1.base==numero2.base:

                    numero1.modify_expoente(basic_operations.soma(numero1.expoente, numero2.expoente))
                    numero1.modify_coeficiente(coeficiente)

                    return numero1
                #Aqui fica perigoso, não para mim
                if float(numero2.expoente)*log(float(numero2.base))<16: 
                    #Aqui trata o limite de precisão do python que pode gerar erro no calculo se o número for grande de mais
                    pass
