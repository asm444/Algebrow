class FuncaoBase:
    """Interface comum para todas as funções."""
    def __init__(self, nome: str, variavel: str = 'x'):
        self.nome = nome
        self.variavel = variavel
        self.tipo = 'funcao'

    def avaliar(self, x: str) -> str:
        """Retorna f(x) como string exata."""
        raise NotImplementedError

    def dominio(self) -> str:
        """Retorna domínio em notação de intervalo."""
        raise NotImplementedError

    def imagem(self) -> str:
        """Retorna imagem em notação de intervalo."""
        raise NotImplementedError

    def representacao_latex(self) -> str:
        raise NotImplementedError

    def zeros(self) -> list:
        """Retorna os zeros da função."""
        raise NotImplementedError
