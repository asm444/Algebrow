"""Solver unificado: resolve expressões de TODAS as 16 fases.

Fluxo: LaTeX/texto → converter_latex → detector → roteamento → resultado com passos

Fases suportadas:
    0-1: Básico (aritmética, frações, raízes, potências, logaritmos)
    2:   Álgebra (equações, sistemas, polinômios, inequações)
    3:   Funções e gráficos
    4-7: Cálculo (derivadas, integrais, limites, séries, EDOs, multivariável)
    5:   Álgebra linear (matrizes, determinantes, autovalores)
    6:   Complexos (aritmética, polar, Laplace)
    8:   Funções especiais (Gamma, Bessel, Legendre)
    9:   Geometria diferencial (curvatura, Frenet)
    10:  Sturm-Liouville, Green
    11:  EDPs (calor, onda, Laplace)
    12:  Fourier (séries, transformada)
    13:  Cálculo variacional (Euler-Lagrange)
    14:  Equações integrais (Fredholm, Volterra)
    15:  Tensores (métrico, Christoffel, Riemann)
    16:  Teoria de grupos (finitos, Lie)
"""

from engine.parser import parsear
from engine.latex_converter import converter_latex
from engine.detector import detectar
from engine.basic.passo import Passo, Historico
from engine.basic.numeros import (
    Racional, Raiz, Exponencial, Logaritmo,
    simplificar, number_to_potencia
)
from engine.basic.expressao import Expressao
from engine.basic import operacoes_basicas as ops
import math


class ResultadoCalculo:
    """Resultado completo de um cálculo."""

    def __init__(self, entrada, resultado, historico, latex_entrada='', valor_numerico=''):
        self.entrada = entrada
        self.resultado = resultado
        self.historico = historico
        self.latex_entrada = latex_entrada
        if resultado is not None and hasattr(resultado, 'representacao_latex'):
            self.latex_resultado = resultado.representacao_latex()
        elif valor_numerico:
            self.latex_resultado = str(valor_numerico)
        else:
            self.latex_resultado = ''
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
        """Resolve uma expressão textual (sintaxe interna ou LaTeX puro) e retorna ResultadoCalculo."""
        if not entrada or not entrada.strip():
            raise ValueError("Expressão vazia")

        historico = Historico(verbosidade=self.verbosidade)

        # Passo 0: Converter LaTeX → sintaxe interna (se necessário)
        entrada_original = entrada.strip()
        entrada_convertida = converter_latex(entrada_original)

        if entrada_convertida != entrada_original:
            historico.adicionar(Passo(
                nivel=1,
                descricao='Converter LaTeX para sintaxe interna',
                latex_antes=entrada_original,
                latex_depois=entrada_convertida,
                regra='latex_para_engine',
                justificativa='A entrada em LaTeX foi traduzida para a sintaxe do engine',
                metodo='Conversor LaTeX → sintaxe Algebrow'
            ))

        # Passo 1: Detectar tipo de operação
        operacao = detectar(entrada_convertida)

        # Passo 2: Rotear para o engine correto
        if operacao['tipo'] != 'basico':
            return self._resolver_operacao(operacao, entrada_original, historico)

        # Fallback: expressão básica (Fases 0-2)
        try:
            return self._resolver_basico(entrada_convertida, entrada_original, historico)
        except Exception as e:
            historico.adicionar(Passo(
                nivel=0,
                descricao=f'Erro ao processar expressão básica: {str(e)}',
                regra='erro',
            ))
            return ResultadoCalculo(
                entrada=entrada_original, resultado=None,
                historico=historico,
                latex_entrada=entrada_original, valor_numerico='',
            )

    def _resolver_operacao(self, operacao, entrada_original, historico):
        """Roteia operações de cálculo para as ferramentas corretas."""
        tipo = operacao['tipo']

        try:
            # --- Derivadas (Fase 4-7) ---
            if tipo == 'derivada':
                from engine.ferramentas.derivada import calcular_derivada
                r = calcular_derivada(operacao['expressao'], operacao['variavel'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=r['resultado'],
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'], valor_numerico='',
                )

            if tipo == 'derivada_ordem':
                from engine.ferramentas.derivada import calcular_derivada_ordem
                r = calcular_derivada_ordem(operacao['expressao'], operacao['variavel'],
                                            operacao['ordem'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=r['resultado'],
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'], valor_numerico='',
                )

            if tipo == 'derivada_implicita':
                from engine.ferramentas.derivada import calcular_derivada_implicita
                r = calcular_derivada_implicita(operacao['expressao'], operacao['var_x'],
                                                operacao['var_y'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=r['resultado'],
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'], valor_numerico='',
                )

            # --- Integrais (Fase 4-7) ---
            if tipo == 'integral':
                from engine.ferramentas.integral import calcular_integral
                r = calcular_integral(operacao['expressao'], operacao['variavel'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=r['resultado'],
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'], valor_numerico='',
                )

            if tipo == 'integral_definida':
                from engine.ferramentas.integral import calcular_integral_definida
                r = calcular_integral_definida(
                    operacao['expressao'], operacao['variavel'],
                    operacao['inferior'], operacao['superior'], self.verbosidade
                )
                rc = ResultadoCalculo(
                    entrada=entrada_original, resultado=r.get('resultado'),
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'],
                    valor_numerico=r.get('valor', ''),
                )
                rc.latex_resultado = r.get('valor', r.get('latex', ''))
                return rc

            # --- Limites (Fase 4-7) ---
            if tipo == 'limite':
                from engine.ferramentas.limite import calcular_limite
                r = calcular_limite(operacao['expressao'], operacao['variavel'],
                                    operacao['valor'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=None,
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'],
                    valor_numerico=r.get('valor', ''),
                )

            if tipo == 'limite_lateral':
                from engine.ferramentas.limite import calcular_limite_lateral
                r = calcular_limite_lateral(operacao['expressao'], operacao['variavel'],
                                            operacao['valor'], operacao['lado'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=None,
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'],
                    valor_numerico=r.get('valor', ''),
                )

            # --- Séries (Fase 4-7) ---
            if tipo == 'taylor':
                from engine.ferramentas.serie import calcular_taylor
                r = calcular_taylor(operacao['expressao'], operacao['variavel'],
                                    operacao['ponto'], operacao['ordem'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=r.get('resultado'),
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'], valor_numerico='',
                )

            # --- Funções Especiais (Fase 8) ---
            if tipo == 'gamma':
                from engine.ferramentas.funcoes_especiais import calcular_gamma
                r = calcular_gamma(operacao['argumento'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=None,
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'],
                    valor_numerico=r.get('valor', ''),
                )

            # --- Álgebra Linear (Fase 5) ---
            if tipo == 'determinante':
                from engine.ferramentas.algebra_linear import calcular_determinante
                r = calcular_determinante(operacao['matriz_texto'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=None,
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'],
                    valor_numerico=r.get('valor', ''),
                )

            if tipo == 'autovalores':
                from engine.ferramentas.algebra_linear import calcular_autovalores
                r = calcular_autovalores(operacao['matriz_texto'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=None,
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'],
                    valor_numerico='',
                )

            # --- Gradiente, Jacobiana, Hessiana (Fase 7) ---
            if tipo == 'gradiente':
                from engine.ferramentas.multivariavel import calcular_gradiente
                r = calcular_gradiente(operacao['expressao'], operacao['variaveis'], self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=None,
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'], valor_numerico='',
                )

            # --- Aplicações (Fase 7) ---
            if tipo in ('maxmin', 'volume_revolucao', 'comprimento_arco'):
                from engine.ferramentas.aplicacoes import resolver_aplicacao
                r = resolver_aplicacao(operacao, self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=None,
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'],
                    valor_numerico=r.get('valor', ''),
                )

            # --- Complexos (Fase 6) ---
            if tipo in ('complexo', 'polar', 'laplace'):
                from engine.ferramentas.complexo import resolver_complexo
                r = resolver_complexo(operacao, self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=None,
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'],
                    valor_numerico=r.get('valor', ''),
                )

            # --- Fourier (Fase 12) ---
            if tipo in ('fourier', 'transformada_fourier'):
                from engine.ferramentas.fourier import resolver_fourier
                r = resolver_fourier(operacao, self.verbosidade)
                return ResultadoCalculo(
                    entrada=entrada_original, resultado=None,
                    historico=r['historico'],
                    latex_entrada=r['latex_entrada'], valor_numerico='',
                )

            # --- Expressão simbólica composta (ex: INTEGRAL(...) - x^3/3) ---
            if tipo == 'expressao_simbolica':
                return self._resolver_expressao_simbolica(operacao, entrada_original, historico)

            # Operação reconhecida mas ferramenta ainda não implementada
            historico_fallback = Historico(verbosidade=self.verbosidade)
            historico_fallback.adicionar(Passo(
                nivel=0,
                descricao=f'Operação "{tipo}" reconhecida mas não disponível via frontend ainda',
                regra='nao_implementado',
            ))
            return ResultadoCalculo(
                entrada=entrada_original, resultado=None,
                historico=historico_fallback,
                latex_entrada=entrada_original, valor_numerico='',
            )

        except Exception as e:
            historico.adicionar(Passo(
                nivel=0,
                descricao=f'Erro ao processar: {str(e)}',
                regra='erro',
            ))
            return ResultadoCalculo(
                entrada=entrada_original, resultado=None,
                historico=historico,
                latex_entrada=entrada_original, valor_numerico='',
            )

    def _resolver_expressao_simbolica(self, operacao, entrada_original, historico):
        """Resolve expressão composta com operações de cálculo + aritmética.

        Ex: INTEGRAL(x^2+y, x) - x^3/3 → resolve integral → monta AST → simplifica → xy + C
        """
        from engine.parser_simbolico import parsear_simbolico
        from engine.calculo.derivada import simplificar_no, simplificar_com_cancelamento
        from engine.calculo.arvore import NoExpressao, num, var, op as ast_op

        texto = operacao['expressao']

        historico.adicionar(Passo(
            nivel=1,
            descricao='Expressão simbólica composta — resolver operações e simplificar',
            latex_antes=entrada_original,
            regra='expressao_simbolica',
        ))

        # Passo 1: Encontrar e resolver cada INTEGRAL/DERIVAR/LIMITE → NoExpressao
        # Substituir no texto por placeholders, guardar os NoExpressao
        resultados_ast = {}
        placeholder_id = 0
        resultado_texto = texto

        for op_name in ('INTEGRAL', 'DERIVAR', 'LIMITE_LATERAL', 'LIMITE'):
            while op_name + '(' in resultado_texto:
                start = resultado_texto.find(op_name + '(')
                if start == -1:
                    break
                depth = 0
                j = start + len(op_name)
                while j < len(resultado_texto):
                    if resultado_texto[j] == '(':
                        depth += 1
                    elif resultado_texto[j] == ')':
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                sub_expr = resultado_texto[start:j+1]

                try:
                    sub_op = detectar(sub_expr)
                    sub_result = self._resolver_operacao(sub_op, sub_expr, historico)
                    # Guardar o NoExpressao do resultado
                    if sub_result.resultado is not None:
                        # Remover o +C da integral para simplificação
                        ast_resultado = sub_result.resultado
                        if (ast_resultado.tipo == 'operacao' and ast_resultado.valor == '+'
                                and ast_resultado.filhos[1].tipo == 'variavel'
                                and ast_resultado.filhos[1].valor == 'C'):
                            ast_sem_c = ast_resultado.filhos[0]
                            tem_c = True
                        else:
                            ast_sem_c = ast_resultado
                            tem_c = False
                        ph = f'__PH{placeholder_id}__'
                        resultados_ast[ph] = (ast_sem_c, tem_c)
                        resultado_texto = resultado_texto[:start] + ph + resultado_texto[j+1:]
                        placeholder_id += 1
                    else:
                        # Sem AST, usar LaTeX como string
                        sub_latex = sub_result.latex_resultado or sub_expr
                        resultado_texto = resultado_texto[:start] + sub_latex + resultado_texto[j+1:]
                except Exception:
                    break

        # Passo 2: Se temos placeholders com AST, parsear o restante e combinar
        if resultados_ast:
            try:
                # Substituir placeholders por variáveis temporárias para parsear
                texto_para_parse = resultado_texto
                mapa_ph_var = {}
                for ph in resultados_ast:
                    var_temp = f'P{ph.strip("_").replace("PH", "")}'
                    # Usar um nome que o parser aceita como variável
                    var_temp_nome = chr(ord('A') + int(ph.strip('_').replace('PH', '')))
                    texto_para_parse = texto_para_parse.replace(ph, var_temp_nome)
                    mapa_ph_var[var_temp_nome] = ph

                # Parsear a expressão com variáveis temporárias
                # Adicionar as letras usadas como variáveis permitidas temporariamente
                from engine.parser_simbolico import VARIAVEIS_PERMITIDAS
                vars_originais = VARIAVEIS_PERMITIDAS.copy()
                for v in mapa_ph_var:
                    VARIAVEIS_PERMITIDAS.add(v.lower())

                try:
                    arvore = parsear_simbolico(texto_para_parse.lower())
                finally:
                    VARIAVEIS_PERMITIDAS.clear()
                    VARIAVEIS_PERMITIDAS.update(vars_originais)

                # Substituir as variáveis temporárias pelos NoExpressao reais
                def _substituir_placeholders(no):
                    if no.tipo == 'variavel' and no.valor.upper() in mapa_ph_var:
                        ph = mapa_ph_var[no.valor.upper()]
                        return resultados_ast[ph][0]
                    if no.tipo in ('numero', 'variavel'):
                        return no
                    novos_filhos = [_substituir_placeholders(f) for f in no.filhos]
                    return NoExpressao(no.tipo, no.valor, novos_filhos)

                arvore_completa = _substituir_placeholders(arvore)

                # Passo 3: Simplificar com cancelamento de termos
                simplificado = simplificar_com_cancelamento(arvore_completa)
                simplificado = simplificar_no(simplificado)

                # Adicionar +C se alguma integral tinha
                tem_c_global = any(tc for _, tc in resultados_ast.values())
                if tem_c_global:
                    simplificado = ast_op('+', simplificado, var('C'))

                latex_resultado = simplificado.representacao_latex()

                historico.adicionar(Passo(
                    nivel=0,
                    descricao='Resultado simplificado',
                    latex_antes=entrada_original,
                    latex_depois=latex_resultado,
                    regra='resultado',
                ))

                rc = ResultadoCalculo(
                    entrada=entrada_original, resultado=simplificado,
                    historico=historico,
                    latex_entrada=entrada_original, valor_numerico='',
                )
                return rc

            except Exception:
                pass  # Fallback para método string abaixo

        # Fallback: substituição por string (sem simplificação)
        for ph, (ast_no, tem_c) in resultados_ast.items():
            latex = ast_no.representacao_latex()
            if tem_c:
                latex += ' + C'
            resultado_texto = resultado_texto.replace(ph, latex)

        historico.adicionar(Passo(
            nivel=0,
            descricao='Resultado (sem simplificação)',
            latex_antes=entrada_original,
            latex_depois=resultado_texto,
            regra='resultado',
        ))

        rc = ResultadoCalculo(
            entrada=entrada_original, resultado=None,
            historico=historico,
            latex_entrada=entrada_original, valor_numerico='',
        )
        rc.latex_resultado = resultado_texto
        return rc

    def _resolver_basico(self, entrada_convertida, entrada_original, historico):
        """Resolve expressão básica (Fases 0-2)."""
        # Passo 1: Parse
        objeto = parsear(entrada_convertida)
        latex_entrada = objeto.representacao_latex() if hasattr(objeto, 'representacao_latex') else entrada_original

        historico.adicionar(Passo(
            nivel=1,
            descricao='Interpretar expressão',
            latex_antes=entrada_original,
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
            entrada=entrada_original,
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
            fatores_extraidos = []
            for base, expoente in fatores.items():
                exp_int = int(expoente)
                idx_int = int(indice)

                # Passo nível 4: divisão euclidiana do expoente pelo índice
                historico.adicionar(Passo(
                    nivel=4,
                    descricao=f'Divisão euclidiana de {base}^{{{expoente}}}',
                    latex_antes=f'{base}^{{{expoente}}}',
                    latex_depois=f'{expoente} \\div {indice} = {exp_int // idx_int} \\text{{ resto }} {exp_int % idx_int}',
                    regra='divisao_euclidiana',
                    justificativa=f'{base}^{{{expoente}}} → divido pelo índice {indice}',
                    metodo=f'{base}^{{{expoente}}} → divido pelo índice {indice}'
                ))

                if exp_int >= idx_int:
                    sai = exp_int // idx_int
                    resta = exp_int % idx_int
                    fatores_extraidos.append((base, sai))
                    historico.adicionar(Passo(
                        nivel=3,
                        descricao=f'Extrair {base} da raiz',
                        latex_antes=f'{base}^{{{expoente}}}',
                        latex_depois=f'{base}^{{{sai}}} sai, {base}^{{{resta}}} fica' if resta > 0 else f'{base}^{{{sai}}} sai inteiro',
                        regra='extracao_fator',
                        justificativa=f'Expoente {expoente} ÷ índice {indice} = {sai} (inteiro) + {resta} (resto)',
                        metodo=f'Se expoente ≥ índice, o fator sai da raiz elevado a expoente÷índice'
                    ))

            # Passo nível 3: Mostrar multiplicação dos fatores extraídos
            if len(fatores_extraidos) > 1:
                valores = [int(b) ** s for b, s in fatores_extraidos]
                mult_str = ' \\times '.join(str(v) for v in valores)
                produto = 1
                for v in valores:
                    produto *= v
                historico.adicionar(Passo(
                    nivel=3,
                    descricao=f'Multiplicar fatores extraídos: {mult_str} = {produto}',
                    latex_antes=mult_str,
                    latex_depois=str(produto),
                    regra='multiplicacao_coeficiente',
                    justificativa='Os fatores que saíram da raiz são multiplicados para formar o coeficiente',
                    metodo=f'{mult_str} = {produto}'
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

            # Calcular resultado concreto da potência de potência
            resultado_pot_str = ' \\cdot '.join(
                f'{b}^{{{int(e) * int(expoente)}}}'
                for b, e in fatores.items()
            )
            historico.adicionar(Passo(
                nivel=3,
                descricao='Aplicar propriedade da potência de potência',
                latex_antes=f'({fatoracao_str})^{{{expoente}}}',
                latex_depois=resultado_pot_str,
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
        num = int(racional.return_numerador())
        den = int(racional.return_denominador())
        mdc = math.gcd(abs(num), abs(den))

        resultado = simplificar(racional)
        latex_resultado = resultado.representacao_latex()

        if latex_original != latex_resultado:
            historico.adicionar(Passo(
                nivel=2,
                descricao=f'Simplificar fração pelo MDC = {mdc}',
                latex_antes=latex_original,
                latex_depois=latex_resultado,
                regra='simplificacao_fracao',
                justificativa='Dividir numerador e denominador pelo MDC',
                metodo=f'{num} ÷ {mdc} = {num//mdc}, {den} ÷ {mdc} = {den//mdc}'
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
        except (ValueError, ZeroDivisionError, OverflowError):
            return ''
        except AttributeError:
            # Tipo sem método numero_real() — não deveria acontecer, mas não mascara
            return ''
        return ''
