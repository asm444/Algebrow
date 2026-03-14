"""Módulo de geração de pontos para gráficos 2D.

Gera pontos (x, y) a partir de uma expressão matemática textual,
detectando descontinuidades e assíntotas verticais.
"""

import ast
import math
import operator

# Namespace seguro para avaliação de expressões
_NAMESPACE_SEGURO = {
    'sqrt': math.sqrt,
    'log': math.log10,
    'ln': math.log,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'abs': abs,
    'pi': math.pi,
    'e': math.e,
    'exp': math.exp,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
}

# Threshold para detectar descontinuidades
_THRESHOLD_DESCONTINUIDADE = 1e6
_THRESHOLD_INFINITO = 1e10


def _preparar_expressao(expressao: str) -> str:
    """Prepara a expressão para avaliação numérica.

    Converte notações comuns para Python válido:
    - 2x → 2*x
    - ^ → **
    """
    expr = expressao.strip()
    # Substituir ^ por **
    expr = expr.replace('^', '**')

    # Inserir multiplicação implícita: número seguido de letra ou '('
    resultado = []
    for i, c in enumerate(expr):
        resultado.append(c)
        if i + 1 < len(expr):
            prox = expr[i + 1]
            # Número seguido de letra ou '('
            if (c.isdigit() or c == '.') and (prox.isalpha() or prox == '('):
                resultado.append('*')
            # ')' seguido de letra, número ou '('
            elif c == ')' and (prox.isalpha() or prox.isdigit() or prox == '('):
                resultado.append('*')
            # Letra seguido de '(' — mas não se for nome de função
            elif c.isalpha() and prox == '(':
                # Extrair a palavra que termina em c
                inicio = i
                while inicio > 0 and expr[inicio - 1].isalpha():
                    inicio -= 1
                palavra = expr[inicio:i + 1]
                if palavra not in _NAMESPACE_SEGURO and palavra != 'x':
                    resultado.append('*')
            # Letra seguida de número (ex: x2 → x*2)
            elif c.isalpha() and prox.isdigit():
                resultado.append('*')

    return ''.join(resultado)


_OPERADORES_BINARIOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

_OPERADORES_UNARIOS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _avaliar_ast_seguro(node: ast.AST, namespace: dict) -> float:
    """Percorre o AST e avalia apenas nós seguros (Num, BinOp, UnaryOp, Name, Call)."""
    if isinstance(node, ast.Expression):
        return _avaliar_ast_seguro(node.body, namespace)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Constante não numérica: {node.value!r}")

    if isinstance(node, ast.Name):
        if node.id in namespace:
            return namespace[node.id]
        raise ValueError(f"Nome não permitido: {node.id}")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _OPERADORES_BINARIOS:
            raise ValueError(f"Operador binário não permitido: {op_type.__name__}")
        esq = _avaliar_ast_seguro(node.left, namespace)
        dir_ = _avaliar_ast_seguro(node.right, namespace)
        return _OPERADORES_BINARIOS[op_type](esq, dir_)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _OPERADORES_UNARIOS:
            raise ValueError(f"Operador unário não permitido: {op_type.__name__}")
        operando = _avaliar_ast_seguro(node.operand, namespace)
        return _OPERADORES_UNARIOS[op_type](operando)

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Chamada de função não permitida (apenas nomes simples)")
        nome_func = node.func.id
        if nome_func not in namespace or not callable(namespace[nome_func]):
            raise ValueError(f"Função não permitida: {nome_func}")
        args = [_avaliar_ast_seguro(arg, namespace) for arg in node.args]
        return namespace[nome_func](*args)

    raise ValueError(f"Nó AST não permitido: {type(node).__name__}")


def _avaliar_seguro(expressao_preparada: str, x: float) -> float | None:
    """Avalia a expressão para um dado valor de x usando AST seguro.

    Apenas nós seguros são aceitos: constantes numéricas, operações aritméticas,
    nomes do namespace seguro e chamadas de funções do namespace.

    Returns:
        O valor float ou None se houver erro matemático.
    """
    namespace = {**_NAMESPACE_SEGURO, 'x': x}
    try:
        tree = ast.parse(expressao_preparada, mode='eval')
        resultado = _avaliar_ast_seguro(tree, namespace)
        if resultado is None:
            return None
        val = float(resultado)
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    except (ValueError, ZeroDivisionError, OverflowError, TypeError, ArithmeticError):
        return None


def gerar_pontos(funcao_avaliar, x_min: float, x_max: float, num_pontos: int = 200) -> dict:
    """Gera pontos para plotar um gráfico 2D.

    Args:
        funcao_avaliar: callable que recebe float e retorna float|None,
                        OU uma string com a expressão (ex: "x**2 + 1", "1/x").
        x_min, x_max: intervalo do eixo x.
        num_pontos: quantidade de pontos.

    Returns:
        {
            "x": [float, ...],
            "y": [float | None, ...],
            "assintotas_verticais": [float, ...],
            "x_min": float,
            "x_max": float
        }
    """
    if x_min >= x_max:
        raise ValueError("x_min deve ser menor que x_max")
    if num_pontos < 2:
        raise ValueError("num_pontos deve ser >= 2")

    # Se recebeu string, preparar para avaliação
    if isinstance(funcao_avaliar, str):
        expr_preparada = _preparar_expressao(funcao_avaliar)
        avaliar = lambda val_x: _avaliar_seguro(expr_preparada, val_x)
    else:
        avaliar = funcao_avaliar

    passo = (x_max - x_min) / (num_pontos - 1)
    xs = [x_min + i * passo for i in range(num_pontos)]
    ys = []

    for val_x in xs:
        try:
            val_y = avaliar(val_x)
            if val_y is not None and abs(val_y) > _THRESHOLD_INFINITO:
                val_y = None
            ys.append(val_y)
        except Exception:
            ys.append(None)

    # Detectar descontinuidades: inserir None onde há saltos abruptos
    assintotas = set()
    for i in range(1, len(ys)):
        if ys[i] is not None and ys[i - 1] is not None:
            if abs(ys[i] - ys[i - 1]) > _THRESHOLD_DESCONTINUIDADE:
                # Marcar como descontinuidade
                assintotas.add(round(xs[i], 10))
                ys[i] = None
        elif ys[i] is None and ys[i - 1] is not None:
            # Ponto onde a função deixou de existir — possível assíntota
            assintotas.add(round(xs[i], 10))
        elif ys[i] is not None and ys[i - 1] is None:
            assintotas.add(round(xs[i - 1], 10))

    return {
        "x": xs,
        "y": ys,
        "assintotas_verticais": sorted(assintotas),
        "x_min": x_min,
        "x_max": x_max,
    }


def detectar_assintotas_verticais(
    funcao_avaliar, x_min: float, x_max: float, num_pontos: int = 1000
) -> list[float]:
    """Detecta assíntotas verticais por aproximação.

    Testa pontos no intervalo e detecta onde y diverge (explode ou muda de sinal
    abruptamente).

    Args:
        funcao_avaliar: callable(float) -> float|None ou string com expressão.
        x_min, x_max: intervalo de busca.
        num_pontos: resolução da busca.

    Returns:
        Lista de valores x onde existem assíntotas verticais.
    """
    if isinstance(funcao_avaliar, str):
        expr_preparada = _preparar_expressao(funcao_avaliar)
        avaliar = lambda val_x: _avaliar_seguro(expr_preparada, val_x)
    else:
        avaliar = funcao_avaliar

    passo = (x_max - x_min) / (num_pontos - 1)
    assintotas = []

    y_anterior = avaliar(x_min)
    for i in range(1, num_pontos):
        val_x = x_min + i * passo
        val_y = avaliar(val_x)

        if val_y is None and y_anterior is not None:
            # Busca binária para refinar a posição da assíntota
            a, b = val_x - passo, val_x
            for _ in range(50):
                meio = (a + b) / 2
                y_meio = avaliar(meio)
                if y_meio is None or abs(y_meio) > _THRESHOLD_INFINITO:
                    b = meio
                else:
                    a = meio
            assintotas.append(round(b, 6))
        elif val_y is not None and y_anterior is not None:
            if abs(val_y - y_anterior) > _THRESHOLD_DESCONTINUIDADE:
                # Mudança abrupta — provável assíntota no intervalo
                a, b = val_x - passo, val_x
                for _ in range(50):
                    meio = (a + b) / 2
                    y_meio = avaliar(meio)
                    if y_meio is None or abs(y_meio) > _THRESHOLD_INFINITO:
                        b = meio
                    else:
                        if abs(y_meio) > abs(y_anterior) * 10:
                            a = meio
                        else:
                            b = meio
                assintotas.append(round((a + b) / 2, 6))

        y_anterior = val_y

    # Remover duplicatas próximas
    if not assintotas:
        return []

    assintotas.sort()
    resultado = [assintotas[0]]
    for a in assintotas[1:]:
        if abs(a - resultado[-1]) > passo * 2:
            resultado.append(a)

    return resultado
