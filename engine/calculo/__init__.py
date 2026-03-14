from .arvore import NoExpressao
from .derivada import derivar, derivar_ordem, derivada_implicita, simplificar_no
from .integral import integrar, integral_impropria
from .limite import limite, limite_lateral, limite_infinito, limite_forma_indeterminada
from .aplicacoes import (
    taxa_variacao,
    encontrar_criticos,
    encontrar_inflexao,
    lhopital_estendido,
    teorema_valor_medio,
    esboco_curva,
    otimizar,
    volume_disco,
    volume_casca,
    comprimento_arco,
)
