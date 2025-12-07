# Definição do Objeto `Número`

Este arquivo tem como objetivo definir o objeto **`Número`**, que servirá como base para representar e operar com diferentes tipos numéricos.  
Outros objetos relacionados serão definidos em arquivos separados devido à sua complexidade e extensão.

---

## Propósito

A criação do objeto `Número` representa um marco no desenvolvimento do sistema, permitindo o aumento da complexidade das operações sem comprometer a estrutura ou clareza do código.

---

## Tipos de Números

O sistema deve ser capaz de lidar com diversos tipos de números, incluindo:

- **Irracionais**, representados por:
  - Exponenciais  
  - Logaritmos  
  - Raízes  

Esses objetos devem ser manipulados em operações básicas **sem conversão para decimais**, preservando sua forma simbólica sempre que possível.

---

## Ordem de Prioridade nas Operações

Ao realizar operações entre diferentes tipos de números, deve-se seguir a seguinte hierarquia de prioridade:

1. Número inteiro ou racional  
2. Exponencial  
3. Raiz  
4. Logaritmo  

Durante as interações:
- Simplificar ao máximo **sem perda de informação**.  
- Testar se alguma operação resulta em uma simplificação para 1 (podendo eliminar o objeto correspondente).  
- Manter a **estrutura simbólica** e o **histórico de operações**.

---

## Hierarquia de Registro dos Passos de Cálculo

Para fins de rastreamento e depuração, os passos das operações poderão ser registrados em diferentes níveis de detalhamento:

| Nível | Descrição |
|:-----:|------------|
| **0** | Todos os passos são registrados. |
| **1** | Passos simples são ignorados; principais e de simplificação são registrados. |
| **2** | Apenas simplificações relevantes e passos principais são registrados. |
| **3** | Apenas os passos principais são registrados. *(Padrão)* |
| **4** | Somente o resultado final é registrado. |

O programa faz todos os calculos e armazena a quantidadade de calculos deacordo com a verbosidade.
Dessa forma ele sabe o que será exibido na solução.
---

## Considerações Finais

O objetivo deste projeto é **fazer o computador compreender os conceitos matemáticos** de forma simbólica e estruturada.  
Nenhuma biblioteca externa será utilizada — todas as implementações serão desenvolvidas manualmente, passo a passo.
