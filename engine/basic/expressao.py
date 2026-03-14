from engine.basic import operacoes_basicas as basic_operations
from engine.basic import numeros as numbers

# Ordem de prioridade na representação: Racional > Exponencial > Raiz > Logaritmo
ORDEM_TIPOS = {'racional': 0, 'exponencial': 1, 'raiz': 2, 'logaritmo': 3}


class Expressao:
    """Representa uma soma de termos heterogêneos (ex: 3 + √2 + log₃(5))."""

    def __init__(self, termos=None, items=None):
        if items is not None:
            termos = items
        self.termos = termos or []
        self.tipo_de_numero = 'expressao'

    def organizar(self):
        """Ordena termos por prioridade: Racional > Exponencial > Raiz > Logaritmo."""
        self.termos.sort(key=lambda t: ORDEM_TIPOS.get(t.tipo_de_numero, 99))
        return self

    def simplificar(self):
        """Agrupa termos semelhantes na expressão."""
        novos = []
        for termo in self.termos:
            termo_simpl = termo.simplificar() if hasattr(termo, 'simplificar') else termo
            agrupado = False
            for i, existente in enumerate(novos):
                resultado = _tentar_somar(existente, termo_simpl)
                if resultado is not None:
                    novos[i] = resultado
                    agrupado = True
                    break
            if not agrupado:
                novos.append(termo_simpl)

        # Remover zeros
        novos = [t for t in novos if not _eh_zero(t)]

        if len(novos) == 0:
            return numbers.Racional('0')
        elif len(novos) == 1:
            return novos[0]
        else:
            return Expressao(termos=novos)

    def representacao_latex(self):
        self.organizar()
        partes = []
        for i, termo in enumerate(self.termos):
            latex = termo.representacao_latex()
            if i > 0 and not latex.startswith('-'):
                partes.append('+')
            partes.append(latex)
        return ' '.join(partes)

    def __eq__(self, other):
        if not isinstance(other, Expressao):
            return NotImplemented
        return set(id(t) for t in self.termos) == set(id(t) for t in other.termos)

    def __repr__(self):
        return f"Expressao({[t.representacao_latex() for t in self.termos]})"


def _eh_zero(obj):
    """Verifica se um objeto numérico é zero."""
    if obj.tipo_de_numero == 'racional':
        return obj.return_number() == '0'
    return obj.coeficiente == '0'


def _mesma_parte_irracional(a, b):
    """Verifica se dois objetos do mesmo tipo têm a mesma parte irracional."""
    if a.tipo_de_numero != b.tipo_de_numero:
        return False

    tipo = a.tipo_de_numero
    if tipo == 'raiz':
        return a.return_indice() == b.return_indice() and a.return_radicando() == b.return_radicando()
    elif tipo == 'exponencial':
        return a.return_base() == b.return_base() and a.return_expoente() == b.return_expoente()
    elif tipo == 'logaritmo':
        return a.return_base() == b.return_base() and a.return_logaritmando() == b.return_logaritmando()
    elif tipo == 'racional':
        return True
    elif tipo == 'variavel':
        return a.nome == b.nome
    return False


def _tentar_somar(a, b):
    """Tenta somar dois termos se forem do mesmo tipo com mesma parte irracional.
    Retorna o resultado ou None se não for possível simplificar."""
    if not _mesma_parte_irracional(a, b):
        return None

    novo_coef = basic_operations.soma(a.coeficiente, b.coeficiente)

    if novo_coef == '0':
        return numbers.Racional('0')

    tipo = a.tipo_de_numero
    if tipo == 'racional':
        return numbers.Racional(basic_operations.soma(a.return_number(), b.return_number()))
    elif tipo == 'raiz':
        return numbers.Raiz(a.return_indice(), a.return_radicando(), novo_coef)
    elif tipo == 'exponencial':
        return numbers.Exponencial(a.return_base(), a.return_expoente(), novo_coef)
    elif tipo == 'logaritmo':
        return numbers.Logaritmo(a.return_base(), a.return_logaritmando(), novo_coef)
    elif tipo == 'variavel':
        from engine.parser import Variavel
        v = Variavel(a.nome)
        v.coeficiente = novo_coef
        return v
    return None


# ============================================================
# Operações entre dois números quaisquer
# ============================================================

def soma(numero1, numero2):
    """Soma dois objetos numéricos quaisquer (tabela 4×4 completa)."""
    n1 = numero1.simplificar()
    n2 = numero2.simplificar()

    # Se mesma parte irracional, simplifica
    resultado = _tentar_somar(n1, n2)
    if resultado is not None:
        return resultado

    # Tipos diferentes → Expressao
    return Expressao(termos=[n1, n2])


def subtracao(numero1, numero2):
    """Subtrai numero2 de numero1 invertendo o coeficiente."""
    n2 = numero2.simplificar()
    novo_coef = basic_operations.multi('-1', n2.coeficiente)

    tipo = n2.tipo_de_numero
    if tipo == 'racional':
        n2_neg = numbers.Racional(basic_operations.multi('-1', n2.return_number()))
    elif tipo == 'raiz':
        n2_neg = numbers.Raiz(n2.return_indice(), n2.return_radicando(), novo_coef)
    elif tipo == 'exponencial':
        n2_neg = numbers.Exponencial(n2.return_base(), n2.return_expoente(), novo_coef)
    elif tipo == 'logaritmo':
        n2_neg = numbers.Logaritmo(n2.return_base(), n2.return_logaritmando(), novo_coef)
    elif tipo == 'variavel':
        from engine.parser import Variavel
        n2_neg = Variavel(n2.nome)
        n2_neg.coeficiente = novo_coef
    else:
        raise ValueError(f"Tipo desconhecido: {tipo}")

    return soma(numero1, n2_neg)


def multiplicacao(numero1, numero2):
    """Multiplica dois objetos numéricos quaisquer (tabela 4×4 completa)."""
    n1 = numero1.simplificar()
    n2 = numero2.simplificar()

    t1, t2 = n1.tipo_de_numero, n2.tipo_de_numero

    # Racional × Racional
    if t1 == 'racional' and t2 == 'racional':
        return numbers.Racional(basic_operations.multi(n1.return_number(), n2.return_number()))

    # Racional × Irracional (ou vice-versa): modifica coeficiente
    if t1 == 'racional':
        return _racional_vezes_irracional(n1, n2)
    if t2 == 'racional':
        return _racional_vezes_irracional(n2, n1)

    # Exponencial × Exponencial (mesma base): soma expoentes
    if t1 == 'exponencial' and t2 == 'exponencial':
        coef = basic_operations.multi(n1.coeficiente, n2.coeficiente)
        if n1.return_base() == n2.return_base():
            novo_exp = basic_operations.soma(n1.return_expoente(), n2.return_expoente())
            return numbers.Exponencial(n1.return_base(), novo_exp, coef)
        # Bases diferentes: tentar calcular numericamente se possível
        try:
            b1, e1 = int(n1.return_base()), int(n1.return_expoente())
            b2, e2 = int(n2.return_base()), int(n2.return_expoente())
            if b1 > 0 and b2 > 0 and e1 >= 0 and e2 >= 0 and b1**e1 * b2**e2 < 10**15:
                produto = basic_operations.multi(str(b1**e1), str(b2**e2))
                return numbers.Racional(basic_operations.multi(coef, produto))
        except (ValueError, OverflowError):
            pass
        # TODO: manter como Expressao para casos não calculáveis
        return Expressao(termos=[numbers.Exponencial(n1.return_base(), n1.return_expoente(), coef),
                                 numbers.Exponencial(n2.return_base(), n2.return_expoente(), '1')])

    # Raiz × Raiz (mesmo índice): multiplica radicandos
    if t1 == 'raiz' and t2 == 'raiz':
        coef = basic_operations.multi(n1.coeficiente, n2.coeficiente)
        if n1.return_indice() == n2.return_indice():
            novo_rad = basic_operations.multi(n1.return_radicando(), n2.return_radicando())
            resultado = numbers.Raiz(n1.return_indice(), novo_rad, coef)
            return resultado.simplificar()
        return Expressao(termos=[n1, n2])

    # Logaritmo × Logaritmo: não simplifica, retorna expressão com produto
    if t1 == 'logaritmo' and t2 == 'logaritmo':
        coef = basic_operations.multi(n1.coeficiente, n2.coeficiente)
        return Expressao(termos=[n1, n2])

    # Tipos mistos irracionais: multiplica coeficientes, retorna expressão
    coef = basic_operations.multi(n1.coeficiente, n2.coeficiente)
    return Expressao(termos=[
        _com_coeficiente(n1, coef),
        _com_coeficiente(n2, '1')
    ])


def _racional_vezes_irracional(racional, irracional):
    """Multiplica um Racional pelo coeficiente de um Irracional."""
    valor = racional.return_number()
    novo_coef = basic_operations.multi(valor, irracional.coeficiente)

    tipo = irracional.tipo_de_numero
    if tipo == 'raiz':
        return numbers.Raiz(irracional.return_indice(), irracional.return_radicando(), novo_coef)
    elif tipo == 'exponencial':
        return numbers.Exponencial(irracional.return_base(), irracional.return_expoente(), novo_coef)
    elif tipo == 'logaritmo':
        return numbers.Logaritmo(irracional.return_base(), irracional.return_logaritmando(), novo_coef)
    elif tipo == 'variavel':
        from engine.parser import Variavel
        v = Variavel(irracional.nome)
        v.coeficiente = novo_coef
        return v
    raise ValueError(f"Tipo inesperado: {tipo}")


def _com_coeficiente(obj, novo_coef):
    """Retorna uma cópia do objeto com novo coeficiente."""
    tipo = obj.tipo_de_numero
    if tipo == 'racional':
        return numbers.Racional(basic_operations.multi(obj.return_number(), novo_coef))
    elif tipo == 'raiz':
        return numbers.Raiz(obj.return_indice(), obj.return_radicando(), novo_coef)
    elif tipo == 'exponencial':
        return numbers.Exponencial(obj.return_base(), obj.return_expoente(), novo_coef)
    elif tipo == 'logaritmo':
        return numbers.Logaritmo(obj.return_base(), obj.return_logaritmando(), novo_coef)
    elif tipo == 'variavel':
        from engine.parser import Variavel
        v = Variavel(obj.nome)
        v.coeficiente = novo_coef
        return v
    raise ValueError(f"Tipo inesperado: {tipo}")
