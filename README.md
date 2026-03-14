<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/react-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/fastapi-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/zero_deps-engine-ff6b6b?style=for-the-badge" />
  <img src="https://img.shields.io/badge/testes-137_passando-brightgreen?style=for-the-badge" />
</p>

# Algebrow

> **Motor algébrico simbólico + plataforma educacional de matemática**
>
> Resolução passo-a-passo de expressões matemáticas — do básico ao cálculo avançado.
> Cada passo explica **o quê** foi feito, **por quê** foi necessário e **como** foi realizado.

---

## O que é

Algebrow é um **CAS** (Computer Algebra System) construído do zero em Python — sem NumPy, sem SymPy, sem dependências externas no motor matemático. Toda a aritmética é feita com strings para preservar precisão arbitrária.

A plataforma web (FastAPI + React + KaTeX) permite digitar uma expressão como `sqrt(216)` e ver instantaneamente:

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

## Expressões suportadas

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
│   └── solver.py                  # Solver com passo-a-passo
│
├── api/                       # FastAPI (única camada com dependências externas)
│   ├── main.py                # App + CORS
│   ├── schemas.py             # Pydantic models
│   └── routers/calcular.py    # POST /api/calcular
│
├── frontend/                  # React + Vite + TypeScript + KaTeX
│   └── src/
│       ├── components/        # EntradaExpressao, ResultadoPrincipal, PassoAPasso, Historico
│       ├── hooks/             # useCalcular (abort+timeout), useKatex, useHistorico
│       └── services/api.ts    # Cliente HTTP com timeout e cancelamento
│
├── tests/                     # 137 testes
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

**Ambição futura (Fase 2+):**
- Polinômios, equações de 1º/2º grau, sistemas lineares
- Funções e gráficos 2D (SVG puro)
- Cálculo: derivadas, integrais, limites
- Álgebra linear: matrizes, determinantes, autovalores

---

## Roadmap

| Fase | Status | Descrição |
|------|--------|-----------|
| 0 | ✅ Concluída | Correção de bugs, refatoração, infraestrutura |
| 1 | ✅ Concluída | Web app mínimo: parser + solver + API + frontend |
| 2 | 🔲 Planejada | Álgebra: polinômios, equações, sistemas |
| 3 | 🔲 Planejada | Funções e gráficos 2D |
| 4 | 🔲 Planejada | Cálculo: derivadas, integrais, limites |
| 5 | 🔲 Planejada | Álgebra linear: matrizes, determinantes |

---

## Licença

MIT — Arthur de Souza Molina, 2025
