"""Equações Diferenciais Ordinárias — Volume 4 Guidorizzi.

Métodos implementados:
- EDO separável
- EDO linear de 1ª ordem (fator integrante)
- EDO linear de 2ª ordem com coeficientes constantes (equação característica)
- EDO de Bernoulli
- EDO exata
- Método de Euler (numérico)
"""

import math

from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.derivada import derivar, simplificar_no
from engine.calculo.integral import integrar, _integrar_interno
from engine.basic.passo import Passo, Historico


def _copiar_no(no: NoExpressao) -> NoExpressao:
    """Copia profunda de um NoExpressao."""
    filhos = [_copiar_no(f) for f in no.filhos]
    return NoExpressao(no.tipo, no.valor, filhos)


def _avaliar_expressao_segura(expressao: str, x: float, y: float) -> float:
    """Avalia uma expressão matemática string de forma restrita.

    Apenas permite variáveis x, y e funções matemáticas seguras.
    Não expõe builtins nem módulos.
    """
    permitidos = {
        'x': x, 'y': y,
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'exp': math.exp, 'log': math.log, 'sqrt': math.sqrt,
        'abs': abs, 'pi': math.pi, 'e': math.e,
    }
    # Compilar a expressão para validar sintaxe antes de avaliar
    codigo = compile(expressao, '<edo>', 'eval')
    # Verificar que não há nomes proibidos nos nomes usados
    for nome in codigo.co_names:
        if nome not in permitidos:
            raise ValueError(f"Nome não permitido na expressão: '{nome}'")
    return float(codigo.co_consts[0]) if not codigo.co_names and len(codigo.co_consts) == 1 \
        else float(_eval_compilado(codigo, permitidos))


def _eval_compilado(codigo, namespace: dict) -> float:
    """Executa código compilado em namespace restrito."""
    # Usar eval com builtins desabilitados e namespace controlado
    return eval(codigo, {"__builtins__": {}}, namespace)  # noqa: S307 — namespace restrito


def edo_separavel(f_x: NoExpressao, g_y: NoExpressao,
                  variavel_x: str = 'x', variavel_y: str = 'y') -> tuple:
    """Resolve EDO separável: g(y)dy = f(x)dx

    Método: Integrar ambos os lados.
    ∫g(y)dy = ∫f(x)dx + C

    Retorna (solucao: NoExpressao, Historico)
    """
    historico = Historico(verbosidade=3)

    latex_f = f_x.representacao_latex()
    latex_g = g_y.representacao_latex()

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'EDO separável: {latex_g} d{variavel_y} = {latex_f} d{variavel_x}',
        latex_antes=f'{latex_g} \\, d{variavel_y} = {latex_f} \\, d{variavel_x}',
        regra='Identificação de EDO separável',
        justificativa='Os termos em x e y podem ser separados em lados distintos.',
    ))

    # Integrar lado esquerdo: ∫g(y)dy (sem +C)
    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Integrar lado esquerdo: ∫{latex_g} d{variavel_y}',
        latex_antes=f'\\int {latex_g} \\, d{variavel_y}',
        regra='Integração do lado esquerdo',
    ))
    int_g = _integrar_interno(g_y, variavel_y, historico)

    # Integrar lado direito: ∫f(x)dx (sem +C)
    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Integrar lado direito: ∫{latex_f} d{variavel_x}',
        latex_antes=f'\\int {latex_f} \\, d{variavel_x}',
        regra='Integração do lado direito',
    ))
    int_f = _integrar_interno(f_x, variavel_x, historico)

    # Solução: int_g = int_f + C
    solucao = op('-', int_g, op('+', int_f, var('C')))
    solucao = simplificar_no(solucao)

    latex_sol_esq = int_g.representacao_latex()
    latex_sol_dir = int_f.representacao_latex()

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Solução: {latex_sol_esq} = {latex_sol_dir} + C',
        latex_depois=f'{latex_sol_esq} = {latex_sol_dir} + C',
        regra='Solução geral da EDO separável',
    ))

    return (solucao, historico)


def edo_linear_1ordem(p: NoExpressao, q: NoExpressao,
                      variavel: str = 'x') -> tuple:
    """Resolve EDO linear de 1ª ordem: y' + p(x)·y = q(x)

    Método: Fator integrante μ(x) = e^(∫p(x)dx)
    Solução: y = (1/μ)·∫μ·q dx + C/μ

    Retorna (solucao: NoExpressao, Historico com passos)
    """
    historico = Historico(verbosidade=3)

    latex_p = p.representacao_latex()
    latex_q = q.representacao_latex()

    historico.adicionar(Passo(
        nivel=1,
        descricao=f"EDO linear de 1ª ordem: y' + ({latex_p})·y = {latex_q}",
        latex_antes=f"y' + ({latex_p}) \\cdot y = {latex_q}",
        regra='Identificação de EDO linear de 1ª ordem',
    ))

    # Passo 1: Calcular ∫p(x)dx (sem constante)
    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Calcular ∫p(x)dx = ∫{latex_p} d{variavel}',
        regra='Integral de p(x)',
    ))
    int_p = _integrar_interno(p, variavel, historico)
    int_p = simplificar_no(int_p)

    # Passo 2: Fator integrante μ = e^(∫p dx)
    mu = func('exp', int_p)
    latex_mu = mu.representacao_latex()

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Fator integrante: μ(x) = e^(∫p dx) = {latex_mu}',
        latex_depois=f'\\mu({variavel}) = {latex_mu}',
        regra='Fator integrante',
        justificativa='O fator integrante torna o lado esquerdo uma derivada exata.',
    ))

    # Passo 3: Calcular ∫μ·q dx (sem constante)
    mu_q = simplificar_no(op('*', _copiar_no(mu), q))
    latex_mu_q = mu_q.representacao_latex()

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Calcular ∫μ·q dx = ∫{latex_mu_q} d{variavel}',
        regra='Integral de μ·q',
    ))
    int_mu_q = _integrar_interno(mu_q, variavel, historico)
    int_mu_q = simplificar_no(int_mu_q)

    # Solução: y = (1/μ)·(∫μ·q dx + C)
    inv_mu = op('/', num('1'), _copiar_no(mu))
    soma_int_c = op('+', int_mu_q, var('C'))
    solucao = simplificar_no(op('*', inv_mu, soma_int_c))

    latex_sol = solucao.representacao_latex()
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Solução: y = (1/μ)·(∫μ·q dx + C) = {latex_sol}',
        latex_depois=f'y = {latex_sol}',
        regra='Solução geral da EDO linear de 1ª ordem',
    ))

    return (solucao, historico)


def edo_linear_2ordem_coef_cte(a: str, b: str, c: str) -> tuple:
    """Resolve EDO linear de 2ª ordem com coeficientes constantes:
    ay'' + by' + cy = 0

    Método: Equação característica ar² + br + c = 0
    - Raízes reais distintas: y = C₁e^(r₁x) + C₂e^(r₂x)
    - Raiz dupla: y = (C₁ + C₂x)e^(rx)
    - Raízes complexas: y = e^(αx)(C₁cos(βx) + C₂sin(βx))

    Retorna (solucao_geral: str em LaTeX, tipo: str, Historico)
    """
    historico = Historico(verbosidade=3)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f"EDO: {a}y'' + {b}y' + {c}y = 0",
        latex_antes=f"{a}y'' + {b}y' + {c}y = 0",
        regra='Identificação de EDO linear 2ª ordem com coef. constantes',
    ))

    # Equação característica: ar² + br + c = 0
    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Equação característica: {a}r² + {b}r + {c} = 0',
        latex_antes=f'{a}r^2 + {b}r + {c} = 0',
        regra='Equação característica',
        justificativa='Substituir y = e^(rx) na EDO leva à equação característica.',
    ))

    a_f = float(a)
    b_f = float(b)
    c_f = float(c)

    # Discriminante
    delta = b_f * b_f - 4 * a_f * c_f

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Discriminante: Δ = {b}² - 4·{a}·{c} = {delta}',
        latex_depois=f'\\Delta = {delta}',
        regra='Cálculo do discriminante',
    ))

    if delta > 0:
        # Raízes reais distintas
        r1 = (-b_f + math.sqrt(delta)) / (2 * a_f)
        r2 = (-b_f - math.sqrt(delta)) / (2 * a_f)

        # Formatar raízes como inteiro se possível
        r1_str = str(int(r1)) if r1 == int(r1) else str(r1)
        r2_str = str(int(r2)) if r2 == int(r2) else str(r2)

        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Δ > 0: duas raízes reais distintas r₁ = {r1_str}, r₂ = {r2_str}',
            latex_depois=f'r_1 = {r1_str}, \\; r_2 = {r2_str}',
            regra='Raízes reais distintas',
        ))

        solucao = f'C_1 e^{{{r1_str}x}} + C_2 e^{{{r2_str}x}}'

        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Solução geral: y = C₁e^({r1_str}x) + C₂e^({r2_str}x)',
            latex_depois=f'y = {solucao}',
            regra='Solução geral — raízes reais distintas',
        ))

        return (solucao, 'raizes_reais_distintas', historico)

    elif delta == 0:
        # Raiz dupla
        r = -b_f / (2 * a_f)
        r_str = str(int(r)) if r == int(r) else str(r)

        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Δ = 0: raiz dupla r = {r_str}',
            latex_depois=f'r = {r_str}',
            regra='Raiz dupla',
        ))

        solucao = f'(C_1 + C_2 x) e^{{{r_str}x}}'

        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Solução geral: y = (C₁ + C₂x)e^({r_str}x)',
            latex_depois=f'y = {solucao}',
            regra='Solução geral — raiz dupla',
        ))

        return (solucao, 'raiz_dupla', historico)

    else:
        # Raízes complexas: α ± βi
        alpha = -b_f / (2 * a_f)
        beta = math.sqrt(abs(delta)) / (2 * a_f)

        alpha_str = str(int(alpha)) if alpha == int(alpha) else str(alpha)
        beta_str = str(int(beta)) if beta == int(beta) else str(beta)

        historico.adicionar(Passo(
            nivel=2,
            descricao=f'Δ < 0: raízes complexas α ± βi com α = {alpha_str}, β = {beta_str}',
            latex_depois=f'\\alpha = {alpha_str}, \\; \\beta = {beta_str}',
            regra='Raízes complexas conjugadas',
        ))

        # Construir solução LaTeX
        if alpha == 0:
            # y = C₁cos(βx) + C₂sin(βx)
            if beta_str == '1':
                solucao = f'C_1 \\cos(x) + C_2 \\sin(x)'
            else:
                solucao = f'C_1 \\cos({beta_str}x) + C_2 \\sin({beta_str}x)'
        else:
            if beta_str == '1':
                solucao = f'e^{{{alpha_str}x}}(C_1 \\cos(x) + C_2 \\sin(x))'
            else:
                solucao = f'e^{{{alpha_str}x}}(C_1 \\cos({beta_str}x) + C_2 \\sin({beta_str}x))'

        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Solução geral: y = {solucao}',
            latex_depois=f'y = {solucao}',
            regra='Solução geral — raízes complexas',
        ))

        return (solucao, 'raizes_complexas', historico)


def edo_bernoulli(p: NoExpressao, q: NoExpressao, n: str,
                  variavel: str = 'x') -> tuple:
    """Resolve EDO de Bernoulli: y' + p(x)·y = q(x)·y^n

    Substituição: v = y^(1-n), transforma em EDO linear.

    Retorna (solucao: str, Historico)
    """
    historico = Historico(verbosidade=3)

    n_f = float(n)
    latex_p = p.representacao_latex()
    latex_q = q.representacao_latex()

    historico.adicionar(Passo(
        nivel=1,
        descricao=f"EDO de Bernoulli: y' + ({latex_p})·y = ({latex_q})·y^{n}",
        latex_antes=f"y' + ({latex_p})y = ({latex_q})y^{{{n}}}",
        regra='Identificação de EDO de Bernoulli',
    ))

    # Substituição v = y^(1-n)
    m = 1 - n_f
    m_str = str(int(m)) if m == int(m) else str(m)

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Substituição: v = y^(1-n) = y^{m_str}',
        latex_depois=f'v = y^{{{m_str}}}',
        regra='Substituição de Bernoulli',
        justificativa=f'Com n = {n}, fazemos v = y^(1-{n}) = y^{m_str} para linearizar.',
    ))

    # v' = (1-n)·y^(-n)·y' => v' + (1-n)·p·v = (1-n)·q
    # EDO linear em v: v' + (1-n)·p(x)·v = (1-n)·q(x)
    coef = num(m_str)
    p_novo = simplificar_no(op('*', coef, _copiar_no(p)))
    q_novo = simplificar_no(op('*', _copiar_no(coef), _copiar_no(q)))

    historico.adicionar(Passo(
        nivel=2,
        descricao=f"EDO linear em v: v' + ({m_str})·({latex_p})·v = ({m_str})·({latex_q})",
        regra='Transformação em EDO linear',
    ))

    # Resolver a EDO linear resultante
    try:
        sol_v, hist_linear = edo_linear_1ordem(p_novo, q_novo, variavel)
        # Transferir passos
        for passo in hist_linear.todos():
            historico.adicionar(passo)

        latex_v = sol_v.representacao_latex()

        # Reverter substituição: y^(1-n) = v => y = v^(1/(1-n))
        inv_m_str = f'1/{m_str}' if m != 1 else '1'
        solucao = f'y = ({latex_v})^{{{inv_m_str}}}'

        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Reverter substituição: {solucao}',
            latex_depois=solucao,
            regra='Reversão da substituição de Bernoulli',
        ))

        return (solucao, historico)
    except (ValueError, ZeroDivisionError) as e:
        historico.adicionar(Passo(
            nivel=1,
            descricao=f'Não foi possível resolver a EDO linear resultante: {e}',
            regra='Erro na resolução',
        ))
        return (f'Erro: {e}', historico)


def edo_exata(M: NoExpressao, N: NoExpressao,
              var_x: str = 'x', var_y: str = 'y') -> tuple:
    """Resolve EDO exata: M(x,y)dx + N(x,y)dy = 0

    Condição: ∂M/∂y = ∂N/∂x
    Solução: F(x,y) = C onde ∂F/∂x = M e ∂F/∂y = N

    Retorna (solucao: str, Historico)
    """
    historico = Historico(verbosidade=3)

    latex_M = M.representacao_latex()
    latex_N = N.representacao_latex()

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'EDO: ({latex_M})dx + ({latex_N})dy = 0',
        latex_antes=f'({latex_M})d{var_x} + ({latex_N})d{var_y} = 0',
        regra='Identificação de EDO exata',
    ))

    # Verificar condição de exatidão: ∂M/∂y = ∂N/∂x
    dM_dy = simplificar_no(derivar(M, var_y))
    dN_dx = simplificar_no(derivar(N, var_x))

    latex_dM_dy = dM_dy.representacao_latex()
    latex_dN_dx = dN_dx.representacao_latex()

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Verificar exatidão: ∂M/∂y = {latex_dM_dy}, ∂N/∂x = {latex_dN_dx}',
        latex_depois=f'\\frac{{\\partial M}}{{\\partial {var_y}}} = {latex_dM_dy}, '
                     f'\\; \\frac{{\\partial N}}{{\\partial {var_x}}} = {latex_dN_dx}',
        regra='Condição de exatidão',
    ))

    # Passo 1: F(x,y) = ∫M dx (tratando y como constante)
    historico.adicionar(Passo(
        nivel=2,
        descricao=f'Calcular F = ∫M dx = ∫{latex_M} d{var_x}',
        regra='Integral de M em relação a x',
    ))
    int_M = _integrar_interno(M, var_x, historico)
    int_M = simplificar_no(int_M)
    latex_int_M = int_M.representacao_latex()

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'F(x,y) = {latex_int_M} + g(y), onde g(y) é função arbitrária de y',
        latex_depois=f'F({var_x},{var_y}) = {latex_int_M} + g({var_y})',
        regra='Forma parcial de F',
    ))

    # Passo 2: ∂F/∂y = ∂(∫M dx)/∂y + g'(y) = N
    # => g'(y) = N - ∂(∫M dx)/∂y
    d_intM_dy = simplificar_no(derivar(int_M, var_y))
    latex_d = d_intM_dy.representacao_latex()

    # g'(y) = N - d_intM_dy
    g_prime = simplificar_no(op('-', _copiar_no(N), d_intM_dy))
    latex_gp = g_prime.representacao_latex()

    historico.adicionar(Passo(
        nivel=2,
        descricao=f"g'(y) = N - ∂(∫M dx)/∂y = {latex_N} - {latex_d} = {latex_gp}",
        latex_depois=f"g'({var_y}) = {latex_gp}",
        regra='Determinar g\'(y)',
    ))

    # Passo 3: g(y) = ∫g'(y) dy
    int_gp = _integrar_interno(g_prime, var_y, historico)
    int_gp = simplificar_no(int_gp)
    latex_g = int_gp.representacao_latex()

    historico.adicionar(Passo(
        nivel=2,
        descricao=f'g(y) = ∫g\'(y) dy = {latex_g}',
        latex_depois=f'g({var_y}) = {latex_g}',
        regra='Integral de g\'(y)',
    ))

    # Solução: F(x,y) = ∫M dx + g(y) = C
    F = simplificar_no(op('+', _copiar_no(int_M), int_gp))
    latex_F = F.representacao_latex()

    solucao = f'{latex_F} = C'

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Solução: F(x,y) = {latex_F} = C',
        latex_depois=f'{latex_F} = C',
        regra='Solução geral da EDO exata',
    ))

    return (solucao, historico)


def metodo_euler(f_derivada, x0: float, y0: float,
                 h: float, n_passos: int) -> tuple:
    """Método de Euler numérico para y' = f(x,y).

    y_{n+1} = y_n + h·f(x_n, y_n)

    f_derivada: callable(x, y) -> float OU string (ex: 'x + y')

    Retorna (pontos: list[(x,y)], Historico)
    """
    historico = Historico(verbosidade=3)

    # Se f_derivada é string, converter para callable com avaliação restrita
    if isinstance(f_derivada, str):
        expressao_str = f_derivada

        def f(x, y):
            return _avaliar_expressao_segura(expressao_str, x, y)
    else:
        f = f_derivada

    historico.adicionar(Passo(
        nivel=1,
        descricao=f"Método de Euler: y' = f(x,y), x₀={x0}, y₀={y0}, h={h}, n={n_passos}",
        regra='Método de Euler',
        justificativa='Aproximação numérica da solução por passos discretos.',
    ))

    pontos = [(x0, y0)]
    x_n = x0
    y_n = y0

    for i in range(n_passos):
        f_val = f(x_n, y_n)
        y_novo = y_n + h * f_val
        x_novo = x_n + h

        # Arredondar para evitar erros de ponto flutuante acumulados
        x_novo = round(x_novo, 12)
        y_novo = round(y_novo, 12)

        historico.adicionar(Passo(
            nivel=3,
            descricao=(f'Passo {i+1}: f({x_n:.4f}, {y_n:.4f}) = {f_val:.6f}, '
                       f'y_{i+1} = {y_n:.6f} + {h}·{f_val:.6f} = {y_novo:.6f}'),
            regra='Iteração de Euler',
        ))

        pontos.append((x_novo, y_novo))
        x_n = x_novo
        y_n = y_novo

    historico.adicionar(Passo(
        nivel=1,
        descricao=f'Resultado final: ({x_n:.4f}, {y_n:.6f}) após {n_passos} passos',
        regra='Resultado do Método de Euler',
    ))

    return (pontos, historico)
