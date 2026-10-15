from fastapi import FastAPI

from direitos.motor.verificar_beneficios import verificar_beneficios
from direitos.routers import beneficios
from direitos.schemas.beneficio import (
    AvaliacaoResposta,
    FamiliaEntrada,
)

app = FastAPI()
app.include_router(beneficios.router)


@app.get("/")
def get_users():
    return {"message": "ooi"}


@app.post("/avaliar", response_model=AvaliacaoResposta)
def avaliar(familia: FamiliaEntrada):
    """Avalia elegibilidade do usuário para os benefícios"""
    beneficios = verificar_beneficios(familia)
    return {"beneficios": beneficios}
