"""Módulo de equações de 1º e 2º grau com resolução passo-a-passo."""

from engine.basic.operacoes_basicas import soma, diff, multi, reduz_fracao
from engine.basic.numeros import Racional, Raiz, frac_latex
from engine.basic.passo import Passo, Historico


def _para_float(s) -> float:
    """Converte string para float, tratando frações como '1/3'."""
    s = str(s)
    if '/' in s:
        partes = s.split('/')
        return float(partes[0]) / float(partes[1])
    return float(s)


def _dividir_como_fracao(numerador: str, denominador: str) -> str:
    """Divide dois valores retornando fração simplificada (nunca decimal)."""
    return reduz_fracao(f'{numerador}/{denominador}')


class Equacao1Grau:
    """Resolve equações do tipo ax + b = 0, onde a e b são strings numéricas."""

    def __init__(self, a: str, b: str):
        self.a = a
        self.b = b

    def representacao_latex(self) -> str:
        """Retorna a representação LaTeX da equação ax + b = 0."""
        partes = []
        if self.a == '1':
            partes.append('x')
        elif self.a == '-1':
            partes.append('-x')
        else:
            partes.append(f'{self.a}x')

        if self.b != '0':
            b_val = _para_float(self.b)
            if b_val > 0:
                partes.append(f' + {self.b}')
            else:
                b_abs = self.b[1:] if self.b.startswith('-') else self.b
                partes.append(f' - {b_abs}')

        return ''.join(partes) + ' = 0'

    def resolver(self) -> tuple:
        """Resolve ax + b = 0 e retorna (solucao, historico).

        A solução é um objeto Racional com representacao_latex().
        O histórico contém os passos da resolução.
        """
        historico = Historico(verbosidade=3)

        if self.a == '0':
            raise ValueError(
                "O coeficiente 'a' não pode ser zero em uma equação de 1º grau. "
                "Se a = 0, a equação se reduz a b = 0, que não depende de x."
            )

        # Passo 1: Identificar a equação
        latex_eq = self.representacao_latex()
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Equação de 1º grau: {latex_eq}',
            latex_antes=latex_eq,
            latex_depois=latex_eq,
            regra='Identificação',
            justificativa='Reconhecer o tipo de equação para aplicar o método correto.',
            metodo='Equação linear: ax + b = 0'
        ))

        # Passo 2: Isolar o termo com x: ax = -b
        neg_b = multi('-1', self.b)
        latex_isolado = f'{self.a}x = {neg_b}'
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Isolar o termo com x: {latex_isolado}',
            latex_antes=latex_eq,
            latex_depois=latex_isolado,
            regra='Transposição de termos',
            justificativa='Mover o termo constante para o outro lado da equação, trocando o sinal.',
            metodo='Subtrair b de ambos os lados: ax = -b'
        ))

        # Passo 3: Dividir ambos os lados por a
        resultado_str = _dividir_como_fracao(neg_b, self.a)
        latex_divisao = f'x = {frac_latex(neg_b, self.a)}'
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Dividir ambos os lados por {self.a}',
            latex_antes=latex_isolado,
            latex_depois=latex_divisao,
            regra='Divisão por coeficiente',
            justificativa=f'Dividir por a = {self.a} para isolar x.',
            metodo=f'x = -b/a = {neg_b}/{self.a}'
        ))

        # Passo 4: Simplificar resultado
        solucao = Racional(resultado_str)

        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Simplificar: x = {solucao.representacao_latex()}',
            latex_antes=latex_divisao,
            latex_depois=f'x = {solucao.representacao_latex()}',
            regra='Simplificação de fração',
            justificativa='Reduzir a fração ao menor termo possível.',
            metodo=f'x = {solucao.representacao_latex()}'
        ))

        return (solucao, historico)


class Equacao2Grau:
    """Resolve equações do tipo ax² + bx + c = 0 via fórmula de Bhaskara."""

    def __init__(self, a: str, b: str, c: str):
        self.a = a
        self.b = b
        self.c = c

    def representacao_latex(self) -> str:
        """Retorna a representação LaTeX da equação ax² + bx + c = 0."""
        partes = []

        # Termo ax²
        if self.a == '1':
            partes.append('x^{2}')
        elif self.a == '-1':
            partes.append('-x^{2}')
        else:
            partes.append(f'{self.a}x^{{2}}')

        # Termo bx
        if self.b != '0':
            b_val = _para_float(self.b)
            if b_val > 0:
                if self.b == '1':
                    partes.append(' + x')
                else:
                    partes.append(f' + {self.b}x')
            else:
                if self.b == '-1':
                    partes.append(' - x')
                else:
                    b_abs = self.b[1:] if self.b.startswith('-') else self.b
                    partes.append(f' - {b_abs}x')

        # Termo c
        if self.c != '0':
            c_val = _para_float(self.c)
            if c_val > 0:
                partes.append(f' + {self.c}')
            else:
                c_abs = self.c[1:] if self.c.startswith('-') else self.c
                partes.append(f' - {c_abs}')

        return ''.join(partes) + ' = 0'

    def resolver(self) -> tuple:
        """Resolve ax² + bx + c = 0 e retorna (solucoes, historico).

        As soluções são objetos Racional ou Raiz com representacao_latex().
        O histórico contém os passos da resolução com Bhaskara.
        Levanta ValueError se o discriminante for negativo.
        """
        historico = Historico(verbosidade=3)

        if self.a == '0':
            raise ValueError(
                "O coeficiente 'a' não pode ser zero em uma equação de 2º grau. "
                "Se a = 0, use Equacao1Grau."
            )

        # Passo 1: Identificar coeficientes
        latex_eq = self.representacao_latex()
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Equação de 2º grau: {latex_eq}',
            latex_antes=latex_eq,
            latex_depois=f'a = {self.a}, b = {self.b}, c = {self.c}',
            regra='Identificação de coeficientes',
            justificativa='Identificar a, b e c para aplicar a fórmula de Bhaskara.',
            metodo='Comparar com a forma geral ax² + bx + c = 0'
        ))

        # Passo 2: Calcular discriminante Δ = b² - 4ac
        b_quadrado = multi(self.b, self.b)
        quatro_ac = multi('4', multi(self.a, self.c))
        delta = diff(b_quadrado, quatro_ac)

        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Calcular o discriminante: Δ = b² - 4ac = {b_quadrado} - {quatro_ac} = {delta}',
            latex_antes='\\Delta = b^{2} - 4ac',
            latex_depois=f'\\Delta = {delta}',
            regra='Fórmula do discriminante',
            justificativa='O discriminante determina a natureza das raízes.',
            metodo=f'Δ = ({self.b})² - 4·({self.a})·({self.c}) = {b_quadrado} - {quatro_ac} = {delta}'
        ))

        delta_float = _para_float(delta)

        # Passo 3: Analisar discriminante
        if delta_float < 0:
            historico.adicionar(Passo(
                nivel=1,
                descricao=f'Δ = {delta} < 0: não existem raízes reais.',
                latex_antes=f'\\Delta = {delta}',
                latex_depois='\\nexists \\; x \\in \\mathbb{{R}}',
                regra='Análise do discriminante',
                justificativa='Quando Δ < 0, a parábola não intercepta o eixo x.',
                metodo='Discriminante negativo implica raízes complexas.'
            ))
            raise ValueError(
                f"Discriminante negativo (Δ = {delta}). "
                "A equação não possui raízes reais. "
                "Isso significa que a parábola não toca o eixo x."
            )

        neg_b = multi('-1', self.b)
        dois_a = multi('2', self.a)

        if delta_float == 0:
            # Raiz dupla: x = -b / (2a)
            historico.adicionar(Passo(
                nivel=1,
                descricao='Δ = 0: raiz dupla.',
                latex_antes=f'\\Delta = 0',
                latex_depois=f'x = {frac_latex("-b", "2a")}',
                regra='Raiz dupla (Δ = 0)',
                justificativa='Quando Δ = 0, as duas raízes são iguais.',
                metodo='x = -b/(2a)'
            ))

            resultado_str = _dividir_como_fracao(neg_b, dois_a)
            solucao = Racional(resultado_str)

            historico.adicionar(Passo(
                nivel=2,
                descricao=f'x = {neg_b} / {dois_a} = {solucao.representacao_latex()}',
                latex_antes=f'x = {frac_latex(neg_b, dois_a)}',
                latex_depois=f'x = {solucao.representacao_latex()}',
                regra='Simplificação',
                justificativa='Calcular e simplificar a raiz dupla.',
                metodo=f'x = {neg_b}/{dois_a} = {solucao.representacao_latex()}'
            ))

            return ([solucao], historico)

        else:
            # Δ > 0: duas raízes distintas
            historico.adicionar(Passo(
                nivel=1,
                descricao=f'Δ = {delta} > 0: duas raízes reais distintas.',
                latex_antes=f'\\Delta = {delta}',
                latex_depois=f'x = {frac_latex("-b \\pm \\sqrt{\\Delta}", "2a")}',
                regra='Fórmula de Bhaskara',
                justificativa='Quando Δ > 0, existem duas raízes reais distintas.',
                metodo='x = (-b ± √Δ) / (2a)'
            ))

            # Verificar se √Δ é inteiro
            import math
            delta_int = int(delta)
            raiz_delta = math.isqrt(abs(delta_int))
            delta_eh_quadrado_perfeito = (raiz_delta * raiz_delta == delta_int)

            if delta_eh_quadrado_perfeito:
                raiz_delta_str = str(raiz_delta)

                # x1 = (-b + √Δ) / (2a)
                numerador1 = soma(neg_b, raiz_delta_str)
                x1_str = _dividir_como_fracao(numerador1, dois_a)
                x1 = Racional(x1_str)

                # x2 = (-b - √Δ) / (2a)
                numerador2 = diff(neg_b, raiz_delta_str)
                x2_str = _dividir_como_fracao(numerador2, dois_a)
                x2 = Racional(x2_str)

                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'√Δ = {raiz_delta_str}',
                    latex_antes=f'\\sqrt{{\\Delta}} = \\sqrt{{{delta}}}',
                    latex_depois=f'\\sqrt{{\\Delta}} = {raiz_delta_str}',
                    regra='Raiz quadrada exata',
                    justificativa=f'{delta} é quadrado perfeito.',
                    metodo=f'√{delta} = {raiz_delta_str}'
                ))

                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'x₁ = ({neg_b} + {raiz_delta_str}) / {dois_a} = {x1.representacao_latex()}',
                    latex_antes=f'x_1 = {frac_latex(neg_b + " + " + raiz_delta_str, dois_a)}',
                    latex_depois=f'x_1 = {x1.representacao_latex()}',
                    regra='Cálculo de x₁',
                    justificativa='Aplicar a fórmula com o sinal positivo.',
                    metodo=f'x₁ = ({neg_b} + {raiz_delta_str}) / {dois_a} = {numerador1}/{dois_a}'
                ))

                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'x₂ = ({neg_b} - {raiz_delta_str}) / {dois_a} = {x2.representacao_latex()}',
                    latex_antes=f'x_2 = {frac_latex(neg_b + " - " + raiz_delta_str, dois_a)}',
                    latex_depois=f'x_2 = {x2.representacao_latex()}',
                    regra='Cálculo de x₂',
                    justificativa='Aplicar a fórmula com o sinal negativo.',
                    metodo=f'x₂ = ({neg_b} - {raiz_delta_str}) / {dois_a} = {numerador2}/{dois_a}'
                ))

                return ([x1, x2], historico)

            else:
                # Δ não é quadrado perfeito: resultado com raiz simbólica
                # Simplificar √Δ: extrair fatores quadrados
                raiz_delta_obj = Raiz('2', delta, '1').simplificar()

                if isinstance(raiz_delta_obj, Racional):
                    # Simplificou para racional (improvável aqui, mas por segurança)
                    raiz_delta_str = raiz_delta_obj.return_number()
                    numerador1 = soma(neg_b, raiz_delta_str)
                    x1 = Racional(_dividir_como_fracao(numerador1, dois_a))

                    numerador2 = diff(neg_b, raiz_delta_str)
                    x2 = Racional(_dividir_como_fracao(numerador2, dois_a))

                    return ([x1, x2], historico)

                # Resultado simbólico: (-b ± coef·√rad) / (2a)
                coef_raiz = raiz_delta_obj.coeficiente
                radicando = raiz_delta_obj.radicando

                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'Simplificar √Δ = {raiz_delta_obj.representacao_latex()}',
                    latex_antes=f'\\sqrt{{{delta}}}',
                    latex_depois=raiz_delta_obj.representacao_latex(),
                    regra='Simplificação de radical',
                    justificativa='Extrair fatores quadrados perfeitos do radicando.',
                    metodo=f'√{delta} = {raiz_delta_obj.representacao_latex()}'
                ))

                # Tentar simplificar dividindo numerador e denominador
                # x = (-b ± coef·√rad) / (2a)
                # Se mdc(neg_b, coef, 2a) > 1, podemos simplificar
                from math import gcd
                neg_b_int = int(neg_b)
                coef_int = int(coef_raiz)
                dois_a_int = int(dois_a)

                d = gcd(gcd(abs(neg_b_int), abs(coef_int)), abs(dois_a_int))

                neg_b_simp = str(neg_b_int // d)
                coef_simp = str(coef_int // d)
                dois_a_simp = str(dois_a_int // d)

                if dois_a_simp == '1':
                    # x1 = neg_b_simp + coef_simp·√rad
                    x1 = _construir_solucao_com_raiz(neg_b_simp, coef_simp, radicando, positivo=True)
                    x2 = _construir_solucao_com_raiz(neg_b_simp, coef_simp, radicando, positivo=False)
                elif dois_a_simp == '-1':
                    neg_b_simp = str(-int(neg_b_simp))
                    coef_simp = str(-int(coef_simp))
                    x1 = _construir_solucao_com_raiz(neg_b_simp, coef_simp, radicando, positivo=True)
                    x2 = _construir_solucao_com_raiz(neg_b_simp, coef_simp, radicando, positivo=False)
                else:
                    # Manter na forma fracionária
                    x1_latex = frac_latex(f'{neg_b_simp} + {_raiz_latex_inline(coef_simp, radicando)}', dois_a_simp)
                    x2_latex = frac_latex(f'{neg_b_simp} - {_raiz_latex_inline(coef_simp, radicando)}', dois_a_simp)

                    x1 = _SolucaoSimbolica(x1_latex)
                    x2 = _SolucaoSimbolica(x2_latex)

                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'x₁ = {x1.representacao_latex()}, x₂ = {x2.representacao_latex()}',
                    latex_antes=f'x = {frac_latex("-b \\pm \\sqrt{\\Delta}", "2a")}',
                    latex_depois=f'x_1 = {x1.representacao_latex()}, \\; x_2 = {x2.representacao_latex()}',
                    regra='Cálculo das raízes',
                    justificativa='Substituir valores e simplificar.',
                    metodo='Aplicar fórmula de Bhaskara com √Δ simplificada.'
                ))

                return ([x1, x2], historico)


class _SolucaoSimbolica:
    """Wrapper para soluções que não se reduzem a Racional puro."""

    def __init__(self, latex: str):
        self._latex = latex

    def representacao_latex(self) -> str:
        return self._latex


def _raiz_latex_inline(coeficiente: str, radicando: str) -> str:
    """Gera representação inline de coeficiente·√radicando."""
    if coeficiente == '1':
        return f'\\sqrt{{{radicando}}}'
    elif coeficiente == '-1':
        return f'-\\sqrt{{{radicando}}}'
    else:
        return f'{coeficiente}\\sqrt{{{radicando}}}'


def _construir_solucao_com_raiz(parte_racional: str, coef_raiz: str, radicando: str, positivo: bool):
    """Constrói uma solução simbólica com parte racional ± coef·√radicando."""
    sinal = '+' if positivo else '-'
    raiz_parte = _raiz_latex_inline(coef_raiz, radicando)

    if parte_racional == '0':
        if positivo:
            latex = raiz_parte
        else:
            # Inverter sinal do coeficiente
            coef_neg = str(-int(coef_raiz))
            latex = _raiz_latex_inline(coef_neg, radicando)
    else:
        latex = f'{parte_racional} {sinal} {raiz_parte}'

    return _SolucaoSimbolica(latex)
