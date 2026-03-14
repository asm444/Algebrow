from pydantic import BaseModel, Field


class CalcularRequest(BaseModel):
    expressao: str = Field(..., description="Expressão matemática em texto", examples=["sqrt(216)", "3/4 + 1/4", "log_3(9)"])
    modo: str = Field(default="simplificar", description="Modo de resolução", examples=["simplificar"])
    verbosidade: int = Field(default=3, ge=0, le=4, description="Nível de detalhe dos passos (0=resultado, 4=micro-operações)")


class PassoResponse(BaseModel):
    nivel: int
    descricao: str
    regra: str
    justificativa: str = ""
    metodo: str = ""
    latex_antes: str = ""
    latex_depois: str = ""


class CalcularResponse(BaseModel):
    entrada: str
    latex_entrada: str
    latex_resultado: str
    valor_numerico: str
    passos: list[PassoResponse]
    erro: str = ""
