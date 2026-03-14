from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import calcular, grafico

app = FastAPI(
    title="Algebrow API",
    description="Motor matemático simbólico com resolução passo-a-passo",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(calcular.router, prefix="/api", tags=["calcular"])
app.include_router(grafico.router, prefix="/api", tags=["grafico"])


@app.get("/")
def raiz():
    return {"status": "ok", "mensagem": "Algebrow API v0.1.0"}
