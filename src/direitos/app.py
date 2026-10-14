from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from direitos.database.database import get_session
from direitos.models.beneficio import Beneficio, Requisitos
from direitos.motor.verificar_beneficios import verificar_beneficios
from direitos.schemas.beneficio import (
    AvaliacaoResposta,
    BeneficioResposta,
    CriarBeneficio,
    CriarRequisitos,
    FamiliaEntrada,
    RespostaRequisito,
)

app = FastAPI()


@app.get("/")
def get_users():
    return {"message": "ooi"}


@app.get("/beneficios", response_model=list[BeneficioResposta])
def carregar_beneficios(session: Session = Depends(get_session)):
    dados = session.scalars(select(Beneficio)).all()

    if not dados:
        raise HTTPException(
            status_code=HTTPStatus.OK, detail="Não há dados para mostrar"
        )

    return dados


@app.post("/beneficios", response_model=CriarBeneficio)
def cadastrar_beneficio(
    beneficio: CriarBeneficio, session: Session = Depends(get_session)
):
    novo_beneficio = Beneficio(nome=beneficio.nome)

    try:
        session.add(novo_beneficio)
        session.commit()
        session.refresh(novo_beneficio)
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Não foi possível cadastrar benefício devido a erro de conflito",
        ) from err
    return novo_beneficio


@app.post(
    "/beneficios/{beneficio_id}/requisitos", response_model=RespostaRequisito
)
def criar_requisitos(
    beneficio_id: int,
    requisitos: CriarRequisitos,
    session: Session = Depends(get_session),
):
    beneficio = session.scalar(
        select(Beneficio).where(Beneficio.id == beneficio_id)
    )

    if beneficio is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Benefício não encontrado"
        )
    novo_requisito = Requisitos(descricao=requisitos.descricao)

    try:
        beneficio.requisito.append(novo_requisito)
        session.commit()
        session.refresh(novo_requisito)
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Não foi possível cadastrar requisito devido a erro "
            "de conflito",
        ) from err
    return novo_requisito


@app.delete("/beneficios/{beneficio_id}/{requisito_id}")
def deletar_requisito(
    requisito_id: int,
    beneficio_id: int,
    session: Session = Depends(get_session),
):
    pass


@app.post("/avaliar", response_model=AvaliacaoResposta)
def avaliar(familia: FamiliaEntrada):
    beneficios = verificar_beneficios(familia)
    return {"beneficios": beneficios}
