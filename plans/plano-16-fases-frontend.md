# Plano: Todas as 16 Fases Acessíveis pelo Frontend

## Visão Geral

Conectar TODAS as 16 fases do Algebrow ao frontend via LaTeX.
O usuário digita LaTeX puro → sistema detecta qual operação → roteia para o engine correto → retorna resultado com passos.

---

## Mapeamento: Fase → Módulos → Operações via LaTeX

### Fase 0-1: Básico (JÁ FUNCIONA)
- **Módulos:** `engine/basic/`, `engine/parser.py`, `engine/solver.py`
- **LaTeX:** `\frac{3}{4}`, `\sqrt{216}`, `2^{10}`, `\log_{2}{8}`
- **Status:** ✅ Completo

### Fase 2: Álgebra
- **Módulos:** `engine/algebra/equacao.py`, `polinomio.py`, `sistema.py`, `inequacao.py`
- **LaTeX entrada:**
  - Equação 1o grau: `2x + 3 = 7`
  - Equação 2o grau: `x^{2} - 5x + 6 = 0`
  - Sistema: `\begin{cases} x + y = 5 \\ x - y = 1 \end{cases}`
  - Inequação: `2x + 1 \geq 5`
- **Status:** ⚠️ Parcial (equações simples detectadas pelo parser, mas resolver não roteia para Equacao2Grau)

### Fase 3: Funções & Gráficos
- **Módulos:** `engine/funcoes/elementares.py`, `grafico.py`
- **LaTeX entrada:** Gráficos já funcionam via `/api/grafico`
- **Status:** ✅ API separada funciona

### Fase 4-7: Cálculo (Derivadas, Integrais, Limites, Séries, EDOs)
- **Módulos:** `engine/calculo/` (todos os 10 arquivos)
- **LaTeX entrada:**
  - Derivada: `\frac{d}{dx} x^{3}` ou `\frac{d}{dx}\left(\sin(x)\right)`
  - Derivada ordem n: `\frac{d^{2}}{dx^{2}} x^{4}`
  - Integral indef: `\int x^{2} \, dx`
  - Integral def: `\int_{0}^{1} x^{2} \, dx`
  - Limite: `\lim_{x \to 0} \frac{\sin(x)}{x}`
  - Série Taylor: `\text{taylor}(\sin(x), x, 0, 5)`
  - EDO: `y' + 2y = 0` ou `\frac{dy}{dx} + 2y = 0`
- **Status:** ❌ Não conectado (engine funciona, sem ponte)

### Fase 5: Álgebra Linear
- **Módulos:** `engine/algebra_linear/` (matriz, determinante, gauss, autovalor)
- **LaTeX entrada:**
  - Determinante: `\det\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}`
  - Multiplicação: `\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix} \cdot \begin{pmatrix} 5 \\ 6 \end{pmatrix}`
  - Autovalores: `\text{autovalores}\begin{pmatrix} 4 & 1 \\ 2 & 3 \end{pmatrix}`
- **Status:** ❌ Não conectado

### Fase 6: Complexos
- **Módulos:** `engine/complexos/` (complexo, funcao_complexa, transformada_laplace)
- **LaTeX entrada:**
  - Aritmética: `(3+2i) \cdot (1-i)`
  - Forma polar: `\text{polar}(3+4i)`
  - Laplace: `\mathcal{L}\{\sin(\omega t)\}`
- **Status:** ❌ Não conectado

### Fase 8: Funções Especiais
- **Módulos:** `engine/funcoes_especiais/` (gamma, bessel, legendre, hermite_laguerre)
- **LaTeX entrada:**
  - Gamma: `\Gamma(5)`, `\Gamma(1/2)`
  - Bessel: `J_{0}(1)`, `J_{1}(2)`
  - Legendre: `P_{3}(x)`, `P_{5}(0.5)`
- **Status:** ❌ Não conectado

### Fase 9: Geometria Diferencial
- **Módulos:** `engine/geometria_diferencial/` (curvas, superficies, auxiliares)
- **LaTeX entrada:**
  - Curvatura: `\kappa(t^{2}, t^{3})`
  - Frenet: `\text{frenet}(\cos(t), \sin(t), t)`
- **Status:** ❌ Não conectado

### Fase 10: Sturm-Liouville & Green
- **Módulos:** `engine/edo_avancada/` (sturm_liouville, green)
- **Status:** ❌ Não conectado (interface complexa, pode ser modo especial)

### Fase 11: EDPs
- **Módulos:** `engine/edp/` (equacao_calor, equacao_onda, equacao_laplace)
- **Status:** ❌ Não conectado

### Fase 12: Fourier
- **Módulos:** `engine/fourier/` (serie_fourier, transformada_fourier)
- **LaTeX entrada:**
  - Série: `\text{fourier}(x^{2}, -\pi, \pi, 5)`
  - Transformada: `\mathcal{F}\{e^{-x^{2}}\}`
- **Status:** ❌ Não conectado

### Fase 13: Cálculo Variacional
- **Módulos:** `engine/variacional/euler_lagrange.py`
- **Status:** ❌ Não conectado

### Fase 14: Equações Integrais
- **Módulos:** `engine/integral_eq/fredholm_volterra.py`
- **Status:** ❌ Não conectado

### Fase 15: Tensores
- **Módulos:** `engine/tensores/` (tensor_metrico, christoffel, riemann)
- **Status:** ❌ Não conectado

### Fase 16: Teoria de Grupos
- **Módulos:** `engine/algebra_abstrata/` (grupo, lie, representacao)
- **Status:** ❌ Não conectado

---

## Arquitetura da Solução

### Camada 1: Conversor LaTeX Universal (`latex_converter.py`)
Estender para reconhecer TODOS os comandos LaTeX de todas as fases:
- `\int`, `\int_a^b`, `\frac{d}{dx}`, `\lim_{x \to a}`
- `\sin`, `\cos`, `\tan`, `\ln`, `\exp`, `\arcsin`, etc.
- `\begin{pmatrix}...\end{pmatrix}` (matrizes)
- `\det`, `\Gamma`, `\mathcal{L}`, `\mathcal{F}`
- `\begin{cases}...\end{cases}` (sistemas)
- Complexos: `i`, `\bar{z}`, `|z|`
- Notação de Leibniz: `\frac{dy}{dx}`, `\frac{d^2y}{dx^2}`

### Camada 2: Detector de Operação (`engine/detector.py`)
Analisar a entrada convertida e classificar:
```python
def detectar_operacao(texto: str) -> dict:
    """Retorna {'tipo': 'integral_definida', 'expressao': ..., 'variavel': ..., ...}"""
```
Tipos: basico, equacao, sistema, derivada, integral, integral_definida,
limite, serie_taylor, edo, matriz_det, matriz_mult, autovalores,
complexo, gamma, bessel, legendre, fourier, laplace, etc.

### Camada 3: Ferramentas (`engine/ferramentas/`)
Cada ferramenta com interface clara:
```
engine/ferramentas/
├── __init__.py
├── derivada.py          # calcular_derivada(expr, var)
├── integral.py          # calcular_integral(expr, var), calcular_integral_definida(...)
├── limite.py            # calcular_limite(expr, var, valor)
├── serie.py             # taylor(expr, var, ponto, ordem)
├── edo.py               # resolver_edo(expr, ...)
├── algebra_linear.py    # determinante(matriz), autovalores(matriz), gauss(sistema)
├── complexo.py          # operar_complexo(expr), polar(expr), laplace(expr)
├── funcoes_especiais.py # gamma(n), bessel(n, x), legendre(n, x)
├── fourier.py           # serie_fourier(expr, L, n), transformada(expr)
├── geometria.py         # curvatura(curva), frenet(curva)
├── tensores.py          # christoffel(metrica), riemann(metrica)
├── grupos.py            # tabela_cayley(grupo), subgrupos(grupo)
├── edp.py               # calor(expr, L), onda(expr, L, c)
├── variacional.py       # euler_lagrange(F, x, y)
├── integral_eq.py       # fredholm(f, K, lambda), volterra(f, K, lambda)
├── multivariavel.py     # gradiente(expr), jacobiana(expr), hessiana(expr)
└── aplicacoes.py        # maxmin(expr), volume_revolucao(expr), comprimento_arco(expr)
```

### Camada 4: Solver Unificado (`engine/solver.py`)
Estender para rotear QUALQUER operação:
```python
def resolver(self, entrada):
    entrada_convertida = converter_latex(entrada)
    operacao = detectar_operacao(entrada_convertida)

    if operacao['tipo'] == 'derivada':
        return self._resolver_derivada(operacao)
    elif operacao['tipo'] == 'integral':
        return self._resolver_integral(operacao)
    elif operacao['tipo'] == 'limite':
        return self._resolver_limite(operacao)
    # ... etc para cada tipo
    else:
        # Fallback: resolver como expressão básica
        return self._resolver_basico(operacao)
```

### Camada 5: Parser Simbólico (`engine/parser_simbolico.py`)
JÁ CRIADO. Converte texto em NoExpressao (AST do cálculo).

### Camada 6: Frontend
- Manual atualizado com TODAS as operações
- Exemplos clicáveis por fase

---

## Ordem de Implementação

### Bloco 1: Infraestrutura (deve vir primeiro)
1. ✅ `parser_simbolico.py` — já criado
2. `detector.py` — classificador de operações
3. Estender `latex_converter.py` com todos os comandos

### Bloco 2: Cálculo (Fases 4-7) — maior impacto
4. `ferramentas/derivada.py` — já criado
5. `ferramentas/integral.py` — já criado
6. `ferramentas/limite.py` — já criado
7. `ferramentas/serie.py`
8. `ferramentas/edo.py`
9. `ferramentas/multivariavel.py`
10. `ferramentas/aplicacoes.py`

### Bloco 3: Álgebra Linear (Fase 5)
11. `ferramentas/algebra_linear.py`
12. Parser de matrizes no `latex_converter.py`

### Bloco 4: Complexos (Fase 6)
13. `ferramentas/complexo.py`

### Bloco 5: Funções Especiais (Fase 8)
14. `ferramentas/funcoes_especiais.py`

### Bloco 6: Geometria & Tensores (Fases 9, 15)
15. `ferramentas/geometria.py`
16. `ferramentas/tensores.py`

### Bloco 7: Análise Avançada (Fases 10-14)
17. `ferramentas/fourier.py`
18. `ferramentas/variacional.py`
19. `ferramentas/integral_eq.py`
20. `ferramentas/edp.py`

### Bloco 8: Grupos (Fase 16)
21. `ferramentas/grupos.py`

### Bloco 9: Integração Final
22. Estender `solver.py` com roteamento completo
23. Atualizar API `/api/calcular`
24. Atualizar Manual do frontend
25. Testes de integração ponta-a-ponta
26. Commit + push

---

## Critério de Sucesso

Para cada fase, o teste é:
1. Digitar LaTeX no frontend
2. Ver preview renderizado
3. Clicar = e ver resultado com passos
4. Resultado correto matematicamente
