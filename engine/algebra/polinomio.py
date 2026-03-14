"""Módulo de Polinômios com aritmética exata via strings."""

from engine.basic.operacoes_basicas import (
    soma, diff, multi, div, reduz_fracao, inteiro,
)


def _normalizar(valor: str) -> str:
    """Normaliza valor numérico: remove '.0' de inteiros, trata frações."""
    if '/' in valor:
        return reduz_fracao(valor)
    return inteiro(valor)


class Polinomio:
    """Polinômio com coeficientes como strings para aritmética exata.

    Representação interna: dict[str, str] onde chave=grau, valor=coeficiente
    Exemplo: 3x² + 2x - 1 → {'2': '3', '1': '2', '0': '-1'}
    """

    def __init__(self, coeficientes: dict, variavel: str = 'x'):
        self.variavel = variavel
        # Normaliza chaves/valores para str e remove coeficientes zero
        self._termos: dict[str, str] = {}
        for grau, coef in coeficientes.items():
            g = str(grau)
            c = _normalizar(str(coef))
            if c != '0':
                self._termos[g] = c
        # Polinômio zero tem pelo menos o termo 0
        if not self._termos:
            self._termos = {'0': '0'}

    def grau(self) -> int:
        """Retorna o maior grau do polinômio."""
        if self._eh_zero():
            return 0
        return max(int(g) for g in self._termos)

    def coeficiente(self, grau) -> str:
        """Retorna o coeficiente do grau informado (ou '0')."""
        return self._termos.get(str(grau), '0')

    def _eh_zero(self) -> bool:
        """Verifica se o polinômio é o polinômio nulo."""
        return all(c == '0' for c in self._termos.values())

    def representacao_latex(self) -> str:
        """Retorna representação LaTeX do polinômio."""
        if self._eh_zero():
            return '0'

        graus = sorted((int(g) for g in self._termos if self._termos[g] != '0'), reverse=True)
        if not graus:
            return '0'

        partes = []
        for i, g in enumerate(graus):
            coef = self._termos[str(g)]
            if coef == '0':
                continue

            # Determina sinal e valor absoluto do coeficiente
            negativo = self._coef_negativo(coef)
            coef_abs = self._coef_abs(coef)

            # Monta o termo
            if g == 0:
                termo = coef_abs
            elif g == 1:
                if coef_abs == '1':
                    termo = self.variavel
                else:
                    termo = f'{coef_abs}{self.variavel}'
            else:
                if coef_abs == '1':
                    termo = f'{self.variavel}^{{{g}}}'
                else:
                    termo = f'{coef_abs}{self.variavel}^{{{g}}}'

            # Monta sinal
            if i == 0:
                if negativo:
                    partes.append(f'-{termo}')
                else:
                    partes.append(termo)
            else:
                if negativo:
                    partes.append(f'- {termo}')
                else:
                    partes.append(f'+ {termo}')

        return ' '.join(partes)

    def _coef_negativo(self, coef: str) -> bool:
        """Verifica se um coeficiente é negativo."""
        if '/' in coef:
            num = coef.split('/')[0]
            return num.startswith('-')
        return coef.startswith('-')

    def _coef_abs(self, coef: str) -> str:
        """Retorna valor absoluto do coeficiente como string."""
        if '/' in coef:
            num, den = coef.split('/')
            num_abs = num.lstrip('-')
            return f'{num_abs}/{den}'
        return coef.lstrip('-')

    def _negar_coef(self, coef: str) -> str:
        """Nega um coeficiente."""
        if coef == '0':
            return '0'
        return multi('-1', coef)

    def avaliar(self, valor: str) -> str:
        """Substitui a variável pelo valor e calcula o resultado."""
        resultado = '0'
        for grau_str, coef in self._termos.items():
            grau_int = int(grau_str)
            # Calcula valor^grau
            potencia = '1'
            for _ in range(grau_int):
                potencia = multi(potencia, valor)
            # Multiplica coeficiente pela potência
            termo = multi(coef, potencia)
            resultado = soma(resultado, termo)
        return resultado

    def somar(self, outro: 'Polinomio') -> 'Polinomio':
        """Soma de polinômios."""
        todos_graus = set(self._termos.keys()) | set(outro._termos.keys())
        novos = {}
        for g in todos_graus:
            c1 = self.coeficiente(g)
            c2 = outro.coeficiente(g)
            s = soma(c1, c2)
            if s != '0':
                novos[g] = s
        return Polinomio(novos, self.variavel)

    def subtrair(self, outro: 'Polinomio') -> 'Polinomio':
        """Subtração de polinômios."""
        todos_graus = set(self._termos.keys()) | set(outro._termos.keys())
        novos = {}
        for g in todos_graus:
            c1 = self.coeficiente(g)
            c2 = outro.coeficiente(g)
            d = diff(c1, c2)
            if d != '0':
                novos[g] = d
        return Polinomio(novos, self.variavel)

    def multiplicar(self, outro: 'Polinomio') -> 'Polinomio':
        """Multiplicação de polinômios (distributiva)."""
        novos: dict[str, str] = {}
        for g1, c1 in self._termos.items():
            for g2, c2 in outro._termos.items():
                grau_novo = str(int(g1) + int(g2))
                prod = multi(c1, c2)
                if grau_novo in novos:
                    novos[grau_novo] = soma(novos[grau_novo], prod)
                else:
                    novos[grau_novo] = prod
        return Polinomio(novos, self.variavel)

    def dividir(self, outro: 'Polinomio') -> tuple:
        """Divisão longa de polinômios. Retorna (quociente, resto)."""
        if outro._eh_zero():
            raise ZeroDivisionError("Divisão por polinômio zero")

        # Se grau do dividendo < grau do divisor, quociente=0, resto=dividendo
        if self.grau() < outro.grau():
            return (Polinomio({'0': '0'}, self.variavel), Polinomio(dict(self._termos), self.variavel))

        resto = Polinomio(dict(self._termos), self.variavel)
        quociente_termos: dict[str, str] = {}

        grau_divisor = outro.grau()
        coef_lider_divisor = outro.coeficiente(grau_divisor)

        while not resto._eh_zero() and resto.grau() >= grau_divisor:
            grau_resto = resto.grau()
            coef_lider_resto = resto.coeficiente(grau_resto)

            # Termo do quociente
            grau_q = str(grau_resto - grau_divisor)
            coef_q = _normalizar(div(coef_lider_resto, coef_lider_divisor))

            if grau_q in quociente_termos:
                quociente_termos[grau_q] = soma(quociente_termos[grau_q], coef_q)
            else:
                quociente_termos[grau_q] = coef_q

            # Subtrai divisor * termo do quociente do resto
            termo_q = Polinomio({grau_q: coef_q}, self.variavel)
            subtrair = outro.multiplicar(termo_q)
            resto = resto.subtrair(subtrair)

        if not quociente_termos:
            quociente_termos = {'0': '0'}

        return (Polinomio(quociente_termos, self.variavel), resto)

    def raizes_racionais(self) -> list:
        """Encontra raízes racionais pelo teorema das raízes racionais (±p/q)."""
        if self._eh_zero():
            return []

        # Coeficiente do termo independente e do líder
        a0 = self.coeficiente('0')
        an = self.coeficiente(str(self.grau()))

        if a0 == '0':
            # 0 é raiz; fatorar x e continuar
            raizes = ['0']
            # Divide por x
            divisor = Polinomio({'1': '1', '0': '0'}, self.variavel)
            quociente, _ = self.dividir(divisor)
            raizes.extend(quociente.raizes_racionais())
            return raizes

        # Divisores do termo independente e do líder
        divs_a0 = self._divisores_inteiro(a0)
        divs_an = self._divisores_inteiro(an)

        candidatos = set()
        for p in divs_a0:
            for q in divs_an:
                frac = reduz_fracao(f'{p}/{q}')
                candidatos.add(frac)
                neg = self._negar_coef(frac)
                candidatos.add(neg)

        raizes = []
        for c in sorted(candidatos):
            val = self.avaliar(c)
            if val == '0':
                raizes.append(c)

        return raizes

    def _divisores_inteiro(self, valor: str) -> list:
        """Retorna divisores positivos de um inteiro (valor absoluto)."""
        if '/' in valor:
            num, den = valor.split('/')
            divs_num = self._divisores_inteiro(num)
            divs_den = self._divisores_inteiro(den)
            resultado = set()
            for p in divs_num:
                for q in divs_den:
                    resultado.add(reduz_fracao(f'{p}/{q}'))
            return sorted(resultado)

        n = abs(int(float(valor)))
        if n == 0:
            return ['1']
        divs = []
        for i in range(1, n + 1):
            if n % i == 0:
                divs.append(str(i))
        return divs

    def fatorar(self) -> list:
        """Fatoração do polinômio.

        Para grau 2: usa Bhaskara (discriminante).
        Para grau 3+: usa raízes racionais + divisão sintética.
        Retorna lista de fatores (Polinomio ou strings para raízes irracionais).
        """
        if self.grau() <= 1:
            return [Polinomio(dict(self._termos), self.variavel)]

        if self.grau() == 2:
            return self._fatorar_grau2()

        return self._fatorar_grau_superior()

    def _fatorar_grau2(self) -> list:
        """Fatoração de polinômio de grau 2 via Bhaskara."""
        a = self.coeficiente('2')
        b = self.coeficiente('1')
        c = self.coeficiente('0')

        # delta = b² - 4ac
        b2 = multi(b, b)
        qac = multi('4', multi(a, c))
        delta = diff(b2, qac)

        delta_float = self._para_float(delta)

        if delta_float < 0:
            # Sem raízes reais -> irredutível
            return [Polinomio(dict(self._termos), self.variavel)]

        if delta_float == 0:
            # Raiz dupla: -b/(2a)
            r = div(self._negar_coef(b), multi('2', a))
            fator = Polinomio({'1': '1', '0': self._negar_coef(r)}, self.variavel)
            fatores = [fator, fator]
            if a != '1':
                fatores.insert(0, Polinomio({'0': a}, self.variavel))
            return fatores

        # Duas raízes: tenta raízes racionais primeiro
        import math
        sqrt_delta = math.isqrt(int(delta_float)) if delta_float == int(delta_float) else None
        if sqrt_delta is not None and sqrt_delta * sqrt_delta == int(delta_float):
            sqrt_d = str(sqrt_delta)
            neg_b = self._negar_coef(b)
            dois_a = multi('2', a)
            r1 = div(soma(neg_b, sqrt_d), dois_a)
            r2 = div(diff(neg_b, sqrt_d), dois_a)
            f1 = Polinomio({'1': '1', '0': self._negar_coef(r1)}, self.variavel)
            f2 = Polinomio({'1': '1', '0': self._negar_coef(r2)}, self.variavel)
            fatores = [f1, f2]
            if a != '1':
                fatores.insert(0, Polinomio({'0': a}, self.variavel))
            return fatores

        # Discriminante não é quadrado perfeito -> irredutível sobre racionais
        return [Polinomio(dict(self._termos), self.variavel)]

    def _fatorar_grau_superior(self) -> list:
        """Fatoração de grau 3+ via raízes racionais + divisão."""
        raizes = self.raizes_racionais()
        if not raizes:
            return [Polinomio(dict(self._termos), self.variavel)]

        fatores = []
        resto = Polinomio(dict(self._termos), self.variavel)

        for r in raizes:
            # Fator (x - r)
            fator = Polinomio({'1': '1', '0': self._negar_coef(r)}, self.variavel)
            quociente, rem = resto.dividir(fator)
            if rem._eh_zero():
                fatores.append(fator)
                resto = quociente

        # Fatora o resto se possível
        if not resto._eh_zero() and resto.grau() >= 2:
            fatores.extend(resto.fatorar())
        elif not resto._eh_zero() and not (resto.grau() == 0 and resto.coeficiente('0') == '1'):
            fatores.append(resto)

        return fatores

    def _para_float(self, valor: str) -> float:
        """Converte string (possivelmente fração) para float."""
        if '/' in valor:
            num, den = valor.split('/')
            return float(num) / float(den)
        return float(valor)

    def __eq__(self, outro) -> bool:
        if not isinstance(outro, Polinomio):
            return False
        # Normaliza: ambos devem ter os mesmos termos não-zero
        g1 = {g: c for g, c in self._termos.items() if c != '0'}
        g2 = {g: c for g, c in outro._termos.items() if c != '0'}
        if not g1 and not g2:
            return True
        return g1 == g2

    def __repr__(self) -> str:
        return f'Polinomio({self._termos}, variavel={self.variavel!r})'
