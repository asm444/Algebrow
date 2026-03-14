"""Cálculo de Variações: equação de Euler-Lagrange."""

from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.derivada import derivar, simplificar_no
from engine.basic.passo import Passo, Historico


def euler_lagrange(F: NoExpressao, y_var: str = 'y', yp_var: str = "y'",
                   x_var: str = 'x') -> tuple:
    """Equação de Euler-Lagrange: dF/dy - d/dx(dF/dy') = 0.

    F é o integrando do funcional J[y] = integral F(x, y, y')dx.
    Retorna (equacao: NoExpressao, Historico com passos).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao='Aplicando equação de Euler-Lagrange: dF/dy - d/dx(dF/dy\') = 0',
        latex_antes=F.representacao_latex(),
        regra='Euler-Lagrange',
    ))

    # Passo 1: dF/dy
    hist.adicionar(Passo(
        nivel=2,
        descricao=f'Calculando dF/d{y_var}',
        regra='Derivada parcial em y',
    ))
    dF_dy = simplificar_no(derivar(F, y_var, hist))
    hist.adicionar(Passo(
        nivel=2,
        descricao=f'dF/d{y_var} = {dF_dy.representacao_latex()}',
        latex_depois=dF_dy.representacao_latex(),
        regra='Resultado dF/dy',
    ))

    # Passo 2: dF/dy'
    hist.adicionar(Passo(
        nivel=2,
        descricao=f'Calculando dF/d{yp_var}',
        regra='Derivada parcial em y\'',
    ))
    dF_dyp = simplificar_no(derivar(F, yp_var, hist))
    hist.adicionar(Passo(
        nivel=2,
        descricao=f'dF/d{yp_var} = {dF_dyp.representacao_latex()}',
        latex_depois=dF_dyp.representacao_latex(),
        regra='Resultado dF/dy\'',
    ))

    # Passo 3: d/dx(dF/dy')
    hist.adicionar(Passo(
        nivel=2,
        descricao=f'd/d{x_var}(dF/d{yp_var})',
        regra='Derivada total em x',
    ))
    d_dx_dF_dyp = simplificar_no(derivar(dF_dyp, x_var, hist))
    hist.adicionar(Passo(
        nivel=2,
        descricao=f'd/d{x_var}(dF/d{yp_var}) = {d_dx_dF_dyp.representacao_latex()}',
        latex_depois=d_dx_dF_dyp.representacao_latex(),
        regra='Resultado d/dx(dF/dy\')',
    ))

    # Passo 4: dF/dy - d/dx(dF/dy') = 0
    equacao = simplificar_no(op('-', dF_dy, d_dx_dF_dyp))
    hist.adicionar(Passo(
        nivel=0,
        descricao=f'Equação de Euler-Lagrange: {equacao.representacao_latex()} = 0',
        latex_depois=f'{equacao.representacao_latex()} = 0',
        regra='Euler-Lagrange - resultado',
    ))

    return (equacao, hist)


def braquisticrona() -> tuple:
    """Resolve o problema clássico da braquistócrona.

    F = sqrt((1+y'^2)/(2gy)) -> ciclóide.
    Retorna (descricao_latex, Historico).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao='Problema da braquistócrona: minimizar tempo de descida',
        latex_antes='J[y] = \\int \\sqrt{\\frac{1+y\'^2}{2gy}} dx',
        regra='Braquistócrona',
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao='O funcional é F = sqrt((1+y\'^2)/(2gy))',
        regra='Integrando',
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao='Como F não depende explicitamente de x, aplica-se a integral primeira de Beltrami',
        latex_depois="F - y' \\frac{\\partial F}{\\partial y'} = C",
        regra='Integral de Beltrami',
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao='Após simplificação: y(1+y\'^2) = constante',
        regra='Simplificação',
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao='A solução é uma ciclóide: x = a(t - sin(t)), y = a(1 - cos(t))',
        latex_depois='x = a(t - \\sin t), \\quad y = a(1 - \\cos t)',
        regra='Solução paramétrica',
    ))

    latex = (
        'x = a(t - \\sin t), \\quad y = a(1 - \\cos t) '
        '\\quad \\text{(ciclóide)}'
    )
    hist.adicionar(Passo(
        nivel=0,
        descricao='Solução da braquistócrona: ciclóide',
        latex_depois=latex,
        regra='Resultado',
    ))

    return (latex, hist)


def geodesica_plano() -> tuple:
    """Geodésica no plano: F = sqrt(1+y'^2) -> reta.

    Retorna (descricao_latex, Historico).
    """
    hist = Historico()

    # F = sqrt(1 + y'^2)
    yp = var("y'")
    F = func('sqrt', op('+', num('1'), op('^', yp, num('2'))))

    hist.adicionar(Passo(
        nivel=1,
        descricao='Geodésica no plano: minimizar comprimento de arco',
        latex_antes='J[y] = \\int \\sqrt{1 + y\'^2} \\, dx',
        regra='Geodésica plana',
    ))

    # Euler-Lagrange simbólica
    equacao, hist_el = euler_lagrange(F, y_var='y', yp_var="y'", x_var='x')
    for p in hist_el.todos():
        hist.adicionar(p)

    # A equação resultante implica y'' = 0
    hist.adicionar(Passo(
        nivel=2,
        descricao='A equação de Euler-Lagrange se reduz a y\'\' = 0',
        latex_depois="y'' = 0",
        regra='Simplificação',
    ))

    latex = "y'' = 0 \\implies y = ax + b \\quad \\text{(reta)}"
    hist.adicionar(Passo(
        nivel=0,
        descricao='Geodésica no plano: reta y = ax + b',
        latex_depois=latex,
        regra='Resultado',
    ))

    return (latex, hist)


def geodesica_esfera() -> tuple:
    """Geodésica na esfera: grande círculo.

    Retorna (descricao_latex, Historico).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao='Geodésica na esfera de raio R',
        latex_antes='ds^2 = R^2(d\\theta^2 + \\sin^2\\theta \\, d\\phi^2)',
        regra='Métrica esférica',
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao='Funcional: L = integral sqrt(1 + sin^2(theta) * phi\'^2) d_theta',
        regra='Funcional de comprimento',
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao='Como L não depende explicitamente de phi, dL/d(phi\') = const',
        latex_depois="\\frac{\\sin^2\\theta \\, \\phi'}{\\sqrt{1 + \\sin^2\\theta \\, \\phi'^2}} = C",
        regra='Integral primeira',
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao='A solução é um grande círculo (interseção de plano pelo centro com a esfera)',
        regra='Solução',
    ))

    latex = '\\text{Grande círculo: } \\cos\\theta = A\\sin\\theta\\cos\\phi + B\\sin\\theta\\sin\\phi'
    hist.adicionar(Passo(
        nivel=0,
        descricao='Geodésica na esfera: grande círculo',
        latex_depois=latex,
        regra='Resultado',
    ))

    return (latex, hist)


def principio_hamilton() -> tuple:
    """S = integral(T-V)dt, delta_S=0 -> Euler-Lagrange.

    Retorna (descricao_latex, Historico).
    """
    hist = Historico()
    hist.adicionar(Passo(
        nivel=1,
        descricao='Princípio de Hamilton: a ação S é estacionária',
        latex_antes='S = \\int_{t_1}^{t_2} (T - V) \\, dt = \\int_{t_1}^{t_2} L(q, \\dot{q}, t) \\, dt',
        regra='Princípio de Hamilton',
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao='Variação delta_S = 0 com extremidades fixas',
        regra='Condição de estacionariedade',
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao='Integração por partes e lema fundamental do cálculo variacional',
        regra='Derivação',
    ))

    hist.adicionar(Passo(
        nivel=2,
        descricao='Resultado: equações de Euler-Lagrange para cada coordenada generalizada',
        latex_depois="\\frac{\\partial L}{\\partial q_i} - \\frac{d}{dt}\\frac{\\partial L}{\\partial \\dot{q}_i} = 0",
        regra='Equações de Euler-Lagrange',
    ))

    latex = (
        "\\delta S = 0 \\implies "
        "\\frac{\\partial L}{\\partial q_i} - "
        "\\frac{d}{dt}\\frac{\\partial L}{\\partial \\dot{q}_i} = 0"
    )
    hist.adicionar(Passo(
        nivel=0,
        descricao='Princípio de Hamilton implica equações de Euler-Lagrange',
        latex_depois=latex,
        regra='Resultado',
    ))

    return (latex, hist)
