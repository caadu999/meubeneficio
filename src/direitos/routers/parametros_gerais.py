from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from direitos.database.database import get_session
from direitos.models.beneficio import ParametrosGerais
from direitos.schemas.beneficio import CriarParametro, ParametroPublic

router = APIRouter(prefix="/gerais", tags=["parâmetros gerais"])

type SessionDB = Annotated[Session, Depends(get_session)]


@router.get(
    "/", response_model=list[ParametroPublic], status_code=HTTPStatus.OK
)
def carregar_parametros(session: SessionDB):
    """Carrega todos os parâmetros cadastrados"""

    parametros = session.scalars(select(ParametrosGerais)).all()

    if not parametros:
        raise HTTPException(
            status_code=HTTPStatus.OK, detail="Não há parametros registrados"
        )
    return parametros


@router.post(
    "/", response_model=ParametroPublic, status_code=HTTPStatus.CREATED
)
def cadastrar_parametro(session: SessionDB, parametro: CriarParametro):
    """Cadastra novos parâmetros"""
    novo_parametro = ParametrosGerais(
        nome=parametro.nome, valor=parametro.valor
    )

    try:
        session.add(novo_parametro)
        session.commit()
        session.refresh(novo_parametro)
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Erro de conflito ao adicionar",
        ) from err

    return novo_parametro


@router.delete("/{parametro_id}")
def deletar_parametro(session: SessionDB, parametro_id: int):
    """Deleta um parâmetro pela ID"""
    parametro = session.scalar(
        select(ParametrosGerais).where(ParametrosGerais.id == parametro_id)
    )

    if parametro is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Parâmetro não encontrado"
        )
    try:
        session.delete(parametro)
        session.commit()
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Erro de conflito ao tentar deletar parâmetro",
        ) from err
    return {"message": "Parâmetro deletado com sucesso"}
