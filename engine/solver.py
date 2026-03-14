"""Solver: resolve expressões e captura passos de resolução.

Fluxo: texto → parse → simplificar → registrar passos → resultado
"""

from engine.parser import parsear
from engine.basic.passo import Passo, Historico
from engine.basic.numeros import (
    Racional, Raiz, Exponencial, Logaritmo,
    simplificar, number_to_potencia
)
from engine.basic.expressao import Expressao
from engine.basic import operacoes_basicas as ops


class ResultadoCalculo:
    """Resultado completo de um cálculo."""

    def __init__(self, entrada, resultado, historico, latex_entrada='', valor_numerico=''):
        self.entrada = entrada
        self.resultado = resultado
        self.historico = historico
        self.latex_entrada = latex_entrada
        self.latex_resultado = resultado.representacao_latex() if hasattr(resultado, 'representacao_latex') else str(resultado)
        self.valor_numerico = valor_numerico

    def serializar(self):
        return {
            'entrada': self.entrada,
            'latex_entrada': self.latex_entrada,
            'latex_resultado': self.latex_resultado,
            'valor_numerico': self.valor_numerico,
            'passos': self.historico.serializar(),
        }


class Solver:
    """Resolve expressões matemáticas com passo-a-passo."""

    def __init__(self, verbosidade=3):
        self.verbosidade = verbosidade

    def resolver(self, entrada):
        """Resolve uma expressão textual e retorna ResultadoCalculo."""
        historico = Historico(verbosidade=self.verbosidade)

        # Passo 1: Parse
        objeto = parsear(entrada)
        latex_entrada = objeto.representacao_latex() if hasattr(objeto, 'representacao_latex') else entrada

        historico.adicionar(Passo(
            nivel=1,
            descricao='Interpretar expressão',
            latex_antes=entrada,
            latex_depois=latex_entrada,
            regra='parse',
            justificativa='Converter a entrada de texto para representação matemática',
            metodo='Parser descendente recursivo analisa a expressão e identifica os componentes'
        ))

        # Passo 2: Simplificar com passos detalhados
        resultado = self._simplificar_com_passos(objeto, historico)

        latex_resultado = resultado.representacao_latex() if hasattr(resultado, 'representacao_latex') else str(resultado)

        # Calcular valor numérico
        valor_numerico = self._calcular_valor_numerico(resultado)

        if latex_entrada != latex_resultado:
            historico.adicionar(Passo(
                nivel=0,
                descricao='Resultado final',
                latex_antes=latex_entrada,
                latex_depois=latex_resultado,
                regra='resultado',
                justificativa='Expressão simplificada ao máximo',
                metodo=f'Valor numérico aproximado: {valor_numerico}' if valor_numerico else ''
            ))

        return ResultadoCalculo(
            entrada=entrada,
            resultado=resultado,
            historico=historico,
            latex_entrada=latex_entrada,
            valor_numerico=valor_numerico,
        )

    def _simplificar_com_passos(self, objeto, historico):
        """Simplifica um objeto e registra passos detalhados."""
        tipo = objeto.tipo_de_numero if hasattr(objeto, 'tipo_de_numero') else 'desconhecido'

        if tipo == 'raiz':
            return self._simplificar_raiz(objeto, historico)
        elif tipo == 'exponencial':
            return self._simplificar_exponencial(objeto, historico)
        elif tipo == 'logaritmo':
            return self._simplificar_logaritmo(objeto, historico)
        elif tipo == 'racional':
            return self._simplificar_racional(objeto, historico)
        elif tipo == 'expressao':
            return self._simplificar_expressao(objeto, historico)

        return objeto

    def _simplificar_raiz(self, raiz, historico):
        """Simplifica uma raiz com passos pedagógicos."""
        radicando = raiz.return_radicando()
        indice = raiz.return_indice()
        latex_original = raiz.representacao_latex()

        if radicando in ('0', '1'):
            resultado = simplificar(raiz)
            historico.adicionar(Passo(
                nivel=1,
                descricao=f'Radicando é {radicando} — resultado trivial',
                latex_antes=latex_original,
                latex_depois=resultado.representacao_latex(),
                regra='raiz_trivial',
                justificativa=f'√({radicando}) = {radicando} para qualquer índice',
                metodo='Caso base da definição de raiz'
            ))
            return resultado

        # Passo: Fatorar o radicando
        fatores = number_to_potencia(radicando)
        if fatores:
            fatoracao_str = ' \\cdot '.join(
                f'{b}^{{{e}}}' if e != '1' else b
                for b, e in fatores.items()
            )
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Fatorar o radicando {radicando}',
                latex_antes=latex_original,
                latex_depois=f'\\sqrt{{{indice}}}{{{fatoracao_str}}}',
                regra='fatoracao_prima',
                justificativa='Decompor em fatores primos permite identificar o que sai da raiz',
                metodo=f'{radicando} = {fatoracao_str}'
            ))

            # Passo: Detalhar cada fator
            for base, expoente in fatores.items():
                exp_int = int(expoente)
                idx_int = int(indice)
                if exp_int >= idx_int:
                    sai = exp_int // idx_int
                    resta = exp_int % idx_int
                    historico.adicionar(Passo(
                        nivel=3,
                        descricao=f'Extrair {base} da raiz',
                        latex_antes=f'{base}^{{{expoente}}}',
                        latex_depois=f'{base}^{{{sai}}} sai, {base}^{{{resta}}} fica' if resta > 0 else f'{base}^{{{sai}}} sai inteiro',
                        regra='extracao_fator',
                        justificativa=f'Expoente {expoente} ÷ índice {indice} = {sai} (inteiro) + {resta} (resto)',
                        metodo=f'Se expoente ≥ índice, o fator sai da raiz elevado a expoente÷índice'
                    ))

        resultado = simplificar(raiz)
        latex_resultado = resultado.representacao_latex()

        if latex_original != latex_resultado:
            historico.adicionar(Passo(
                nivel=1,
                descricao='Resultado da simplificação da raiz',
                latex_antes=latex_original,
                latex_depois=latex_resultado,
                regra='simplificacao_raiz',
                justificativa='Fatores extraídos do radical formam o coeficiente',
                metodo='Multiplica-se os fatores que saíram para obter o coeficiente'
            ))

        return resultado

    def _simplificar_exponencial(self, exp, historico):
        """Simplifica uma exponencial com passos pedagógicos."""
        base = exp.return_base()
        expoente = exp.return_expoente()
        latex_original = exp.representacao_latex()

        if base in ('0', '1') or expoente == '0':
            resultado = simplificar(exp)
            caso = 'base 0 → 0' if base == '0' else 'base 1 → 1' if base == '1' else 'expoente 0 → 1'
            historico.adicionar(Passo(
                nivel=1,
                descricao=f'Caso trivial: {caso}',
                latex_antes=latex_original,
                latex_depois=resultado.representacao_latex(),
                regra='exponencial_trivial',
                justificativa=f'Propriedade fundamental da exponenciação',
                metodo=caso
            ))
            return resultado

        fatores = number_to_potencia(base)
        if fatores and '1' not in fatores.values():
            fatoracao_str = ' \\cdot '.join(
                f'{b}^{{{e}}}' if e != '1' else b
                for b, e in fatores.items()
            )
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Fatorar a base {base}',
                latex_antes=latex_original,
                latex_depois=f'({fatoracao_str})^{{{expoente}}}',
                regra='fatoracao_base',
                justificativa='Reduzir a base à menor forma possível',
                metodo=f'{base} = {fatoracao_str}'
            ))

            historico.adicionar(Passo(
                nivel=3,
                descricao='Aplicar propriedade da potência de potência',
                latex_antes=f'({fatoracao_str})^{{{expoente}}}',
                latex_depois='',
                regra='potencia_de_potencia',
                justificativa='(aⁿ)ᵐ = aⁿᵐ — multiplicar expoentes',
                metodo='Multiplicar cada expoente da fatoração pelo expoente externo'
            ))

        resultado = simplificar(exp)
        latex_resultado = resultado.representacao_latex()

        if latex_original != latex_resultado:
            historico.adicionar(Passo(
                nivel=1,
                descricao='Resultado da simplificação da exponencial',
                latex_antes=latex_original,
                latex_depois=latex_resultado,
                regra='simplificacao_exponencial',
                justificativa='Base reduzida e expoente recalculado',
                metodo='Nova base × novo expoente'
            ))

        return resultado

    def _simplificar_logaritmo(self, log, historico):
        """Simplifica um logaritmo com passos pedagógicos."""
        base = log.return_base()
        logaritmando = log.return_logaritmando()
        latex_original = log.representacao_latex()

        if logaritmando == '1':
            resultado = simplificar(log)
            historico.adicionar(Passo(
                nivel=1,
                descricao='Logaritmo de 1 é sempre 0',
                latex_antes=latex_original,
                latex_depois='0',
                regra='log_de_um',
                justificativa='b⁰ = 1, portanto log_b(1) = 0 para qualquer base b',
                metodo='Propriedade fundamental do logaritmo'
            ))
            return resultado

        if logaritmando == base:
            resultado = simplificar(log)
            historico.adicionar(Passo(
                nivel=1,
                descricao='Logaritmo da base é sempre 1',
                latex_antes=latex_original,
                latex_depois='1',
                regra='log_da_base',
                justificativa=f'b¹ = b, portanto log_{base}({base}) = 1',
                metodo='Propriedade fundamental do logaritmo'
            ))
            return resultado

        fatores = number_to_potencia(logaritmando)
        if fatores and '1' not in fatores.values():
            minimo = min(fatores.values())
            if minimo != '1':
                fatoracao_str = ' \\cdot '.join(
                    f'{b}^{{{e}}}' if e != '1' else b
                    for b, e in fatores.items()
                )
                historico.adicionar(Passo(
                    nivel=2,
                    descricao=f'Fatorar o logaritmando {logaritmando}',
                    latex_antes=latex_original,
                    latex_depois=f'\\log_{{{base}}}{{{fatoracao_str}}}',
                    regra='fatoracao_logaritmando',
                    justificativa='Identificar potências comuns que podem virar coeficiente',
                    metodo=f'{logaritmando} = {fatoracao_str}'
                ))

                historico.adicionar(Passo(
                    nivel=3,
                    descricao='Aplicar propriedade do expoente no logaritmo',
                    latex_antes=f'\\log_{{{base}}}(x^n)',
                    latex_depois=f'n \\cdot \\log_{{{base}}}(x)',
                    regra='log_potencia',
                    justificativa='log_b(xⁿ) = n·log_b(x) — o expoente vira coeficiente',
                    metodo=f'Extrair expoente mínimo {minimo} como coeficiente'
                ))

        resultado = simplificar(log)
        latex_resultado = resultado.representacao_latex()

        if latex_original != latex_resultado:
            historico.adicionar(Passo(
                nivel=1,
                descricao='Resultado da simplificação do logaritmo',
                latex_antes=latex_original,
                latex_depois=latex_resultado,
                regra='simplificacao_logaritmo',
                justificativa='Expoente comum extraído como coeficiente',
                metodo='Coeficiente × log_b(logaritmando reduzido)'
            ))

        return resultado

    def _simplificar_racional(self, racional, historico):
        """Simplifica um racional com passos."""
        latex_original = racional.representacao_latex()
        resultado = simplificar(racional)
        latex_resultado = resultado.representacao_latex()

        if latex_original != latex_resultado:
            historico.adicionar(Passo(
                nivel=2,
                descricao='Simplificar fração',
                latex_antes=latex_original,
                latex_depois=latex_resultado,
                regra='simplificacao_fracao',
                justificativa='Dividir numerador e denominador pelo MDC',
                metodo='Encontrar divisores comuns e reduzir'
            ))

        return resultado

    def _simplificar_expressao(self, expr, historico):
        """Simplifica uma expressão com passos."""
        latex_original = expr.representacao_latex()
        resultado = expr.simplificar()
        latex_resultado = resultado.representacao_latex() if hasattr(resultado, 'representacao_latex') else str(resultado)

        if latex_original != latex_resultado:
            historico.adicionar(Passo(
                nivel=2,
                descricao='Agrupar termos semelhantes',
                latex_antes=latex_original,
                latex_depois=latex_resultado,
                regra='agrupamento',
                justificativa='Termos com mesma parte irracional podem ser somados',
                metodo='Somar coeficientes de termos semelhantes'
            ))

        return resultado

    def _calcular_valor_numerico(self, resultado):
        """Calcula o valor numérico aproximado."""
        try:
            if resultado.tipo_de_numero == 'racional':
                val = resultado.numero_real()
                return str(val)
            elif resultado.tipo_de_numero in ('raiz', 'exponencial', 'logaritmo'):
                val = resultado.numero_real()
                return f"{float(val):.10g}"
            elif resultado.tipo_de_numero == 'expressao':
                total = 0.0
                for termo in resultado.termos:
                    val = termo.numero_real()
                    total += float(val)
                return f"{total:.10g}"
        except Exception:
            return ''
        return ''
