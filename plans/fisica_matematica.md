# Plano: Física Matemática no Algebrow

## Visão Geral

Transformar o Algebrow numa plataforma que resolve problemas de física com passo-a-passo, usando o motor de cálculo simbólico como base. Cada módulo de física importa diretamente os módulos de cálculo (derivadas, integrais, EDOs, álgebra linear).

## Dependências do Engine

```
engine/calculo/     → derivadas, integrais, limites, EDOs, séries
engine/algebra/     → equações, sistemas, polinômios
engine/algebra_linear/ → matrizes, determinantes, autovalores
engine/basic/       → aritmética exata, passos
```

Toda física usa esses módulos — NÃO reimplementa cálculo.

---

## Fase 6 — Mecânica Clássica (`engine/fisica/mecanica/`)

### 6.1 Cinemática (`cinematica.py`)

**Conceitos:**
- MRU: s = s₀ + vt
- MRUV: s = s₀ + v₀t + at²/2, v = v₀ + at
- Lançamento oblíquo: decomposição em x e y
- Queda livre: caso particular do MRUV com g

**Implementação:**
```python
class MovimentoRetilineoUniforme:
    def resolver(self, conhecidos: dict) -> tuple:
        """Dado qualquer combinação de s, s0, v, t → calcula o faltante."""

class MRUV:
    def resolver(self, conhecidos: dict) -> tuple:
        """5 equações do MRUV — detecta qual usar baseado nos dados."""

class LancamentoObliquo:
    def resolver(self, v0, angulo, g='9.8') -> tuple:
        """Alcance, altura máxima, tempo de voo com passos."""
```

**Técnica de resolução:** Identificar variáveis conhecidas → selecionar equação → isolar incógnita via `Equacao1Grau`/`Equacao2Grau` → simplificar.

### 6.2 Dinâmica (`dinamica.py`)

**Conceitos:**
- 2ª Lei de Newton: F = ma (sistemas com múltiplas forças)
- Atrito: f = μN
- Plano inclinado: decomposição de forças
- Trabalho: W = ∫F·ds (usar integrar())
- Energia cinética e potencial
- Conservação de energia

**Implementação:**
```python
class SistemaForcas:
    def resolver(self, forcas: list, massa: str) -> tuple:
        """Soma vetorial de forças → aceleração."""

class PlanoInclinado:
    def resolver(self, massa, angulo, mu=None) -> tuple:
        """Decomposição de forças com/sem atrito."""

class TrabalhoEnergia:
    def trabalho(self, forca: NoExpressao, deslocamento) -> tuple:
        """W = ∫F·ds usando integrar()."""
```

### 6.3 Oscilações (`oscilacoes.py`)

**Conceitos:**
- MHS: x'' + ω²x = 0 (usar edo_linear_2ordem_coef_cte)
- Amortecido: x'' + 2γx' + ω²x = 0
- Forçado: x'' + 2γx' + ω²x = F₀cos(ωt)
- Ressonância

**Implementação:** Delega para `engine/calculo/edo.py` — cada tipo de oscilação é uma EDO de 2ª ordem com coeficientes constantes.

### 6.4 Gravitação (`gravitacao.py`)

- Lei da gravitação universal
- Órbitas circulares: igualar F_grav = F_centripeta
- Energia potencial gravitacional
- Velocidade de escape

---

## Fase 7 — Eletromagnetismo (`engine/fisica/eletromag/`)

### 7.1 Eletrostática (`eletrostatica.py`)

- Lei de Coulomb: F = kq₁q₂/r²
- Campo elétrico: E = kq/r² (ponto), E = ∫dE (distribuição)
- Potencial elétrico: V = -∫E·dl
- Lei de Gauss: ∮E·dA = Q/ε₀ (usa integral de superfície)

**Técnica:** Para distribuições contínuas, usar integrar() do engine.

### 7.2 Circuitos (`circuitos.py`)

- Lei de Ohm: V = RI
- Kirchhoff: sistema de equações lineares (usa SistemaLinear)
- RC, RL, RLC: EDOs de 1ª e 2ª ordem (usa edo.py)

### 7.3 Magnetismo (`magnetismo.py`)

- Biot-Savart: dB = μ₀I(dl × r̂)/(4πr²)
- Lei de Ampère: ∮B·dl = μ₀I
- Força de Lorentz: F = qv × B

### 7.4 Equações de Maxwell (`maxwell.py`)

- Forma diferencial: div, rot, gradiente (usa multivariavel.py)
- Ondas EM: equação de onda (EDO 2ª ordem)

---

## Fase 8 — Termodinâmica (`engine/fisica/termodinamica/`)

### 8.1 Leis da Termodinâmica (`leis.py`)

- 1ª Lei: ΔU = Q - W
- Gás ideal: PV = nRT
- Processos: isotérmico, isobárico, isocórico, adiabático
- Trabalho: W = ∫PdV (usa integrar())

### 8.2 Ciclos (`ciclos.py`)

- Carnot: eficiência η = 1 - T_fria/T_quente
- Otto, Diesel
- Diagrama PV: usar gerar_pontos() para plotar

### 8.3 Entropia (`entropia.py`)

- ΔS = ∫dQ/T
- 2ª Lei: ΔS_universo ≥ 0

---

## Fase 9 — Mecânica Quântica Introdutória (`engine/fisica/quantica/`)

### 9.1 Equação de Schrödinger (`schrodinger.py`)

- Independente do tempo: -ℏ²/2m · ψ'' + V(x)ψ = Eψ
- É uma EDO de 2ª ordem (usa edo.py)

### 9.2 Potenciais (`potenciais.py`)

- Poço infinito: ψ_n = √(2/L)·sin(nπx/L), E_n = n²π²ℏ²/(2mL²)
- Barreira de potencial: coeficientes de transmissão/reflexão
- Oscilador harmônico: níveis E_n = (n+1/2)ℏω

### 9.3 Operadores (`operadores.py`)

- Operador posição, momento
- Comutadores: [x, p] = iℏ
- Valores esperados: ⟨x⟩ = ∫ψ*xψ dx

---

## Arquitetura Proposta

```
engine/fisica/
├── __init__.py
├── constantes.py          # c, ℏ, k_B, ε₀, μ₀, G, etc.
├── unidades.py            # Conversão de unidades SI
├── mecanica/
│   ├── cinematica.py
│   ├── dinamica.py
│   ├── oscilacoes.py
│   └── gravitacao.py
├── eletromag/
│   ├── eletrostatica.py
│   ├── circuitos.py
│   ├── magnetismo.py
│   └── maxwell.py
├── termodinamica/
│   ├── leis.py
│   ├── ciclos.py
│   └── entropia.py
└── quantica/
    ├── schrodinger.py
    ├── potenciais.py
    └── operadores.py
```

## Princípio Central

**Cada problema de física se reduz a um problema de cálculo:**
- Cinemática → derivadas e integrais
- Dinâmica → equações e sistemas
- Oscilações → EDOs de 2ª ordem
- Eletrostática → integrais
- Circuitos → sistemas lineares
- Termodinâmica → integrais
- Quântica → EDOs + autovalores

O Algebrow já tem TUDO isso implementado. A física é a camada de modelagem que traduz problemas do mundo real para objetos do engine.

## Ordem de Implementação

```
Fase 6.1 (Cinemática)     — mais simples, usa apenas equações
    ↓
Fase 6.2 (Dinâmica)       — vetores + equações
    ↓
Fase 6.3 (Oscilações)     — EDOs de 2ª ordem
    ↓
Fase 7.1 (Eletrostática)  — integrais + vetores
    ↓
Fase 7.2 (Circuitos)      — sistemas lineares + EDOs
    ↓
Fase 8 (Termodinâmica)    — integrais + equações
    ↓
Fase 9 (Quântica)         — EDOs + autovalores
```

## Parser de Física

Expandir o parser para reconhecer:
- Unidades: `m/s`, `kg`, `N`, `J`, `C`, `V`
- Constantes: `g`, `c`, `hbar`, `k`, `epsilon0`
- Notação vetorial: `vec(F)`, `|F|`
- Notação de derivada temporal: `x'(t)`, `x''(t)`

## API de Física

```
POST /api/fisica/cinematica   { tipo: "mruv", dados: {v0: "10", a: "2", t: "5"} }
POST /api/fisica/eletrostatica { tipo: "coulomb", dados: {q1: "1e-6", q2: "2e-6", r: "0.1"} }
POST /api/fisica/edo          { tipo: "oscilador", dados: {omega: "2", gamma: "0.1"} }
```

Cada resposta inclui passo-a-passo com justificativa física + justificativa matemática.
