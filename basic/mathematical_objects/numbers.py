"""
A ideia principal desse arquivo é definir um objeto chamado Número. Os outros objetos serão declarados
em arquivos diferentes pois será extenso. Lidar com cada um deles. Definir essas operações é uma vira
de chave para aumentar a complexidade sem preocupações.

Será contido formas de se lidar com diversos tipos de números como
    * Irracionais representados por
        * Exponenciais
        * Logaritmos
        * Raizes
    No caso de lidar com esses objetos usando operações básicas sem decompor para decimal
        * Lidar por ordem de prioridade:
            1 -> Número inteiro ou racional
            2 -> Exponencial
            3 -> Raiz
            4 -> Logaritmo
        * Simplificar o máximo que conseguir ao interagir na interação de cada um 
        deles sem perder informações mantendo as estruturas.
        * Se alguma operação levar a uma simplificação por 1, (excluindo o objeto) ele deve testar.
"""