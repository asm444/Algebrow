from basic import basic_operations

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
    if numero1.tipo_de_numero=='racional':

        if numero2.tipo_de_numero=='racional':
            return basic_operations.soma(numero1, numero2)
        
        else:
            numero2 = numero2.simplificar()
            if numero2.tipo_de_numero=='racional':
                return basic_operations.soma(numero1, numero2)
            else:
                return Expressao(items=[numero1,numero2])

    elif numero1.tipo_de_numero=='raiz':

        if numero2.tipo_de_numero=='racional':

            numero1 = numero1.simplificar()
            if numero1.tipo_de_numero=='racional':
                return basic_operations.soma(numero1, numero2)
            else:
                return Expressao(items=[numero1, numero2])

        elif numero2.tipo_de_numero=='raiz':

            numero1, numero2 = numero1.simplificar(), numero2.simplificar()
            if numero1.tipo_de_numero=='racional' and numero2.tipo_de_numero=='racional':
                return basic_operations.soma(numero1, numero2)
            if numero1.tipo_de_numero=='raiz' and numero2.tipo_de_numero=='raiz':

                if numero1.return_indice!=numero2.return_indice:
                    return Expressao(items=[numero1, numero2])
                else:
                    if numero1.return_radicando!=numero2.radicando:
                        return Expressao(items=[numero1, numero2])
                    else:
                        numero1.modify(basic_operations.soma(numero1.coeficiente, numero2.coeficiente))
            else:
                return Expressao(items=[numero1, numero2])

    elif numero2.tipo_de_numero=='exponencial':

        numero2 = numero2.simplificar()
        if numero2.tipo_de_numero=='racional':
            return Expressao(items=[numero1, numero2])
        el




