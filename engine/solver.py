"""Solver: resolve expressões e captura passos de resolução.

Fluxo: texto → parse → simplificar → registrar passos → resultado
"""

from engine.parser import parsear
from engine.basic.passo import Passo, Historico
from engine.basic.numeros import Racional, Raiz, Exponencial, Logaritmo, simplificar
from engine.basic.expressao import Expressao


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
            regra='parse'
        ))

        # Passo 2: Simplificar
        if hasattr(objeto, 'simplificar'):
            resultado = objeto.simplificar()
        else:
            resultado = objeto

        latex_resultado = resultado.representacao_latex() if hasattr(resultado, 'representacao_latex') else str(resultado)

        # Registrar passos de simplificação baseado no tipo
        self._registrar_passos_simplificacao(objeto, resultado, historico)

        # Calcular valor numérico
        valor_numerico = self._calcular_valor_numerico(resultado)

        if latex_entrada != latex_resultado:
            historico.adicionar(Passo(
                nivel=1,
                descricao='Resultado simplificado',
                latex_antes=latex_entrada,
                latex_depois=latex_resultado,
                regra='simplificacao'
            ))

        return ResultadoCalculo(
            entrada=entrada,
            resultado=resultado,
            historico=historico,
            latex_entrada=latex_entrada,
            valor_numerico=valor_numerico,
        )

    def _registrar_passos_simplificacao(self, original, resultado, historico):
        """Registra passos detalhados da simplificação."""
        tipo = original.tipo_de_numero if hasattr(original, 'tipo_de_numero') else 'desconhecido'

        if tipo == 'raiz':
            latex_orig = original.representacao_latex()
            latex_res = resultado.representacao_latex()
            if latex_orig != latex_res:
                historico.adicionar(Passo(
                    nivel=2,
                    descricao='Fatorar radicando e extrair fatores do radical',
                    latex_antes=latex_orig,
                    latex_depois=latex_res,
                    regra='simplificacao_raiz'
                ))

        elif tipo == 'exponencial':
            latex_orig = original.representacao_latex()
            latex_res = resultado.representacao_latex()
            if latex_orig != latex_res:
                historico.adicionar(Passo(
                    nivel=2,
                    descricao='Simplificar base da exponencial',
                    latex_antes=latex_orig,
                    latex_depois=latex_res,
                    regra='simplificacao_exponencial'
                ))

        elif tipo == 'logaritmo':
            latex_orig = original.representacao_latex()
            latex_res = resultado.representacao_latex()
            if latex_orig != latex_res:
                historico.adicionar(Passo(
                    nivel=2,
                    descricao='Aplicar propriedades do logaritmo',
                    latex_antes=latex_orig,
                    latex_depois=latex_res,
                    regra='simplificacao_logaritmo'
                ))

        elif tipo == 'racional':
            latex_orig = original.representacao_latex()
            latex_res = resultado.representacao_latex()
            if latex_orig != latex_res:
                historico.adicionar(Passo(
                    nivel=2,
                    descricao='Simplificar fração',
                    latex_antes=latex_orig,
                    latex_depois=latex_res,
                    regra='simplificacao_fracao'
                ))

        elif tipo == 'expressao':
            latex_orig = original.representacao_latex()
            latex_res = resultado.representacao_latex()
            if latex_orig != latex_res:
                historico.adicionar(Passo(
                    nivel=2,
                    descricao='Agrupar termos semelhantes',
                    latex_antes=latex_orig,
                    latex_depois=latex_res,
                    regra='agrupamento'
                ))

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
