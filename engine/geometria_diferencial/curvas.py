"""Curvas parametricas e referencial de Frenet-Serret.

Toda manipulacao simbolica via NoExpressao, sem sympy.
"""

from engine.calculo.arvore import NoExpressao, num, var, op, func
from engine.calculo.derivada import derivar, simplificar_no
from engine.basic.passo import Passo, Historico
from .auxiliares import produto_escalar, produto_vetorial, norma, norma_quadrada


class CurvaParametrica:
    """Curva parametrizada alpha(t) = (x(t), y(t), z(t))."""

    def __init__(self, componentes: list[NoExpressao], parametro: str = 't'):
        self.componentes = componentes  # [x(t), y(t), z(t)]
        self.parametro = parametro
        self.dimensao = len(componentes)

    # ------------------------------------------------------------------
    # Derivada da curva
    # ------------------------------------------------------------------

    def derivada(self) -> 'CurvaParametrica':
        """alpha'(t) — derivar cada componente."""
        novas = []
        for c in self.componentes:
            dc = simplificar_no(derivar(c, self.parametro))
            novas.append(dc)
        return CurvaParametrica(novas, self.parametro)

    # ------------------------------------------------------------------
    # Comprimento de arco
    # ------------------------------------------------------------------

    def comprimento_arco_formula(self) -> NoExpressao:
        """Retorna o integrando |alpha'(t)| = sqrt(x'^2 + y'^2 + z'^2)."""
        d = self.derivada()
        return norma(d.componentes)

    # ------------------------------------------------------------------
    # Curvatura
    # ------------------------------------------------------------------

    def curvatura(self) -> tuple:
        """Curvatura kappa(t).

        2D: kappa = |x'y'' - y'x''| / (x'^2 + y'^2)^(3/2)
        3D: kappa = |alpha' x alpha''| / |alpha'|^3

        Retorna (NoExpressao, Historico).
        """
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Calculando curvatura da curva parametrica',
            regra='Curvatura',
        ))

        d1 = self.derivada()
        d2 = d1.derivada()

        if self.dimensao == 2:
            historico.adicionar(Passo(
                nivel=2,
                descricao='Curvatura 2D: kappa = |x\'y\'\' - y\'x\'\'| / (x\'^2 + y\'^2)^(3/2)',
                regra='Curvatura 2D',
            ))
            x1, y1 = d1.componentes
            x2, y2 = d2.componentes

            # Numerador: |x'*y'' - y'*x''|
            cruz = simplificar_no(op('-', op('*', x1, y2), op('*', y1, x2)))
            numerador = func('abs', cruz)

            # Denominador: (x'^2 + y'^2)^(3/2)
            soma_quad = simplificar_no(op('+', op('^', x1, num('2')), op('^', y1, num('2'))))
            denominador = simplificar_no(op('^', soma_quad, op('/', num('3'), num('2'))))

            resultado = simplificar_no(op('/', numerador, denominador))

        elif self.dimensao == 3:
            historico.adicionar(Passo(
                nivel=2,
                descricao='Curvatura 3D: kappa = |alpha\' x alpha\'\'| / |alpha\'|^3',
                regra='Curvatura 3D',
            ))

            # alpha' x alpha''
            cruz = produto_vetorial(d1.componentes, d2.componentes)
            numerador = norma(cruz)

            # |alpha'|^3
            norma_d1 = norma(d1.componentes)
            denominador = simplificar_no(op('^', norma_d1, num('3')))

            resultado = simplificar_no(op('/', numerador, denominador))
        else:
            raise ValueError(f'Curvatura nao implementada para dimensao {self.dimensao}')

        historico.adicionar(Passo(
            nivel=1,
            descricao='Curvatura calculada',
            latex_depois=resultado.representacao_latex(),
            regra='Curvatura',
        ))

        return resultado, historico

    # ------------------------------------------------------------------
    # Torcao (3D)
    # ------------------------------------------------------------------

    def torcao(self) -> tuple:
        """Torcao tau(t) — apenas 3D.

        tau = (alpha' x alpha'') . alpha''' / |alpha' x alpha''|^2

        Retorna (NoExpressao, Historico).
        """
        if self.dimensao != 3:
            raise ValueError('Torcao definida apenas para curvas 3D')

        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Calculando torcao da curva 3D',
            regra='Torcao',
        ))

        d1 = self.derivada()
        d2 = d1.derivada()
        d3 = d2.derivada()

        # (alpha' x alpha'')
        cruz = produto_vetorial(d1.componentes, d2.componentes)

        # Numerador: (alpha' x alpha'') . alpha'''
        numerador = produto_escalar(cruz, d3.componentes)

        # Denominador: |alpha' x alpha''|^2
        denominador = norma_quadrada(cruz)

        resultado = simplificar_no(op('/', numerador, denominador))

        historico.adicionar(Passo(
            nivel=1,
            descricao='Torcao calculada',
            latex_depois=resultado.representacao_latex(),
            regra='Torcao',
        ))

        return resultado, historico

    # ------------------------------------------------------------------
    # Vetores de Frenet
    # ------------------------------------------------------------------

    def vetor_tangente(self) -> list[NoExpressao]:
        """T = alpha' / |alpha'|."""
        d = self.derivada()
        n = norma(d.componentes)
        return [simplificar_no(op('/', c, n)) for c in d.componentes]

    def vetor_normal(self) -> list[NoExpressao]:
        """N = T' / |T'|."""
        T_comps = self.vetor_tangente()
        curva_T = CurvaParametrica(T_comps, self.parametro)
        dT = curva_T.derivada()
        n = norma(dT.componentes)
        return [simplificar_no(op('/', c, n)) for c in dT.componentes]

    def vetor_binormal(self) -> list[NoExpressao]:
        """B = T x N (3D apenas)."""
        if self.dimensao != 3:
            raise ValueError('Vetor binormal definido apenas para curvas 3D')
        T = self.vetor_tangente()
        N = self.vetor_normal()
        return produto_vetorial(T, N)

    # ------------------------------------------------------------------
    # Frenet-Serret completo
    # ------------------------------------------------------------------

    def frenet_serret(self) -> tuple:
        """Retorna (T, N, B, kappa, tau, Historico)."""
        historico = Historico()
        historico.adicionar(Passo(
            nivel=1,
            descricao='Calculando referencial de Frenet-Serret',
            regra='Frenet-Serret',
        ))

        T = self.vetor_tangente()
        N = self.vetor_normal()

        kappa, hist_k = self.curvatura()
        for p in hist_k.todos():
            historico.adicionar(p)

        if self.dimensao == 3:
            B = self.vetor_binormal()
            tau, hist_t = self.torcao()
            for p in hist_t.todos():
                historico.adicionar(p)
        else:
            B = None
            tau = None

        historico.adicionar(Passo(
            nivel=1,
            descricao='Referencial de Frenet-Serret calculado',
            regra='Frenet-Serret',
        ))

        return T, N, B, kappa, tau, historico

    # ------------------------------------------------------------------
    # LaTeX
    # ------------------------------------------------------------------

    def representacao_latex(self) -> str:
        """alpha(t) = (x(t), y(t), z(t))."""
        comps = ', '.join(c.representacao_latex() for c in self.componentes)
        return f'\\alpha({self.parametro}) = ({comps})'
