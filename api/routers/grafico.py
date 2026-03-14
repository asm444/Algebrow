from fastapi import APIRouter
from api.schemas import GraficoRequest, GraficoResponse
from engine.funcoes.grafico import gerar_pontos

router = APIRouter()


@router.post("/grafico", response_model=GraficoResponse)
def grafico(req: GraficoRequest):
    """Gera pontos para gráfico 2D de uma expressão."""
    try:
        dados = gerar_pontos(req.expressao, req.x_min, req.x_max, req.num_pontos)
        return GraficoResponse(
            x=dados["x"],
            y=dados["y"],
            assintotas_verticais=dados["assintotas_verticais"],
            x_min=dados["x_min"],
            x_max=dados["x_max"],
        )
    except ValueError as e:
        return GraficoResponse(
            x=[], y=[], assintotas_verticais=[],
            x_min=req.x_min, x_max=req.x_max,
            erro=f"Erro: {str(e)}",
        )
    except Exception:
        return GraficoResponse(
            x=[], y=[], assintotas_verticais=[],
            x_min=req.x_min, x_max=req.x_max,
            erro="Erro interno",
        )
