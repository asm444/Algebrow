# Plano: Física-Matemática — Arfken + Butkov

## Referências
- **Arfken** — Mathematical Methods for Physicists, 7th ed. (23 capítulos)
- **Butkov** — Mathematical Physics (15 capítulos)

## Mapeamento: O que já existe vs. o que falta

### JÁ IMPLEMENTADO no Algebrow
| Tópico | Arfken | Módulo existente |
|--------|--------|------------------|
| Matrizes e determinantes | Cap 2 | engine/algebra_linear/ |
| Autovalores | Cap 6 | engine/algebra_linear/autovalor.py |
| EDOs | Cap 7 | engine/calculo/edo.py |
| Variável complexa (parcial) | Cap 11 | engine/complexos/ (em andamento) |
| Séries de Fourier (parcial) | Cap 19 | engine/calculo/serie.py |
| Análise vetorial (parcial) | Cap 3 | engine/calculo/multivariavel.py |
| PDEs (básico) | Cap 9 | — |
| Cálculo de variações | Cap 22 | — |

### FALTA IMPLEMENTAR

---

## Fase 6 — Números Complexos e Análise Complexa (Arfken Cap 11-12)
**Status: Em andamento (agente rodando)**

- Classe Complexo com aritmética exata
- Fórmula de Euler, De Moivre, raízes n-ésimas
- Cauchy-Riemann, séries de Laurent, resíduos
- Transformada de Laplace (tabela + resolução de EDOs)

---

## Fase 7 — Funções Especiais (Arfken Cap 13-16, 18; Butkov Cap 9-11)

### 7.1 Função Gamma (`engine/funcoes_especiais/gamma.py`)
- Γ(n) = (n-1)! para inteiros
- Integral: Γ(z) = ∫₀^∞ t^(z-1) e^(-t) dt
- Propriedades: Γ(z+1) = zΓ(z), Γ(1/2) = √π
- Função Beta: B(a,b) = Γ(a)Γ(b)/Γ(a+b)
- Fórmula de Stirling: n! ≈ √(2πn)(n/e)^n

### 7.2 Funções de Bessel (`engine/funcoes_especiais/bessel.py`)
- EDO de Bessel: x²y'' + xy' + (x² - ν²)y = 0
- Série de potências: J_ν(x) = Σ (-1)^k (x/2)^(2k+ν) / (k! Γ(k+ν+1))
- Propriedades: relações de recorrência, ortogonalidade
- Zeros de Bessel
- Funções de Neumann Y_ν, Hankel H_ν

### 7.3 Polinômios de Legendre (`engine/funcoes_especiais/legendre.py`)
- EDO de Legendre: (1-x²)y'' - 2xy' + l(l+1)y = 0
- Fórmula de Rodrigues: P_l(x) = 1/(2^l l!) d^l/dx^l (x²-1)^l
- Ortogonalidade: ∫₋₁¹ P_m(x) P_n(x) dx = 2δ_mn/(2n+1)
- Harmônicos esféricos Y_l^m(θ,φ)
- Polinômios associados de Legendre

### 7.4 Polinômios de Hermite e Laguerre (`engine/funcoes_especiais/hermite_laguerre.py`)
- Hermite: H_n(x) — oscilador harmônico quântico
- Laguerre: L_n(x) — átomo de hidrogênio
- Fórmulas de Rodrigues, ortogonalidade, funções geradoras

---

## Fase 8 — Teoria de Sturm-Liouville e Funções de Green (Arfken Cap 8, 10; Butkov Cap 7-8)

### 8.1 Sturm-Liouville (`engine/edo_avancada/sturm_liouville.py`)
- Problema de Sturm-Liouville: [p(x)y']' + [q(x) + λw(x)]y = 0
- Autovalores e autofunções
- Ortogonalidade das autofunções
- Expansão em autofunções
- Exemplos: Fourier, Bessel, Legendre como casos particulares

### 8.2 Funções de Green (`engine/edo_avancada/green.py`)
- Definição: LG(x,x') = δ(x-x')
- Construção para EDOs de 2ª ordem
- Green para equação do calor, onda, Laplace
- Propriedades de simetria

---

## Fase 9 — Tensores e Geometria Diferencial (Arfken Cap 3-4; Butkov Cap 4)
**Status: Em andamento (agente rodando)**

### 9.1 Curvas
- Curvatura, torção, triedro de Frenet-Serret

### 9.2 Superfícies
- Formas fundamentais, curvatura gaussiana e média

### 9.3 Tensores (`engine/geometria_diferencial/tensores.py`)
- Tensor métrico g_ij
- Transformações de coordenadas
- Símbolos de Christoffel: Γ^k_ij = ½g^kl(∂g_il/∂x^j + ∂g_jl/∂x^i - ∂g_ij/∂x^l)
- Derivada covariante
- Tensor de Riemann R^i_jkl (simplificado 2D)
- Tensor de Ricci, escalar de curvatura

### 9.4 Formas diferenciais (`engine/geometria_diferencial/formas.py`)
- 0-formas (funções), 1-formas, 2-formas
- Derivada exterior d
- Produto wedge ∧
- Teorema de Stokes generalizado

---

## Fase 10 — PDEs e Separação de Variáveis (Arfken Cap 9; Butkov Cap 7)

### 10.1 PDEs clássicas (`engine/edp/`)
- Equação do calor: ∂u/∂t = k∇²u
- Equação da onda: ∂²u/∂t² = c²∇²u
- Equação de Laplace: ∇²u = 0
- Equação de Poisson: ∇²u = f

### 10.2 Separação de variáveis
- Coordenadas cartesianas
- Coordenadas cilíndricas (→ Bessel)
- Coordenadas esféricas (→ Legendre/harmônicos esféricos)

### 10.3 Condições de contorno
- Dirichlet, Neumann, mistas
- Problemas de valor de contorno

---

## Fase 11 — Transformadas Integrais (Arfken Cap 20; Butkov Cap 6)

### 11.1 Transformada de Fourier (`engine/fourier/`)
- Definição, propriedades, convolução, Parseval
- DFT discreta (para cálculo numérico)
- Aplicações a PDEs

### 11.2 Transformada de Laplace (já em complexos/)
- Expandir: inversão por resíduos, convolução

### 11.3 Outras transformadas
- Hankel, Mellin (referência)

---

## Fase 12 — Cálculo de Variações e Equações Integrais (Arfken Cap 21-22)

### 12.1 Cálculo de variações (`engine/variacional/`)
- Funcional e extremos
- Equação de Euler-Lagrange: ∂F/∂y - d/dx(∂F/∂y') = 0
- Problemas com restrições (multiplicadores de Lagrange)
- Braquistócrona, geodésicas
- Princípio de Hamilton

### 12.2 Equações integrais (`engine/integral_eq/`)
- Fredholm de 1ª e 2ª espécie
- Volterra
- Método de séries de Neumann
- Relação com Sturm-Liouville

---

## Fase 13 — Teoria de Grupos (Arfken Cap 5, 16-17)

### 13.1 Espaços vetoriais (`engine/algebra_abstrata/`)
- Espaços com produto interno
- Operadores lineares
- Bases ortonormais, Gram-Schmidt

### 13.2 Grupos (introdutório)
- Grupos de simetria
- Representações matriciais
- Momento angular (SU(2), SO(3))

---

## Arquitetura Final

```
engine/
├── basic/                     # Aritmética exata (existente)
├── algebra/                   # Polinômios, equações (existente)
├── algebra_linear/            # Matrizes, autovalores (existente)
├── calculo/                   # Derivadas, integrais, EDOs (existente)
├── complexos/                 # Análise complexa, Laplace (Fase 6)
├── funcoes/                   # Funções elementares (existente)
├── funcoes_especiais/         # Gamma, Bessel, Legendre, Hermite (Fase 7)
├── geometria_diferencial/     # Curvas, superfícies, tensores (Fase 9)
├── edo_avancada/              # Sturm-Liouville, Green (Fase 8)
├── edp/                       # PDEs, separação de variáveis (Fase 10)
├── fourier/                   # Séries e transformada de Fourier (Fase 11)
├── variacional/               # Euler-Lagrange (Fase 12)
├── integral_eq/               # Equações integrais (Fase 12)
├── algebra_abstrata/          # Espaços vetoriais, grupos (Fase 13)
├── parser.py
└── solver.py
```

## Ordem de Implementação

```
Fase 6  (Complexos)              ← em andamento
Fase 9  (Geometria Diferencial)  ← em andamento
    ↓
Fase 7  (Funções Especiais)      ← depende de EDOs + Complexos
    ↓
Fase 8  (Sturm-Liouville/Green) ← depende de Funções Especiais
    ↓
Fase 10 (PDEs)                   ← depende de Fourier + Funções Especiais
    ↓
Fase 11 (Transformadas)          ← depende de Complexos
    ↓
Fase 12 (Variacional/Integrais)  ← independente
    ↓
Fase 13 (Grupos)                 ← independente
```
