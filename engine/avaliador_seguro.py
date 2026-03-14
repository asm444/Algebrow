"""Avaliador seguro de expressões matemáticas via AST walking.

NÃO usa eval(). Percorre a árvore AST nó a nó e aceita apenas:
- Constantes numéricas (int, float)
- Nomes do namespace permitido (variáveis e funções matemáticas)
- Operações binárias e unárias
- Chamadas de funções do namespace

Qualquer outro nó (Attribute, Lambda, Import, Comprehension) é rejeitado.
"""

import ast
import math
import operator

NAMESPACE_PADRAO = {
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

_OPS_BIN = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

_OPS_UN = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _avaliar_no(node, ns):
    """Percorre AST recursivamente avaliando apenas nós seguros."""
    if isinstance(node, ast.Expression):
        return _avaliar_no(node.body, ns)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Constante não numérica: {node.value!r}")
    if isinstance(node, ast.Name):
        if node.id in ns:
            val = ns[node.id]
            return val if callable(val) else float(val)
        raise ValueError(f"Nome não permitido: {node.id}")
    if isinstance(node, ast.BinOp):
        op = type(node.op)
        if op not in _OPS_BIN:
            raise ValueError(f"Operador não permitido: {op.__name__}")
        return _OPS_BIN[op](_avaliar_no(node.left, ns), _avaliar_no(node.right, ns))
    if isinstance(node, ast.UnaryOp):
        op = type(node.op)
        if op not in _OPS_UN:
            raise ValueError(f"Operador unário não permitido: {op.__name__}")
        return _OPS_UN[op](_avaliar_no(node.operand, ns))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Apenas chamadas de funções simples permitidas")
        nome = node.func.id
        if nome not in ns or not callable(ns[nome]):
            raise ValueError(f"Função não permitida: {nome}")
        args = [_avaliar_no(a, ns) for a in node.args]
        return ns[nome](*args)
    raise ValueError(f"Nó AST não permitido: {type(node).__name__}")


def preparar_expressao(expr: str) -> str:
    """Prepara expressão: ^ → **, multiplicação implícita (2x → 2*x)."""
    expr = expr.strip().replace('^', '**')
    resultado = []
    for i, c in enumerate(expr):
        resultado.append(c)
        if i + 1 < len(expr):
            prox = expr[i + 1]
            if (c.isdigit() or c == '.') and (prox.isalpha() or prox == '('):
                resultado.append('*')
            elif c == ')' and (prox.isalpha() or prox.isdigit() or prox == '('):
                resultado.append('*')
            elif c.isalpha() and prox.isdigit():
                resultado.append('*')
    return ''.join(resultado)


def avaliar_seguro(expr_str: str, variaveis: dict = None) -> float:
    """Avalia expressão matemática de forma segura via AST walking.

    NÃO usa eval(). Percorre ast.parse(mode='eval') nó a nó.

    Args:
        expr_str: expressão como "sin(x) + 2*x^2"
        variaveis: dict de variáveis, ex: {'x': 1.5}

    Returns:
        Resultado float.
    """
    ns = dict(NAMESPACE_PADRAO)
    if variaveis:
        ns.update(variaveis)
    expr = preparar_expressao(expr_str)
    tree = ast.parse(expr, mode='eval')
    return float(_avaliar_no(tree, ns))
