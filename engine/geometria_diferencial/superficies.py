"""Superficies parametricas — formas fundamentais e curvaturas.

Toda manipulacao simbolica via NoExpressao, sem sympy.
"""

from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.derivada import derivar, simplificar_no
from engine.calculo.multivariavel import derivada_parcial
from engine.basic.passo import Passo, Historico
from .auxiliares import produto_escalar, produto_vetorial, norma


class SuperficieParametrica:
    """Superficie sigma(u,v) = (x(u,v), y(u,v), z(u,v))."""

    def __init__(self, componentes: list[NoExpressao],
                 parametros: list[str] = None):
        if parametros is None:
            parametros = ['u', 'v']
        self.componentes = componentes  # [x(u,v), y(u,v), z(u,v)]
        self.parametros = parametros

    # ------------------------------------------------------------------
    # Derivadas parciais
    # ------------------------------------------------------------------

    def derivadas_parciais(self) -> tuple:
        """sigma_u e sigma_v — derivar cada componente em u e v.

        Retorna (sigma_u: list, sigma_v: list, Historico).
        """
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Calculando derivadas parciais da superficie',
            regra='Derivadas parciais',
        ))

        u, v = self.parametros

        sigma_u = []
        for c in self.componentes:
            dc = derivada_parcial(c, u, historico)
            sigma_u.append(dc)

        sigma_v = []
        for c in self.componentes:
            dc = derivada_parcial(c, v, historico)
            sigma_v.append(dc)

        historico.adicionar(Passo(
            nivel=1,
            descricao='Derivadas parciais calculadas',
            regra='Derivadas parciais',
        ))

        return sigma_u, sigma_v, historico

    # ------------------------------------------------------------------
    # Primeira forma fundamental
    # ------------------------------------------------------------------

    def primeira_forma_fundamental(self) -> tuple:
        """I = E du^2 + 2F dudv + G dv^2.

        E = sigma_u . sigma_u
        F = sigma_u . sigma_v
        G = sigma_v . sigma_v

        Retorna (E, F, G, Historico).
        """
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Calculando primeira forma fundamental',
            regra='Primeira forma fundamental',
        ))

        sigma_u, sigma_v, hist_d = self.derivadas_parciais()
        for p in hist_d.todos():
            historico.adicionar(p)

        E = simplificar_no(produto_escalar(sigma_u, sigma_u))
        F = simplificar_no(produto_escalar(sigma_u, sigma_v))
        G = simplificar_no(produto_escalar(sigma_v, sigma_v))

        historico.adicionar(Passo(
            nivel=1,
            descricao=f'E = {E.representacao_latex()}, F = {F.representacao_latex()}, G = {G.representacao_latex()}',
            regra='Primeira forma fundamental',
        ))

        return E, F, G, historico

    # ------------------------------------------------------------------
    # Vetor normal
    # ------------------------------------------------------------------

    def vetor_normal(self) -> tuple:
        """N = (sigma_u x sigma_v) / |sigma_u x sigma_v|.

        Retorna (lista de NoExpressao, Historico).
        """
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Calculando vetor normal da superficie',
            regra='Vetor normal',
        ))

        sigma_u, sigma_v, hist_d = self.derivadas_parciais()
        for p in hist_d.todos():
            historico.adicionar(p)

        cruz = produto_vetorial(sigma_u, sigma_v)
        n = norma(cruz)

        normal = [simplificar_no(op('/', c, n)) for c in cruz]

        historico.adicionar(Passo(
            nivel=1,
            descricao='Vetor normal calculado',
            regra='Vetor normal',
        ))

        return normal, historico

    # ------------------------------------------------------------------
    # Segunda forma fundamental
    # ------------------------------------------------------------------

    def segunda_forma_fundamental(self) -> tuple:
        """II = e du^2 + 2f dudv + g dv^2.

        e = sigma_uu . N
        f = sigma_uv . N
        g = sigma_vv . N

        Retorna (e, f, g, Historico).
        """
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Calculando segunda forma fundamental',
            regra='Segunda forma fundamental',
        ))

        u_var, v_var = self.parametros

        sigma_u, sigma_v, hist_d = self.derivadas_parciais()
        for p in hist_d.todos():
            historico.adicionar(p)

        # Segundas derivadas
        sigma_uu = [simplificar_no(derivada_parcial(c, u_var, historico)) for c in sigma_u]
        sigma_uv = [simplificar_no(derivada_parcial(c, v_var, historico)) for c in sigma_u]
        sigma_vv = [simplificar_no(derivada_parcial(c, v_var, historico)) for c in sigma_v]

        # Vetor normal
        normal, hist_n = self.vetor_normal()
        for p in hist_n.todos():
            historico.adicionar(p)

        e = simplificar_no(produto_escalar(sigma_uu, normal))
        f = simplificar_no(produto_escalar(sigma_uv, normal))
        g = simplificar_no(produto_escalar(sigma_vv, normal))

        historico.adicionar(Passo(
            nivel=1,
            descricao=f'e = {e.representacao_latex()}, f = {f.representacao_latex()}, g = {g.representacao_latex()}',
            regra='Segunda forma fundamental',
        ))

        return e, f, g, historico

    # ------------------------------------------------------------------
    # Curvatura gaussiana
    # ------------------------------------------------------------------

    def curvatura_gaussiana(self) -> tuple:
        """K = (eg - f^2) / (EG - F^2).

        Retorna (NoExpressao, Historico).
        """
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Calculando curvatura gaussiana',
            regra='Curvatura gaussiana',
        ))

        E, F, G, hist_1 = self.primeira_forma_fundamental()
        for p in hist_1.todos():
            historico.adicionar(p)

        e, f, g, hist_2 = self.segunda_forma_fundamental()
        for p in hist_2.todos():
            historico.adicionar(p)

        # K = (eg - f^2) / (EG - F^2)
        numerador = simplificar_no(op('-', op('*', e, g), op('^', f, num('2'))))
        denominador = simplificar_no(op('-', op('*', E, G), op('^', F, num('2'))))
        resultado = simplificar_no(op('/', numerador, denominador))

        historico.adicionar(Passo(
            nivel=1,
            descricao='Curvatura gaussiana calculada',
            latex_depois=f'K = {resultado.representacao_latex()}',
            regra='Curvatura gaussiana',
        ))

        return resultado, historico

    # ------------------------------------------------------------------
    # Curvatura media
    # ------------------------------------------------------------------

    def curvatura_media(self) -> tuple:
        """H = (eG - 2fF + gE) / 2(EG - F^2).

        Retorna (NoExpressao, Historico).
        """
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Calculando curvatura media',
            regra='Curvatura media',
        ))

        E, F, G, hist_1 = self.primeira_forma_fundamental()
        for p in hist_1.todos():
            historico.adicionar(p)

        e, f, g, hist_2 = self.segunda_forma_fundamental()
        for p in hist_2.todos():
            historico.adicionar(p)

        # H = (eG - 2fF + gE) / (2*(EG - F^2))
        termo1 = op('*', e, G)
        termo2 = op('*', op('*', num('2'), f), F)
        termo3 = op('*', g, E)
        numerador = simplificar_no(op('+', op('-', termo1, termo2), termo3))

        det = simplificar_no(op('-', op('*', E, G), op('^', F, num('2'))))
        denominador = simplificar_no(op('*', num('2'), det))

        resultado = simplificar_no(op('/', numerador, denominador))

        historico.adicionar(Passo(
            nivel=1,
            descricao='Curvatura media calculada',
            latex_depois=f'H = {resultado.representacao_latex()}',
            regra='Curvatura media',
        ))

        return resultado, historico

    # ------------------------------------------------------------------
    # LaTeX
    # ------------------------------------------------------------------

    def representacao_latex(self) -> str:
        """sigma(u,v) = (x(u,v), y(u,v), z(u,v))."""
        params = ', '.join(self.parametros)
        comps = ', '.join(c.representacao_latex() for c in self.componentes)
        return f'\\sigma({params}) = ({comps})'
