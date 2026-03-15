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

    # --- Frações ---
    if comando == 'frac':
        numerador, i = _extrair_grupo(texto, i)
        while i < len(texto) and texto[i] == ' ':
            i += 1
        denominador, i = _extrair_grupo(texto, i)
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
            return f'log({arg_conv})', i
        return 'log', i

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

    # --- Formatação ignorável ---
    if comando in ('displaystyle', 'textstyle', 'scriptstyle',
                    'scriptscriptstyle', 'mathrm', 'mathbf', 'mathit',
                    'text', 'operatorname'):
        if i < len(texto) and texto[i] == '{':
            conteudo, i = _extrair_grupo(texto, i)
            return _processar_latex(conteudo), i
        return '', i

    # Comando desconhecido: retorna como texto
    return comando, i
