from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from direitos.database.database import get_session
from direitos.models.beneficio import ParametrosGerais
from direitos.schemas.beneficio import (
    AtualizarParametro,
    CriarParametro,
    ParametroPublic,
)
from direitos.utils.senha_hash import get_current_active_user

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
    "/",
    response_model=ParametroPublic,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(get_current_active_user)],
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


@router.patch(
    "/{parametro_id}",
    response_model=ParametroPublic,
    dependencies=[Depends(get_current_active_user)],
)
def atualizar_parametro(
    session: SessionDB, parametro_id: int, parametro: AtualizarParametro
):
    parametroDB = session.scalar(
        select(ParametrosGerais).where(ParametrosGerais.id == parametro_id)
    )

    if parametroDB is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Parâmetro não encontrado"
        )
    alteracoes = parametro.model_dump(exclude_unset=True)

    for campo in ("nome", "valor"):
        if campo in alteracoes and alteracoes[campo] is None:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=f"O campo {campo} não pode ser null",
            )
    for key, value in alteracoes.items():
        setattr(parametroDB, key, value)

    try:
        session.commit()
        session.refresh(parametroDB)
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Não foi possível alterar devido a um conflito",
        ) from err
    return parametroDB


@router.delete(
    "/{parametro_id}", dependencies=[Depends(get_current_active_user)]
)
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
