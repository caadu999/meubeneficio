from fastapi import FastAPI

from direitos.motor.verificar_beneficios import verificar_beneficios
from direitos.schemas.beneficio import BeneficioResponse, FamiliaEntrada

app = FastAPI()


@app.get("/")
def get_users():
    return {"message": "ooi"}


@app.post("/avaliar", response_model=BeneficioResponse)
def avaliar(familia: FamiliaEntrada):
    beneficios = verificar_beneficios(familia)
    return {"beneficios": beneficios}
