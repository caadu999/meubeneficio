from fastapi import FastAPI

from direitos.routers import auth, avaliacao, beneficios, parametros_gerais

app = FastAPI()
app.include_router(beneficios.router)
app.include_router(avaliacao.router)
app.include_router(parametros_gerais.router)
app.include_router(auth.router)


@app.get("/")
def get_users():
    return {"message": "ooi"}
