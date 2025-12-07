############# Variáveis
primos = '.\\data\\primos.txt'

## Toda a estrutura de decomposição e lógica de padronização de estruturas matemáticas

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

def inteiro(numero):
    ponto = float(numero)
    inteiro = int(ponto)
    if ponto.is_integer():
        return str(inteiro)
    else:
        return numero
    
def simplifica_fracao(fracao: str) -> str:
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
            return simplifica_fracao(f"-{numerador}/{denominador}")
        else:
            return simplifica_fracao(f"{numerador}/{denominador}")
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
        return simplifica_fracao(f"{numerador}/{denominador}")
    
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

    fracao_resultante =  simplifica_fracao(f"{numerador_total}/{denominador_total}")

    numerador, denominador = fracao_resultante.split('/')

    if numerador > 1000000000 or denominador > 1000000000:
        return n  #Quase irracional ou multiplos comuns são primos absurdamente grandes. Há um erro na conta se chegar com esse número até aqui.
    
    return fracao_resultante

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