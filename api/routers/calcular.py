from fastapi import APIRouter, HTTPException
from api.schemas import CalcularRequest, CalcularResponse, PassoResponse
from engine.solver import Solver
from engine.parser import ParserError, TokenizadorError

router = APIRouter()


@router.post("/calcular", response_model=CalcularResponse)
def calcular(req: CalcularRequest):
    """Resolve uma expressão matemática e retorna resultado com passos."""
    try:
        solver = Solver(verbosidade=req.verbosidade)
        resultado = solver.resolver(req.expressao)
        dados = resultado.serializar()

        return CalcularResponse(
            entrada=dados['entrada'],
            latex_entrada=dados['latex_entrada'],
            latex_resultado=dados['latex_resultado'],
            valor_numerico=dados['valor_numerico'],
            passos=[PassoResponse(**p) for p in dados['passos']],
        )
    except (ParserError, TokenizadorError) as e:
        return CalcularResponse(
            entrada=req.expressao,
            latex_entrada=req.expressao,
            latex_resultado="",
            valor_numerico="",
            passos=[],
            erro=f"Erro de parsing: {str(e)}",
        )
    except (ValueError, ZeroDivisionError) as e:
        return CalcularResponse(
            entrada=req.expressao,
            latex_entrada=req.expressao,
            latex_resultado="",
            valor_numerico="",
            passos=[],
            erro=f"Erro matemático: {str(e)}",
        )
    except Exception:
        return CalcularResponse(
            entrada=req.expressao,
            latex_entrada=req.expressao,
            latex_resultado="",
            valor_numerico="",
            passos=[],
            erro="Erro interno",
        )
