<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/react-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/fastapi-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/zero_deps-engine-ff6b6b?style=for-the-badge" />
  <img src="https://img.shields.io/badge/testes-585_passando-brightgreen?style=for-the-badge" />
</p>

# Algebrow

> **Motor algébrico simbólico + plataforma educacional de matemática**
>
> Resolução passo-a-passo de expressões matemáticas — do básico ao cálculo avançado.
> Cada passo explica **o quê** foi feito, **por quê** foi necessário e **como** foi realizado.

---

## O que é

Algebrow é um **CAS** (Computer Algebra System) construído do zero em Python — sem NumPy, sem SymPy, sem dependências externas no motor matemático. Toda a aritmética é feita com strings para preservar precisão arbitrária.

A plataforma web (FastAPI + React + KaTeX) permite digitar uma expressão em **LaTeX puro** como `\sqrt{216}` (ou sintaxe simplificada `sqrt(216)`) e ver instantaneamente:

```
√216  →  6√6  ≈ 14.6969...
```

Com cada passo detalhado:

| # | Passo | Transformação |
|---|-------|---------------|
| 1 | Fatorar o radicando 216 | `√216 → √(2³·3³)` |
| 2 | Extrair 2 da raiz | `2³ ÷ índice 2 = 1 inteiro, resta 1` |
| 3 | Extrair 3 da raiz | `3³ ÷ índice 2 = 1 inteiro, resta 1` |
| 4 | Resultado | `6√6` |

---

## Quickstart

### Backend

```bash
# Clonar e configurar
git clone https://github.com/asm444/Algebrow.git
cd Algebrow

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Instalar dependências
pip install -r requirements.txt

# Rodar API
uvicorn api.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Acesse http://localhost:5173
```

### Usar direto no Python

```python
from engine.solver import Solver

s = Solver(verbosidade=3)

# Aceita LaTeX puro:
r = s.resolver(r'\frac{3}{4} + \frac{1}{6}')
print(r.latex_resultado)     # \frac{11}{12}

# Ou sintaxe simplificada:
r = s.resolver('sqrt(216)')
print(r.latex_resultado)     # 6\sqrt{2}{6}
print(r.valor_numerico)      # 14.69693846
for p in r.historico.filtrar():
    print(f"  [{p.nivel}] {p.descricao}")
```

### Rodar testes

```bash
python -m pytest tests/TEST_numbers.py tests/TEST_basic.py tests/TEST_expression.py tests/TEST_parser.py -v
```

---

## Entrada LaTeX

O Algebrow aceita **LaTeX puro** como entrada. O sistema detecta e converte automaticamente:

| Operação | LaTeX | Sintaxe Simples | Exemplo |
|----------|-------|-----------------|---------|
| Fração | `\frac{3}{4}` | `3/4` | ¾ |
| Raiz quadrada | `\sqrt{216}` | `sqrt(216)` | 6√6 |
| Raiz n-ésima | `\sqrt[3]{8}` | `sqrt_3(8)` | 2 |
| Potência | `2^{10}` | `2^10` | 1024 |
| Logaritmo | `\log_{2}{8}` | `log_2(8)` | 3 |
| Multiplicação | `\cdot` ou `\times` | `*` | — |
| Maior/igual | `\geq` | `>=` | — |
| Menor/igual | `\leq` | `<=` | — |

**Ambas as sintaxes são aceitas.** Cole expressões direto do Overleaf, copie de PDFs, ou use a sintaxe simplificada.

> Manual completo com todos os exemplos: [`docs/MANUAL_LATEX.md`](docs/MANUAL_LATEX.md)

### Exemplos de uso com LaTeX

```latex
\frac{3}{4} + \frac{1}{6}          % → 11/12
\sqrt{216}                          % → 6√6
\sqrt[3]{27}                        % → 3
\log_{2}{8}                         % → 3
2^{10}                              % → 1024
\frac{2}{3} \cdot \frac{5}{7}      % → 10/21
x^{2} - 5x + 6 = 0                 % → x₁=2, x₂=3
2x + 1 \geq 5                      % → x ≥ 2
```

### Expressões suportadas (sintaxe simplificada)

| Tipo | Sintaxe | Exemplo |
|------|---------|---------|
| Inteiro | `42` | `42` |
| Fração | `3/4` | `¾` |
| Raiz quadrada | `sqrt(n)` | `√216 → 6√6` |
| Raiz n-ésima | `sqrt_n(x)` | `∛8 → 2` |
| Exponencial | `a^b` | `2^3` |
| Logaritmo | `log_b(x)` | `log₃(9) → 2` |
| Log base 10 | `log(x)` | `log(100)` |
| Expressões | `a + b * c` | `3/4 + sqrt(2)` |
| Parênteses | `(a + b) * c` | `(2 + 3) * 4 → 20` |
| Negativos | `-a` | `-5 + 3 → -2` |

---

## Verbosidade (0–4)

O sistema de passos tem 5 níveis de detalhe:

| Nível | Nome | O que mostra |
|-------|------|-------------|
| **0** | Resultado | Apenas o resultado final |
| **1** | Principal | Passos principais (interpretar, simplificar) |
| **2** | Intermediário | Fatorações, extrações, propriedades |
| **3** | Detalhado | Aritmética de cada fator, divisões |
| **4** | Tudo | Micro-operações (cada ÷, cada ×) |

Cada passo inclui:
- **Descrição**: o que foi feito
- **Justificativa**: por quê foi necessário
- **Método**: como a operação foi realizada
- **LaTeX antes/depois**: transformação visual

---

## API

### `POST /api/calcular`

```json
// Request
{
  "expressao": "sqrt(216)",
  "modo": "simplificar",
  "verbosidade": 3
}

// Response
{
  "entrada": "sqrt(216)",
  "latex_entrada": "\\sqrt{2}{216}",
  "latex_resultado": "6\\sqrt{2}{6}",
  "valor_numerico": "14.69693846",
  "passos": [
    {
      "nivel": 1,
      "descricao": "Interpretar expressão",
      "regra": "parse",
      "justificativa": "Converter a entrada de texto para representação matemática",
      "metodo": "Parser descendente recursivo analisa a expressão"
    }
  ]
}
```

Documentação interativa: `http://localhost:8000/docs`

---

## Arquitetura

```
Algebrow/
├── engine/                    # Motor matemático (ZERO dependências externas)
│   ├── basic/
│   │   ├── operacoes_basicas.py   # Aritmética com strings (soma, diff, multi, div)
│   │   ├── numeros.py             # Racional, Exponencial, Raiz, Logaritmo
│   │   ├── expressao.py           # Expressão + tabela 4×4 de operações
│   │   └── passo.py               # Passo + Historico com verbosidade 0-4
│   ├── parser.py                  # Parser descendente recursivo
│   ├── latex_converter.py         # Conversor LaTeX puro → sintaxe interna
│   └── solver.py                  # Solver com passo-a-passo (aceita LaTeX)
│
├── api/                       # FastAPI (única camada com dependências externas)
│   ├── main.py                # App + CORS
│   ├── schemas.py             # Pydantic models
│   └── routers/calcular.py    # POST /api/calcular
│
├── frontend/                  # React + Vite + TypeScript + KaTeX
│   └── src/
│       ├── components/        # EntradaExpressao, ResultadoPrincipal, PassoAPasso, Historico, Manual
│       ├── hooks/             # useCalcular (abort+timeout), useKatex, useHistorico
│       └── services/api.ts    # Cliente HTTP com timeout e cancelamento
│
├── docs/
│   └── MANUAL_LATEX.md        # Manual completo de entrada LaTeX
│
├── tests/                     # 585 testes
│   ├── TEST_basic.py          # 52 testes — aritmética com strings
│   ├── TEST_numbers.py        # 20 testes — tipos numéricos e simplificação
│   ├── TEST_expression.py     # 31 testes — operações entre tipos
│   └── TEST_parser.py         # 34 testes — parser, solver, verbosidade
│
└── data/primos.txt            # Lista de primos para fatoração
```

### Princípios de design

- **Zero dependências no engine** — toda aritmética é manual com strings
- **Imutabilidade** — operações criam novos objetos, nunca mutam o original
- **Passo-a-passo como cidadão de primeira classe** — toda operação gera histórico
- **Nomes em português** — classes e funções do engine em PT-BR
- **Separação clara** — engine (puro Python) / API (FastAPI) / frontend (React)

---

## Changelog por Fase

### Fase 0 — Correção de Bugs e Refatoração

**O que foi implementado:**
- Corrigido `Logaritmo.numero_real()` com argumentos invertidos
- Corrigido `Exponencial.numero_real()` que referenciava classe inexistente
- Corrigido `Racional.__init__` para aceitar `str`, `int` e `float`
- Eliminada mutação in-place no `simplificar()` — agora cria novos objetos
- Corrigidas escape sequences em strings LaTeX
- Adicionado `__eq__` e `__hash__` nas 4 classes numéricas
- Criada infraestrutura de passo-a-passo (`Passo` + `Historico`)
- Completada classe `Expressao` com tabela 4×4 de operações (soma + multiplicação)
- Reorganizada estrutura: `basic/` → `engine/basic/` com nomes em português

**O que deu certo:**
- 72 testes originais continuaram passando após refatoração
- 31 novos testes para `Expressao` passando
- Imutabilidade eliminou bugs de efeito colateral

**Ambição futura:**
- Suporte a números imaginários (i = √(-1))
- Divisão entre tipos irracionais (racionalização)

---

### Fase 1 — Web App Mínimo (Calculadora Simbólica)

**O que foi implementado:**
- Parser descendente recursivo manual (zero dependências)
  - Suporta: inteiros, frações, raízes, exponenciais, logaritmos, parênteses, negativos
  - Precedência correta: `2 + 3 * 4 = 14`
- Solver com resolução passo-a-passo pedagógico
  - Cada passo com justificativa (porquê) e método (como)
  - Verbosidade configurável 0-4
- API FastAPI com POST `/api/calcular`
  - Schemas Pydantic, CORS, documentação automática
- Frontend React + Vite + KaTeX
  - Preview LaTeX em tempo real enquanto digita
  - Passos expansíveis com detalhes
  - Histórico persistente via localStorage
  - Slider de verbosidade

**O que deu certo:**
- API retorna JSON completo com `sqrt(216)` em <50ms
- Frontend compila sem erros TypeScript
- Segurança: timeout 10s, cancelamento de requests, sem innerHTML
- 137 testes passando

**Ambição futura:**
- Suporte a números imaginários
- Integrar equações no solver/API

---

### Fase 2 — Álgebra

**O que foi implementado:**
- Classe `Polinomio` com aritmética exata (soma, sub, multi, divisão longa)
  - Fatoração por raízes racionais (teorema ±p/q)
  - Bhaskara para grau 2, divisão sintética para grau 3+
- `Equacao1Grau`: resolve `ax + b = 0` com passo-a-passo
- `Equacao2Grau`: Bhaskara completo (discriminante, raiz dupla, raízes com √)
- `SistemaLinear`: eliminação de Gauss para 2×2 e 3×3
  - Classificação: determinado / indeterminado / impossível
- `Inequacao1Grau`: resolve com inversão de sinal automática
- Parser expandido: variáveis (x, y), equações (=), inequações (>, <)
  - Multiplicação implícita: `2x` → `2*x`

**O que deu certo:**
- `x²-5x+6=0` → `x₁=2, x₂=3` com passos detalhados
- `x³-6x²+11x-6` fatorado em `(x-1)(x-2)(x-3)`
- Sistema `x+y=5, x-y=1` → `x=3, y=2` com Gauss
- 50 testes de álgebra passando

**Ambição futura:**
- Integrar polinômios e equações no solver/API
- Equações de grau 3+ (Cardano)
- Sistemas não-lineares

---

### Fase 3 — Funções e Gráficos

**O que foi implementado:**
- 4 classes de funções elementares com interface comum:
  - `FuncaoLinear(a, b)`: zeros, inversa, avaliação
  - `FuncaoQuadratica(a, b, c)`: vértice, zeros (via Bhaskara), concavidade
  - `FuncaoExponencial(a, b)`: domínio, imagem, assíntotas
  - `FuncaoLogaritmica(a, b)`: domínio, zeros
- Gerador de pontos para gráficos 2D (`gerar_pontos`)
  - Aceita expressões como `"x^2 - 4"` ou callables
  - Detecção de descontinuidades e assíntotas
  - Multiplicação implícita (`2x`, `3x^2`)
- API `POST /api/grafico` com schemas Pydantic
- `detectar_assintotas_verticais` com busca binária

**O que deu certo:**
- `1/x` detecta descontinuidade em x=0
- `x²` gera parábola com todos os pontos positivos
- 57 testes de funções e gráficos passando
- 253 testes total

**Ambição futura:**
- Trigonometria: sen, cos, tan com propriedades
- Componente SVG no frontend para plotar gráficos
- Composição de funções (f∘g)

---

### Auditoria de Qualidade

**Segurança:**
- Parser com limite de profundidade (50 níveis)
- Input limitado a 500 caracteres
- Catch genérico na API sem exposição de detalhes
- CORS restrito, sem innerHTML no frontend
- Timeout 10s e cancelamento de requests

**Desempenho:**
- Cache de primos.txt no module-level (1 leitura)
- `math.gcd` substitui recursão em `reduz_fracao`
- Trial division O(√n) em `number_to_potencia`
- Testes 5x mais rápidos (0.34s → 0.07s)

**Inteligência:**
- `0^0` → indefinido, `√(-n)` → erro, `(-n)^m` → erro
- Expoente 1 simplifica, coeficiente -1 renderiza como "-"
- Passos nível 4 implementados (divisão euclidiana)
- MDC explícito na simplificação de frações

---

### Fase 4 — Cálculo

**O que foi implementado:**
- AST simbólica (`NoExpressao`) para representar `sen(x²)`, `e^(2x+1)`, etc.
  - Tipos: numero, variavel, operacao, funcao
  - Helpers fluentes: `num()`, `var()`, `op()`, `func()`
- Derivação simbólica via regras recursivas na AST:
  - Constante, variável, soma, produto, quociente, potência
  - Regra da cadeia para funções compostas
  - sin→cos, cos→-sin, exp→exp, ln→1/x, tan→sec²
  - Cada regra gera Passo explicativo com justificativa
- Integração simbólica:
  - Tabela direta: x^n, 1/x, sin, cos, exp
  - Constante × função, soma/diferença
  - Adiciona + C automaticamente
- Limites:
  - Substituição direta
  - L'Hôpital para formas indeterminadas 0/0 e ∞/∞
  - Fallback para aproximação numérica
- Simplificação algébrica: 0+x→x, 1*x→x, 0*x→0, x^0→1, x^1→x

**O que deu certo:**
- `d/dx(x³ + 2x)` → `3x² + 2` com passos de cada regra
- `∫(2x + 1)dx` → `x² + x + C`
- `lim(x→0) sen(x)/x` → `1` via L'Hôpital
- 45 testes de cálculo passando

**Ambição futura:**
- Séries de Taylor/Maclaurin
- Integração por substituição e por partes
- Frações parciais
- Derivadas parciais

---

### Fase 5 — Álgebra Linear

**O que foi implementado:**
- Classe `Matriz` com aritmética exata (strings):
  - Soma, subtração, multiplicação escalar e matricial
  - Transposta, igualdade
  - LaTeX com `\begin{pmatrix}...\end{pmatrix}`
- Determinante: 2×2 (ad-bc), 3×3 (Sarrus), n×n (Laplace)
  - Passo-a-passo mostrando cada menor e cofator
- Eliminação de Gauss com passo-a-passo pedagógico:
  - Cada operação elementar como Passo (L₂ ← L₂ - kL₁)
  - Classificação: determinado / indeterminado / impossível
  - Substituição regressiva
- Autovalores 2×2 via polinômio característico (`det(A - λI) = 0`)
- Autovetores 2×2

**O que deu certo:**
- Determinante 3×3 com Sarrus e passos detalhados
- Sistema 3×3 via Gauss com cada operação elementar
- Autovalores de `[[4,1],[2,3]]` → `λ₁=5, λ₂=2`
- 33 testes de álgebra linear passando

**Ambição futura:**
- Autovalores/autovetores n×n
- Decomposição LU
- Espaços vetoriais e bases
- Diagonalização

---

### Fase 6 — Números Complexos e Análise Complexa

**Que contas resolve:**
- Aritmética complexa: `(3+2i) × (1-i)`, `(4+2i) ÷ (1+i) = 3-i`
- Forma polar: `z = r·e^(iθ)`, conversão retangular ↔ polar
- Raízes n-ésimas: raízes cúbicas de 1, raízes quadradas de i
- Fórmula de Euler: `e^(iπ) = -1`
- Verificação de Cauchy-Riemann (funções holomorfas)
- Resíduo em polo simples
- Transformada de Laplace: `L{sin(ωt)} = ω/(s²+ω²)`
- Transformada inversa e resolução de EDOs via Laplace

---

### Fase 7 — Cálculo Completo (Guidorizzi Vol 1-4)

**Que contas resolve:**
- **Derivadas avançadas:** arcsin, arccos, arctan, regra da cadeia compostas, derivada implícita, ordem N
- **Integrais:** substituição (∫2x·cos(x²)dx), por partes (LIATE), frações parciais, trigonométrica
- **Limites:** laterais, no infinito, formas indeterminadas (0·∞, 0^0, 1^∞)
- **Aplicações:** máx/mín (teste 2ª derivada), inflexão, TVM, esboço de curvas, sólidos de revolução, comprimento de arco
- **Séries:** Taylor/Maclaurin, geométrica, série p, testes de convergência (razão, raiz, comparação)
- **Sequências:** limite, raio de convergência
- **EDOs:** separável, linear 1ª ordem (fator integrante), 2ª ordem coef constante (Bhaskara), Bernoulli, exata, Euler numérico
- **Multivariável:** gradiente, divergente, rotacional, laplaciano, jacobiana, hessiana, Lagrange

---

### Fase 9 — Geometria Diferencial

**Que contas resolve:**
- **Curvas:** curvatura κ, torção τ, triedro de Frenet-Serret (T, N, B)
- **Superfícies:** primeira e segunda forma fundamental, curvatura gaussiana K, curvatura média H
- **Exemplos:** κ do círculo = 1, κ e τ da hélice, K da esfera = 1
- **Álgebra vetorial simbólica:** produto escalar, vetorial, norma

---

## Roadmap

### Plataforma Base (Concluída)
| Fase | Status | Descrição |
|------|--------|-----------|
| 0 | ✅ | Correção de bugs, refatoração, infraestrutura |
| 1 | ✅ | Web app: parser + solver + API + frontend React/KaTeX |
| 2 | ✅ | Álgebra: polinômios, equações, sistemas, inequações |
| 3 | ✅ | Funções elementares e gráficos 2D |
| 4-7 | ✅ | Cálculo completo (Guidorizzi Vol 1-4) |
| 5 | ✅ | Álgebra linear: matrizes, determinantes, autovalores |

### Física-Matemática (Arfken + Butkov + Wald)
| Fase | Status | Descrição |
|------|--------|-----------|
| 6 | ✅ | Complexos: aritmética, polar, Euler, Laplace |
| 8 | ✅ | Funções especiais: Gamma, Bessel, Legendre, Hermite, Laguerre |
| 9 | ✅ | Geometria diferencial: curvas, superfícies, Frenet |
| 10 | ✅ | Sturm-Liouville, funções de Green |
| 11 | ✅ | PDEs: calor, onda, Laplace, separação de variáveis |
| 12 | ✅ | Fourier: séries completas, transformada contínua |
| 13 | ✅ | Cálculo variacional: Euler-Lagrange, braquistócrona |
| 14 | ✅ | Equações integrais: Fredholm, Volterra, Neumann |
| 15 | ✅ | Tensores: métrico, Christoffel, Riemann, Schwarzschild (Wald) |
| 16 | ✅ | Teoria de grupos: Z_n, S_n, D_n, Lie, SO(3), SU(2) |

---

## Estatísticas

| Métrica | Valor |
|---------|-------|
| Testes | 585 passando |
| Tempo de testes | ~11s |
| Commits | 40+ |
| Módulos do engine | 50+ arquivos Python |
| Dependências do engine | 0 (zero!) |
| Linhas de código (engine) | ~16000 |

---

## Licença

MIT — Arthur de Souza Molina, 2025
