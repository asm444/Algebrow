"""Conversor de LaTeX puro para a sintaxe interna do engine.

Transforma expressões LaTeX como \\frac{3}{4}, \\sqrt[3]{8}, \\log_{2}{8}
na sintaxe que o parser do Algebrow entende: 3/4, sqrt_3(8), log_2(8).

Exemplos:
    converter_latex("\\frac{3}{4} + \\sqrt{2}")       → "3/4 + sqrt(2)"
    converter_latex("\\sqrt[3]{8}")                    → "sqrt_3(8)"
    converter_latex("2^{10}")                          → "2^10"
    converter_latex("\\log_{2}{8}")                    → "log_2(8)"
    converter_latex("x^{2} - 5x + 6 = 0")             → "x^2 - 5x + 6 = 0"
    converter_latex("\\frac{1}{2} + \\frac{1}{3}")     → "1/2 + 1/3"
"""

import re


def _extrair_grupo(texto: str, pos: int) -> tuple[str, int]:
    """Extrai conteúdo de um grupo LaTeX delimitado por chaves {}.

    Retorna (conteúdo, posição_após_fechar_chave).
    Se não há '{' na posição, retorna o próximo caractere como grupo.
    """
    if pos >= len(texto):
        return '', pos

    if texto[pos] == '{':
        profundidade = 1
        inicio = pos + 1
        i = inicio
        while i < len(texto) and profundidade > 0:
            if texto[i] == '{':
                profundidade += 1
            elif texto[i] == '}':
                profundidade -= 1
            i += 1
        return texto[inicio:i - 1], i
    else:
        return texto[pos], pos + 1


def _extrair_grupo_opcional(texto: str, pos: int) -> tuple[str | None, int]:
    """Extrai conteúdo de um grupo opcional LaTeX delimitado por [].

    Retorna (conteúdo, posição_após_fechar_colchete) ou (None, pos) se não há '['.
    """
    if pos >= len(texto) or texto[pos] != '[':
        return None, pos

    profundidade = 1
    inicio = pos + 1
    i = inicio
    while i < len(texto) and profundidade > 0:
        if texto[i] == '[':
            profundidade += 1
        elif texto[i] == ']':
            profundidade -= 1
        i += 1
    return texto[inicio:i - 1], i


def _eh_expressao_simples(texto: str) -> bool:
    """Verifica se o texto é uma expressão simples (número, variável, ou identificador)."""
    texto = texto.strip()
    if not texto:
        return True
    # Número puro (inclui negativos e decimais)
    if texto.replace('.', '').replace('-', '').isdigit():
        return True
    # Variável simples
    if len(texto) == 1 and texto.isalpha():
        return True
    # Identificadores como sqrt_3(...), log_2(...)
    if texto.startswith(('sqrt', 'log')):
        return True
    return False


def _eh_latex(texto: str) -> bool:
    """Detecta se a entrada contém comandos LaTeX."""
    indicadores = [
        '\\frac', '\\dfrac', '\\tfrac',
        '\\sqrt', '\\log', '\\ln',
        '\\cdot', '\\times', '\\div',
        '\\left', '\\right',
        '\\geq', '\\leq', '\\neq',
        '\\pi', '\\infty',
        '\\begin', '\\end',
        '\\int', '\\lim', '\\sum', '\\prod',
        '\\sin', '\\cos', '\\tan', '\\arcsin', '\\arccos', '\\arctan',
        '\\sinh', '\\cosh', '\\tanh', '\\sec', '\\csc', '\\cot',
        '\\exp', '\\det', '\\Gamma',
        '\\mathcal', '\\partial', '\\nabla',
        '\\kappa', '\\tau', '\\to', '\\rightarrow',
    ]
    # Também detecta chaves usadas como agrupamento LaTeX (ex: 2^{10})
    if '{' in texto and '}' in texto:
        return True
    return any(ind in texto for ind in indicadores)


def converter_latex(texto: str) -> str:
    """Converte LaTeX puro para sintaxe interna do engine.

    Se a entrada não contém comandos LaTeX, retorna sem alteração.
    """
    if not _eh_latex(texto):
        return texto

    resultado = _processar_latex(texto)
    # Normalizar espaços múltiplos
    resultado = re.sub(r' +', ' ', resultado)
    return resultado.strip()


def _processar_latex(texto: str) -> str:
    """Processa o texto LaTeX caractere a caractere, convertendo comandos."""
    resultado = []
    i = 0

    while i < len(texto):
        c = texto[i]

        # Ignorar espaços LaTeX e delimitadores
        if c in (' ', '\t', '\n'):
            resultado.append(' ')
            i += 1
            continue

        # Comando LaTeX (começa com \)
        if c == '\\':
            cmd, i = _processar_comando(texto, i)
            resultado.append(cmd)
            continue

        # Chaves: grupo LaTeX → conteúdo direto ou com parênteses
        if c == '{':
            conteudo, i = _extrair_grupo(texto, i)
            processado = _processar_latex(conteudo)
            # Se é um número, variável simples ou já processado como expressão simples → sem parênteses
            if processado.replace('.', '').replace('-', '').isdigit() or \
               (len(processado) == 1 and processado.isalnum()):
                resultado.append(processado)
            elif _eh_expressao_simples(processado):
                resultado.append(processado)
            else:
                resultado.append(f'({processado})')
            continue

        # Caractere normal
        resultado.append(c)
        i += 1

    return ''.join(resultado)


def _extrair_integrando(texto: str, pos: int) -> tuple[str, str, int]:
    """Extrai o integrando e a variável de integração de uma integral.

    Procura padrão: <integrando> \\, d<var> ou <integrando> d<var>
    Retorna (integrando, variavel, nova_posicao).
    """
    import re as _re

    # Procurar padrão "d<var>" no texto a partir de pos
    restante = texto[pos:]

    # Tentar encontrar \, dx ou dx ou d{x} no final
    # Padrões: "\\, dx", "\\,dx", " dx", "\\; dx", "d{x}"
    patterns = [
        r'(.+?)\\[,;]\s*d([a-z])\s*$',   # \, dx ou \; dx
        r'(.+?)\\[,;]\s*d\{([a-z])\}\s*$',  # \, d{x}
        r'(.+?)\s+d([a-z])\s*$',           # espaço dx
        r'(.+?)d([a-z])\s*$',              # dx colado
    ]

    for pattern in patterns:
        m = _re.match(pattern, restante, _re.DOTALL)
        if m:
            integrando = m.group(1).strip()
            variavel = m.group(2)
            return integrando, variavel, pos + m.end()

    # Fallback: assumir x como variável e tudo é integrando
    return restante.strip(), 'x', len(texto)


def _extrair_corpo_apos_derivada(texto: str, pos: int) -> tuple[str, int]:
    """Extrai o corpo da expressão após \\frac{d}{dx}, que pode ser \\left(...)\\right), {...}, (...) ou texto."""
    if pos >= len(texto):
        return '', pos
    # \left(...)
    if texto[pos:pos+5] == '\\left':
        # Encontrar \right correspondente
        depth = 0
        j = pos
        while j < len(texto):
            if texto[j:j+5] == '\\left':
                depth += 1
                j += 5
                if j < len(texto) and texto[j] in '(.[|{':
                    j += 1
                continue
            if texto[j:j+6] == '\\right':
                depth -= 1
                j += 6
                if j < len(texto) and texto[j] in ').]|}':
                    j += 1
                if depth == 0:
                    # Extrair interior (sem \left( e \right))
                    interior = texto[pos:j]
                    return interior, j
                continue
            j += 1
        return texto[pos:], len(texto)
    # {corpo}
    if texto[pos] == '{':
        corpo, new_pos = _extrair_grupo(texto, pos)
        return corpo, new_pos
    # (corpo)
    if texto[pos] == '(':
        depth = 1
        j = pos + 1
        while j < len(texto) and depth > 0:
            if texto[j] == '(':
                depth += 1
            elif texto[j] == ')':
                depth -= 1
            j += 1
        return texto[pos+1:j-1], j
    # Texto até o fim ou até operador/espaço
    j = pos
    while j < len(texto) and texto[j] not in ' =><':
        if texto[j] == '\\':
            # Pode ser outro comando, parar
            break
        j += 1
    return texto[pos:j], j


def _processar_comando(texto: str, pos: int) -> tuple[str, int]:
    """Processa um comando LaTeX começando em \\."""
    # Extrair nome do comando
    i = pos + 1  # pula o '\'
    if i >= len(texto):
        return '\\', i

    # Comando de uma letra (ex: \, \; \! \\ )
    if not texto[i].isalpha():
        return '', i + 1

    inicio = i
    while i < len(texto) and texto[i].isalpha():
        i += 1
    comando = texto[inicio:i]

    # Pular espaços após o comando
    while i < len(texto) and texto[i] == ' ':
        i += 1

    # --- Frações (com detecção de derivada: \frac{d}{dx} ou \frac{d^n}{dx^n}) ---
    if comando == 'frac':
        numerador, i = _extrair_grupo(texto, i)
        while i < len(texto) and texto[i] == ' ':
            i += 1
        denominador, i = _extrair_grupo(texto, i)

        # Detectar derivada de Leibniz: \frac{d}{dx}(...) ou \frac{d^n}{dx^n}(...)
        import re as _re
        m_deriv = _re.match(r'^d(\^(\d+))?$', numerador.strip())
        m_denom = _re.match(r'^d([a-z])(\^\d+)?$', denominador.strip())
        if m_deriv and m_denom:
            ordem = m_deriv.group(2) or '1'
            var = m_denom.group(1)
            # Extrair a expressão que segue
            while i < len(texto) and texto[i] == ' ':
                i += 1
            # Extrair corpo: se tem \left( ou { ou ( delimita, senão pega tudo
            if i < len(texto) and (texto[i] == '{' or texto[i] == '(' or texto[i:i+5] == '\\left'):
                corpo, i = _extrair_corpo_apos_derivada(texto, i)
                corpo_conv = _processar_latex(corpo)
            else:
                corpo_raw = texto[i:]
                i = len(texto)
                corpo_conv = _processar_latex(corpo_raw)
            if ordem == '1':
                return f'DERIVAR({corpo_conv}, {var})', i
            return f'DERIVAR({corpo_conv}, {var}, {ordem})', i

        num_conv = _processar_latex(numerador)
        den_conv = _processar_latex(denominador)
        return f'{num_conv}/{den_conv}', i

    if comando == 'dfrac' or comando == 'tfrac':
        numerador, i = _extrair_grupo(texto, i)
        while i < len(texto) and texto[i] == ' ':
            i += 1
        denominador, i = _extrair_grupo(texto, i)
        num_conv = _processar_latex(numerador)
        den_conv = _processar_latex(denominador)
        return f'{num_conv}/{den_conv}', i

    # --- Raízes ---
    if comando == 'sqrt':
        indice, i = _extrair_grupo_opcional(texto, i)
        while i < len(texto) and texto[i] == ' ':
            i += 1
        radicando, i = _extrair_grupo(texto, i)
        rad_conv = _processar_latex(radicando)
        if indice:
            ind_conv = _processar_latex(indice)
            return f'sqrt_{ind_conv}({rad_conv})', i
        return f'sqrt({rad_conv})', i

    # --- Logaritmos ---
    if comando == 'log':
        if i < len(texto) and texto[i] == '_':
            i += 1  # pula _
            while i < len(texto) and texto[i] == ' ':
                i += 1
            base, i = _extrair_grupo(texto, i)
            while i < len(texto) and texto[i] == ' ':
                i += 1
            # O argumento pode ser {x} ou (x)
            if i < len(texto) and texto[i] == '{':
                argumento, i = _extrair_grupo(texto, i)
            elif i < len(texto) and texto[i] == '(':
                # Já está em parênteses, extrair conteúdo
                prof = 1
                inicio_arg = i + 1
                j = inicio_arg
                while j < len(texto) and prof > 0:
                    if texto[j] == '(':
                        prof += 1
                    elif texto[j] == ')':
                        prof -= 1
                    j += 1
                argumento = texto[inicio_arg:j - 1]
                i = j
            else:
                argumento, i = _extrair_grupo(texto, i)
            base_conv = _processar_latex(base)
            arg_conv = _processar_latex(argumento)
            return f'log_{base_conv}({arg_conv})', i
        # \log sem base → log base 10
        if i < len(texto) and texto[i] in ('{', '('):
            if texto[i] == '{':
                argumento, i = _extrair_grupo(texto, i)
            else:
                prof = 1
                inicio_arg = i + 1
                j = inicio_arg
                while j < len(texto) and prof > 0:
                    if texto[j] == '(':
                        prof += 1
                    elif texto[j] == ')':
                        prof -= 1
                    j += 1
                argumento = texto[inicio_arg:j - 1]
                i = j
            arg_conv = _processar_latex(argumento)
            return f'log({arg_conv})', i
        return 'log', i

    if comando == 'ln':
        if i < len(texto) and texto[i] in ('{', '('):
            if texto[i] == '{':
                argumento, i = _extrair_grupo(texto, i)
            else:
                prof = 1
                inicio_arg = i + 1
                j = inicio_arg
                while j < len(texto) and prof > 0:
                    if texto[j] == '(':
                        prof += 1
                    elif texto[j] == ')':
                        prof -= 1
                    j += 1
                argumento = texto[inicio_arg:j - 1]
                i = j
            arg_conv = _processar_latex(argumento)
            return f'ln({arg_conv})', i
        return 'ln', i

    # --- Operadores (preservar espaço ao redor) ---
    if comando == 'cdot':
        return ' * ', i
    if comando == 'times':
        return ' * ', i
    if comando == 'div':
        return ' / ', i

    # --- Comparadores ---
    if comando == 'geq' or comando == 'ge':
        return ' >= ', i
    if comando == 'leq' or comando == 'le':
        return ' <= ', i
    if comando == 'neq' or comando == 'ne':
        return ' != ', i

    # --- Delimitadores descartáveis ---
    if comando in ('left', 'right', 'bigl', 'bigr', 'Bigl', 'Bigr',
                    'biggl', 'biggr', 'Biggl', 'Biggr'):
        # Próximo caractere é o delimitador (ex: \left( → ()
        if i < len(texto):
            delim = texto[i]
            i += 1
            if delim == '.':
                return '', i
            return delim, i
        return '', i

    # --- Constantes ---
    if comando == 'pi':
        return 'pi', i
    if comando == 'infty':
        return 'inf', i

    # --- Integral: \int, \int_a^b ---
    if comando == 'int':
        inferior = None
        superior = None
        # Verificar limites: \int_{a}^{b} ou \int_a^b
        if i < len(texto) and texto[i] == '_':
            i += 1
            while i < len(texto) and texto[i] == ' ':
                i += 1
            inferior_raw, i = _extrair_grupo(texto, i)
            inferior = _processar_latex(inferior_raw)
        if i < len(texto) and texto[i] == '^':
            i += 1
            while i < len(texto) and texto[i] == ' ':
                i += 1
            superior_raw, i = _extrair_grupo(texto, i)
            superior = _processar_latex(superior_raw)
        while i < len(texto) and texto[i] == ' ':
            i += 1
        # Extrair integrando até \, dx ou dx ou d{var}
        corpo, var, i = _extrair_integrando(texto, i)
        corpo_conv = _processar_latex(corpo)
        if inferior is not None and superior is not None:
            return f'INTEGRAL({corpo_conv}, {var}, {inferior}, {superior})', i
        return f'INTEGRAL({corpo_conv}, {var})', i

    # --- Limite: \lim_{x \to a} ---
    if comando == 'lim':
        var = 'x'
        valor = '0'
        lado = None
        if i < len(texto) and texto[i] == '_':
            i += 1
            while i < len(texto) and texto[i] == ' ':
                i += 1
            subscrito, i = _extrair_grupo(texto, i)
            # Parsear "x \to a" ou "x \to a^+" ou "x \to a^-"
            import re as _re
            m = _re.match(r'([a-z])\s*(?:\\to|\\rightarrow|->)\s*(.+)', subscrito)
            if m:
                var = m.group(1)
                valor_raw = m.group(2).strip()
                # Verificar lateral: a^+ ou a^-
                m_lat = _re.match(r'(.+)\^([+-])$', valor_raw)
                if m_lat:
                    valor = _processar_latex(m_lat.group(1))
                    lado = 'direita' if m_lat.group(2) == '+' else 'esquerda'
                else:
                    valor = _processar_latex(valor_raw)
        while i < len(texto) and texto[i] == ' ':
            i += 1
        # Para \lim, o corpo é TUDO que vem depois (até o fim do texto)
        corpo_raw = texto[i:]
        i = len(texto)
        corpo_conv = _processar_latex(corpo_raw)
        if lado:
            return f'LIMITE_LATERAL({corpo_conv}, {var}, {valor}, {lado})', i
        return f'LIMITE({corpo_conv}, {var}, {valor})', i

    # --- Funções trigonométricas e transcendentes ---
    if comando in ('sin', 'cos', 'tan', 'arcsin', 'arccos', 'arctan',
                    'sinh', 'cosh', 'tanh', 'sec', 'csc', 'cot'):
        if i < len(texto) and texto[i] in ('{', '(', '\\'):
            if texto[i] == '{':
                arg, i = _extrair_grupo(texto, i)
            elif texto[i] == '\\' and texto[i:i+5] == '\\left':
                arg, i = _extrair_corpo_apos_derivada(texto, i)
            else:
                # Parênteses (...)
                depth = 1
                j = i + 1
                while j < len(texto) and depth > 0:
                    if texto[j] == '(':
                        depth += 1
                    elif texto[j] == ')':
                        depth -= 1
                    j += 1
                arg = texto[i+1:j-1]
                i = j
            arg_conv = _processar_latex(arg)
            return f'{comando}({arg_conv})', i
        return comando, i

    # --- Funções especiais ---
    if comando == 'Gamma':
        if i < len(texto) and texto[i] in ('{', '('):
            if texto[i] == '{':
                arg, i = _extrair_grupo(texto, i)
            else:
                depth = 1
                j = i + 1
                while j < len(texto) and depth > 0:
                    if texto[j] == '(':
                        depth += 1
                    elif texto[j] == ')':
                        depth -= 1
                    j += 1
                arg = texto[i+1:j-1]
                i = j
            arg_conv = _processar_latex(arg)
            return f'GAMMA({arg_conv})', i
        return 'GAMMA', i

    # --- Transformadas: \mathcal{L}, \mathcal{F} ---
    if comando == 'mathcal':
        if i < len(texto) and texto[i] == '{':
            tipo_transf, i = _extrair_grupo(texto, i)
            while i < len(texto) and texto[i] == ' ':
                i += 1
            # Extrair argumento entre \{ \} ou { }
            if i < len(texto) and texto[i] == '\\' and i+1 < len(texto) and texto[i+1] == '{':
                i += 2  # pular \{
                depth = 1
                j = i
                while j < len(texto) and depth > 0:
                    if texto[j] == '\\' and j+1 < len(texto) and texto[j+1] == '{':
                        depth += 1
                        j += 2
                        continue
                    if texto[j] == '\\' and j+1 < len(texto) and texto[j+1] == '}':
                        depth -= 1
                        j += 2
                        if depth == 0:
                            break
                        continue
                    j += 1
                arg = texto[i:j-2] if j >= 2 else ''
                i = j
            elif i < len(texto) and texto[i] == '{':
                arg, i = _extrair_grupo(texto, i)
            else:
                arg = ''
            arg_conv = _processar_latex(arg)
            if tipo_transf == 'L':
                return f'LAPLACE({arg_conv}, t)', i
            if tipo_transf == 'F':
                return f'TRANSFORMADA_FOURIER({arg_conv}, x)', i
            return arg_conv, i
        return '', i

    # --- Determinante: \det ---
    if comando == 'det':
        return 'DETERMINANTE', i

    # --- Somatório: \sum ---
    if comando == 'sum':
        return 'sum', i

    # --- Produto: \prod ---
    if comando == 'prod':
        return 'prod', i

    # --- Valor absoluto ---
    if comando == 'abs':
        if i < len(texto) and texto[i] == '{':
            arg, i = _extrair_grupo(texto, i)
            arg_conv = _processar_latex(arg)
            return f'abs({arg_conv})', i
        return 'abs', i

    # --- Begin/End environments (matrizes, sistemas) ---
    if comando == 'begin':
        if i < len(texto) and texto[i] == '{':
            env_name, i = _extrair_grupo(texto, i)
            if env_name in ('pmatrix', 'bmatrix', 'matrix', 'vmatrix'):
                # Extrair até \end{pmatrix}
                end_tag = f'\\end{{{env_name}}}'
                end_pos = texto.find(end_tag, i)
                if end_pos == -1:
                    return '', len(texto)
                conteudo = texto[i:end_pos]
                i = end_pos + len(end_tag)
                # Converter LaTeX de matriz para formato interno
                linhas = conteudo.strip().split('\\\\')
                matriz_str = '['
                for idx_l, linha in enumerate(linhas):
                    elementos = [_processar_latex(e.strip()) for e in linha.split('&') if e.strip()]
                    if elementos:
                        matriz_str += '[' + ', '.join(elementos) + ']'
                        if idx_l < len(linhas) - 1:
                            matriz_str += ', '
                matriz_str += ']'
                return matriz_str, i
            if env_name == 'cases':
                # Extrair até \end{cases}
                end_tag = '\\end{cases}'
                end_pos = texto.find(end_tag, i)
                if end_pos == -1:
                    return '', len(texto)
                conteudo = texto[i:end_pos]
                i = end_pos + len(end_tag)
                # Converter sistema de equações
                linhas = conteudo.strip().split('\\\\')
                eqs = []
                for linha in linhas:
                    eq = _processar_latex(linha.strip())
                    if eq:
                        eqs.append(eq)
                return ' ; '.join(eqs), i
        return '', i

    if comando == 'end':
        if i < len(texto) and texto[i] == '{':
            _, i = _extrair_grupo(texto, i)
        return '', i

    # --- Kappa, tau (geometria diferencial) ---
    if comando == 'kappa':
        return 'CURVATURA', i
    if comando == 'tau':
        return 'TORSAO', i

    # --- Nabla (gradiente, divergente, rotacional) ---
    if comando == 'nabla':
        return 'NABLA', i

    # --- Partial ---
    if comando == 'partial':
        return 'd', i

    # --- Formatação ignorável ---
    if comando in ('displaystyle', 'textstyle', 'scriptstyle',
                    'scriptscriptstyle', 'mathrm', 'mathbf', 'mathit',
                    'text', 'operatorname', 'quad', 'qquad', 'hspace',
                    'vspace', 'phantom', 'hfill'):
        if i < len(texto) and texto[i] == '{':
            conteudo, i = _extrair_grupo(texto, i)
            return _processar_latex(conteudo), i
        return '', i

    # --- Espaçamento LaTeX ignorável ---
    if comando in (',', ';', '!', ' ', 'thinspace', 'medspace', 'thickspace',
                    'enspace', 'negthickspace', 'negthinspace'):
        return ' ', i

    # Comando desconhecido: retorna como texto
    return comando, i
