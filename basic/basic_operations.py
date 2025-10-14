############# Variáveis
primos = '.\\data\\primos.txt'

def inteiro(numero):
    ponto = float(numero)
    inteiro = int(ponto)
    if ponto.is_integer():
        return str(inteiro)
    else:
        return numero
    
def detectar_dizima(numerador, denominador):
    numerador = abs(float(numerador))
    denominador = abs(float(denominador))

    def normalizar(valor):
        s = str(valor)
        if '.' in s:
            casas = len(s.split('.')[1])
            return int(s.replace('.', '')), 10 ** casas
        return int(valor), 1

    n_num, d_num = normalizar(numerador)
    n_den, d_den = normalizar(denominador)

    numerador_final = n_num * d_den
    denominador_final = n_den * d_num

    parte_inteira = numerador_final // denominador_final
    resto = numerador_final % denominador_final

    if resto == 0:
        return f"{float(parte_inteira)}"

    parte_decimal = ""
    restos_vistos = {}
    pos = 0
    repeticao_inicio = None

    while resto != 0:
        if resto in restos_vistos:
            repeticao_inicio = restos_vistos[resto]
            break

        restos_vistos[resto] = pos
        resto *= 10
        digito = resto // denominador_final
        parte_decimal += str(digito)
        resto = resto % denominador_final
        pos += 1

        if pos > 200:
            return f"{float(numerador_final / denominador_final)}"

    if repeticao_inicio is not None:
        parte_nao_repete = parte_decimal[:repeticao_inicio]
        parte_repete = parte_decimal[repeticao_inicio:]
        if parte_nao_repete == "":
            return f"{parte_inteira}.({parte_repete})"
        else:
            return f"{parte_inteira}.{parte_nao_repete}({parte_repete})"

    return f"{float(numerador_final / denominador_final)}"

#Operações Básicas: Contém frações!
def soma(valor1: str, valor2: str) -> str:
    """Soma dois números racionais."""
    if '/' not in valor1:
        if '/' not in valor2:
            if '.' not in valor1:
                if '.' not in valor2:
                    return inteiro(str(int(valor1)+int(valor2)))
                else:
                    decimais = valor2.split('.')[1]
            else:
                if '.' not in valor2:
                    decimais = valor1.split('.')[1]
                else:
                    if valor2.split('.')[1] < valor1.split('.')[1]:
                        decimais = valor1.split('.')[1]
                    else:
                        decimais = valor2.split('.')[1]
            return inteiro(str(round(float(valor1)+float(valor2),len(decimais))))
            
        else:
            numerador1, denominador1 = converter_em_fracao(valor1).split('/')
            numerador2, denominador2 = valor2.split('/')
    else:
        if '/' not in valor2:
            numerador1, denominador1 = valor1.split('/')
            numerador2, denominador2 = converter_em_fracao(valor2).split('/')
        else:
            numerador1, denominador1 = valor1.split('/')
            numerador2, denominador2 = valor2.split('/')

            if denominador1==denominador2:
                return reduz_fracao(soma(numerador1,numerador2)+'/'+denominador1)
            
    return reduz_fracao(soma(multi(numerador1,denominador2),multi(numerador2,denominador1))+'/'+multi(denominador1,denominador2))      

def diff(valor1: str, valor2:str) -> str:
    """Diferença de dois números racionais. Segundo argumento muda o sinal."""
    if '/' not in valor1:
        if '/' not in valor2:
            if '.' not in valor1:
                if '.' not in valor2:
                    return inteiro(str(int(valor1)-int(valor2)))
                else:
                    decimais = valor2.split('.')[1]
            else:
                if '.' not in valor2:
                    decimais = valor1.split('.')[1]
                else:
                    if valor2.split('.')[1] < valor1.split('.')[1]:
                        decimais = valor1.split('.')[1]
                    else:
                        decimais = valor2.split('.')[1]
            return inteiro(str(round(float(valor1)-float(valor2),len(decimais))))
        else:
            numerador1, denominador1 = converter_em_fracao(valor1).split('/')
            numerador2, denominador2 = valor2.split('/')
    else:
        if '/' not in valor2:
            numerador1, denominador1 = valor1.split('/')
            numerador2, denominador2 = converter_em_fracao(valor2).split('/')
        else:
            numerador1, denominador1 = valor1.split('/')
            numerador2, denominador2 = valor2.split('/')

            if denominador1==denominador2:
                return reduz_fracao(diff(numerador1,numerador2)+'/'+denominador1)
            
    return reduz_fracao(diff(multi(numerador1,denominador2),multi(numerador2,denominador1))+'/'+multi(denominador1,denominador2)) 

def multi(valor1: str, valor2: str) -> float:
    """Multiplicação de dois números racionais."""
    if valor1 == '0' or valor2 == '0':
        return '0'
    else:
        if '/' not in valor1:
            if '/' not in valor2:
                if '.' not in valor1:
                    if '.' not in valor2:
                        return inteiro(str(int(valor1)*int(valor2)))
                    else:
                        decimais = valor2.split('.')[1]
                else:
                    if '.' not in valor2:
                        decimais = valor1.split('.')[1]
                    else:
                        decimais = valor2.split('.')[1]+valor1.split('.')[1]
                return inteiro(str(round(float(valor1)*float(valor2),len(decimais))))
            else:
                numerador1, denominador1 = converter_em_fracao(valor1).split('/')
                numerador2, denominador2 = valor2.split('/')
                if numerador2=='0': return '0'

        else:
            if '/' not in valor2:
                numerador1, denominador1 = valor1.split('/')
                if numerador1=='0': return '0'
                numerador2, denominador2 = converter_em_fracao(valor2).split('/')
            else:
                numerador1, denominador1 = valor1.split('/')
                numerador2, denominador2 = valor2.split('/')

        return reduz_fracao(multi(numerador1,numerador2)+'/'+multi(denominador1,denominador2))
            
def div(valor1: str, valor2: str) -> float:
    """Divisão de números racionais. Natualmente emite erro se houver divisão por zero."""
    #Sinal
    if '-' in valor1 and  '-' not in valor2:
        sinal = '-'
        valor1 = valor1.split('-')[1]
    elif '-' in valor2 and  '-' not in valor1:
        sinal = '-'
        valor2 = valor2.split('-')[1]
    elif '-' in valor1 and '-' in valor2:
        sinal = ''
    else:
        sinal =''
    if '/' not in valor1:
        if '/' not in valor2:
            if valor1 =='0': 
                if valor2 =='0': raise ZeroDivisionError("Divisão por zero")

                return '0'             
            
            return sinal+detectar_dizima(inteiro(valor1), inteiro(valor2))
        else:
            if valor1 =='0': return '0' 

            numerador1, denominador1 = converter_em_fracao(valor1).split('/')
            numerador2, denominador2 = valor2.split('/')
            if numerador2 =='0': raise ZeroDivisionError("Divisão por zero")
    else:
        if '/' not in valor2:
            if valor2 =='0': raise ZeroDivisionError("Divisão por zero")
            
            numerador1, denominador1 = valor1.split('/')
            numerador2, denominador2 = converter_em_fracao(valor2).split('/')

        else:
            numerador1, denominador1 = valor1.split('/')
            numerador2, denominador2 = valor2.split('/')

            if numerador2 =='0': raise ZeroDivisionError("Divisão por zero")

    if numerador2=='0' or denominador1 =='0': raise ZeroDivisionError("Divisão por zero")

    return sinal+reduz_fracao(multi(numerador1,denominador2)+'/'+multi(denominador1,numerador2))

def fatorial(valor: int) -> int:
    """Fatorial na forma não integral, confia será útil."""
    if valor == 0 or valor == 1:
        return 1
    else:
        return valor * fatorial(valor-1)

def multiplos_comuns(valores: list) -> set:
    if isinstance(valores,str) or isinstance(valores,int):
        divisores = []
        n = int(valores)
        with open(primos, 'r') as f:
            for linha in f:
                p = int(linha.strip())
                if p > n:
                    break
                elif n % p == 0:
                    divisores.append(p)
                elif p >1000000000:
                    raise ValueError("Há algum erro na conta, não é possível.")
        return divisores

    else:
        lista_de_multiplos = [set(multiplos_comuns(int(valor))) for valor in valores]

        intersecao = lista_de_multiplos[0]
        for conjunto in lista_de_multiplos[1:]:
            intersecao = intersecao & conjunto
        return intersecao

def converter_em_fracao(n: str) -> str: 
    """
    Inicialmente projetado para converter qualquer dizimias em fração. 
    A ideias é converter qualquer número de ponto flutuante em fração. 
    Lógico que função não será aplicada em números irracionais. 
    Números irracionais são mais faceis de criar, precisiveis e não serão uma preocupação.
    """
    if '/' in n:
        return n

    elif '.' in n:
        parte_inteira, resto = n.split('.')
    else:
        return n+'/'+'1'
    
    parte_inteira = int(parte_inteira) if parte_inteira else 0

    if '(' in resto and ')' in resto:
        nao_periodica, periodica = resto.split('(')
        periodica = periodica.rstrip(')')
    else:
        if resto == '':
            return f"{parte_inteira}"
        
        numerador = int(parte_inteira * (10 ** len(resto)) + int(resto))
        denominador = 10 ** len(resto)
        return reduz_fracao(f"{numerador}/{denominador}")
    
    n = len(nao_periodica)
    k = len(periodica)
  
    total = int(nao_periodica + periodica)
    nao_periodico_int = int(nao_periodica) if nao_periodica else 0
    
    numerador_decimal = total - nao_periodico_int
    denominador_decimal = (10**n) * (10**k - 1)
    
    numerador_total = parte_inteira * denominador_decimal + numerador_decimal
    denominador_total = denominador_decimal

    #### Equação de conversão dizima em fração ==> 
    # fração = parte inteira + {(todo número até o fim do período) - (todo número até antes do período)}/((10**k - 1 ) 10**n)

    fracao_resultante =  reduz_fracao(f"{numerador_total}/{denominador_total}")

    numerador, denominador = fracao_resultante.split('/')

    if numerador > 1000000000 or denominador > 1000000000:
        return n  #Quase irracional ou multiplos comuns são primos absurdamente grandes. Há um erro na conta se chegar com esse número até aqui.
    
    return fracao_resultante

def reduz_fracao(fracao: str) -> str:
    """Simplifica frações. É uma função recursiva, tome cuidado onde implementar."""
    partes = fracao.split('/')   
    numerador = int(float(partes[0]))
    if numerador == '0':
        return '0'
    denominador = int(float(partes[1]))

    negativo = False
    if numerador<0:
        negativo = True
        numerador *= -1

    comuns = multiplos_comuns([numerador, denominador])
    if comuns:
        for divisor in comuns:
            numerador //= divisor
            denominador //= divisor
        if negativo:
            return reduz_fracao(f"-{numerador}/{denominador}")
        else:
            return reduz_fracao(f"{numerador}/{denominador}")
    else:
        if denominador==1:
            if negativo:
                return f"-{numerador}"
            else:
                return f"{numerador}"
        else:
            if negativo:
                return f"-{numerador}/{denominador}"
            else:
                return f"{numerador}/{denominador}"        