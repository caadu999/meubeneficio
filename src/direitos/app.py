from fastapi import FastAPI

from direitos.routers import avaliacao, beneficios

app = FastAPI()
app.include_router(beneficios.router)
app.include_router(avaliacao.router)


@app.get("/")
def get_users():
    return {"message": "ooi"}
