# Manual de Entrada LaTeX — Algebrow

O Algebrow aceita **LaTeX puro** como entrada. Basta digitar a expressão usando os comandos LaTeX padrão, e o sistema interpreta, calcula e mostra o resultado passo a passo.

> **Nota:** A sintaxe simplificada (`sqrt(216)`, `2^3`, `log_2(8)`) também continua sendo aceita.

---

## Referência Rápida

| Operação          | LaTeX                       | Exemplo                              | Resultado         |
|-------------------|-----------------------------|--------------------------------------|--------------------|
| Fração            | `\frac{a}{b}`               | `\frac{3}{4}`                        | 3/4                |
| Raiz quadrada     | `\sqrt{x}`                  | `\sqrt{216}`                         | 6√6                |
| Raiz n-ésima      | `\sqrt[n]{x}`               | `\sqrt[3]{8}`                        | 2                  |
| Potência          | `a^{b}`                     | `2^{10}`                             | 1024               |
| Logaritmo         | `\log_{b}{x}`               | `\log_{2}{8}`                        | 3                  |
| Multiplicação     | `\cdot` ou `\times`         | `3 \cdot 4`                          | 12                 |
| Divisão           | `\div`                      | `12 \div 3`                          | 4                  |
| Maior ou igual    | `\geq`                      | `x \geq 5`                           | —                  |
| Menor ou igual    | `\leq`                      | `x \leq 10`                          | —                  |

---

## 1. Frações

### Sintaxe
```latex
\frac{numerador}{denominador}
```

### Variantes aceitas
- `\frac{a}{b}` — fração padrão
- `\dfrac{a}{b}` — fração display (mesmo efeito)
- `\tfrac{a}{b}` — fração inline (mesmo efeito)

### Exemplos
| Entrada LaTeX                            | O que calcula                     |
|------------------------------------------|-----------------------------------|
| `\frac{3}{4}`                            | Fração 3/4                       |
| `\frac{3}{4} + \frac{1}{6}`             | Soma de frações: 3/4 + 1/6       |
| `\frac{2}{3} \cdot \frac{5}{7}`         | Multiplicação: (2/3) × (5/7)     |
| `\frac{1}{2} + \frac{1}{3} + \frac{1}{6}` | Soma de 3 frações              |

---

## 2. Raízes

### Sintaxe
```latex
\sqrt{radicando}         % raiz quadrada
\sqrt[n]{radicando}      % raiz n-ésima
```

### Exemplos
| Entrada LaTeX        | O que calcula                        | Resultado |
|----------------------|--------------------------------------|-----------|
| `\sqrt{216}`         | Raiz quadrada de 216                 | 6√6       |
| `\sqrt{50}`          | Raiz quadrada de 50                  | 5√2       |
| `\sqrt{144}`         | Raiz quadrada de 144                 | 12        |
| `\sqrt[3]{8}`        | Raiz cúbica de 8                     | 2         |
| `\sqrt[3]{27}`       | Raiz cúbica de 27                    | 3         |
| `\sqrt[4]{81}`       | Raiz quarta de 81                    | 3         |
| `\sqrt[5]{32}`       | Raiz quinta de 32                    | 2         |

### Como funciona a simplificação
O Algebrow fatoriza o radicando em fatores primos e extrai os que "saem" da raiz:

```
√216 = √(2³ × 3³)
     = √(2² × 2 × 3² × 3)
     = 2 × 3 × √(2 × 3)
     = 6√6
```

---

## 3. Potências

### Sintaxe
```latex
base^{expoente}
```

### Exemplos
| Entrada LaTeX        | O que calcula        | Resultado |
|----------------------|----------------------|-----------|
| `2^{10}`             | 2 elevado a 10       | 1024      |
| `3^{4}`              | 3 elevado a 4        | 81        |
| `5^{3}`              | 5 elevado a 3        | 125       |
| `2^{3} + 3^{2}`     | Soma de potências    | 8 + 9     |

---

## 4. Logaritmos

### Sintaxe
```latex
\log_{base}{argumento}    % logaritmo com base
\log{argumento}           % logaritmo base 10
```

### Exemplos
| Entrada LaTeX           | O que calcula              | Resultado |
|-------------------------|----------------------------|-----------|
| `\log_{2}{8}`           | log base 2 de 8            | 3         |
| `\log_{3}{9}`           | log base 3 de 9            | 2         |
| `\log_{10}{1000}`       | log base 10 de 1000        | 3         |
| `\log_{5}{125}`         | log base 5 de 125          | 3         |
| `\log{100}`             | log base 10 de 100         | 2         |

### Como funciona
O motor fatoriza o argumento e verifica se é uma potência da base:

```
log₂(8) → 8 = 2³ → log₂(2³) = 3
```

---

## 5. Operadores

### Multiplicação
```latex
3 \cdot 4       % ponto central
6 \times 7      % sinal de vezes
2x              % multiplicação implícita (sem operador)
```

### Divisão
```latex
\frac{a}{b}     % como fração (preferido)
a \div b        % sinal de divisão
```

### Comparação (Equações e Inequações)
```latex
2x + 3 = 7       % equação
x^{2} - 4 = 0    % equação de 2o grau
2x + 1 > 5       % maior que
3x - 2 < 10      % menor que
x \geq 7         % maior ou igual
5x \leq 20       % menor ou igual
```

---

## 6. Expressões Mistas

Combine livremente frações, raízes, potências e logaritmos:

| Entrada LaTeX                                   | Descrição                    |
|-------------------------------------------------|------------------------------|
| `\frac{3}{4} + \sqrt{2}`                        | Fração + raiz               |
| `2^{3} + \log_{2}{16}`                          | Potência + logaritmo        |
| `\sqrt{3} \cdot \sqrt{12}`                      | Produto de raízes           |
| `\frac{1}{2} + \frac{1}{3} + \frac{1}{6}`      | Soma de várias frações      |

---

## 7. Equações e Inequações

### Equação de 1o grau
```latex
2x + 3 = 7
```
Resolução: isolamento da variável com passo a passo.

### Equação de 2o grau
```latex
x^{2} - 5x + 6 = 0
```
Resolução via **fórmula de Bhaskara**, mostrando discriminante, raízes e classificação.

### Inequação
```latex
2x + 1 \geq 5
```
Resolução com inversão automática do sinal quando necessário.

---

## 8. Variáveis Aceitas

O parser reconhece as seguintes variáveis: **x, y, z, a, b, c, n, t**.

A multiplicação implícita é suportada:
- `2x` = 2 × x
- `3x^{2}` = 3 × x²
- `xy` não suportado (use `x \cdot y`)

---

## 9. Delimitadores LaTeX (ignorados automaticamente)

Os seguintes comandos de formatação são aceitos mas ignorados (não afetam o cálculo):

| Comando                      | Comportamento            |
|------------------------------|--------------------------|
| `\left( ... \right)`         | Tratado como parênteses  |
| `\displaystyle`              | Ignorado                 |
| `\mathrm{...}`               | Conteúdo preservado      |
| `\text{...}`                 | Conteúdo preservado      |
| `\operatorname{...}`         | Conteúdo preservado      |

---

## 10. Nível de Detalhamento (Verbosidade)

O slider de detalhamento controla a quantidade de passos mostrados:

| Nível | Nome               | O que mostra                                       |
|-------|--------------------|-----------------------------------------------------|
| 0     | Só resultado       | Apenas a resposta final                             |
| 1     | Passos principais  | Etapas-chave da resolução                           |
| 2     | Intermediário      | Fatorações, extrações, simplificações               |
| 3     | Detalhado          | Aritmética de cada fator, justificativas            |
| 4     | Tudo               | Micro-operações (divisão euclidiana, etc.)           |

---

## 11. Dicas de Uso

1. **Use o preview**: Ao digitar, a expressão LaTeX é renderizada em tempo real acima do campo de entrada
2. **Clique nos exemplos**: O Manual tem exemplos clicáveis que preenchem o campo automaticamente
3. **Histórico**: Cálculos anteriores ficam salvos no painel lateral — clique para recalcular
4. **Ambas as sintaxes**: Pode misturar LaTeX (`\frac{3}{4}`) com sintaxe simples (`sqrt(2)`) sem problemas
5. **Copie do Overleaf**: Expressões copiadas de editores LaTeX funcionam diretamente

---

## 12. Limitações

- Máximo de 500 caracteres por expressão
- Profundidade máxima de aninhamento: 50 níveis
- Timeout: 10 segundos por cálculo
- Não suporta matrizes LaTeX (`\begin{pmatrix}...`) na entrada (use a API direta)
- Não suporta integrais/derivadas na entrada LaTeX (em desenvolvimento)
