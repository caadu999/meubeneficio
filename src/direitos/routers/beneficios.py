from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from direitos.database.database import get_session
from direitos.models.beneficio import Beneficio, Requisitos
from direitos.schemas.beneficio import (
    AtualizarLimite,
    BeneficioResposta,
    CriarBeneficio,
    CriarRequisitos,
    RespostaRequisito,
)

router = APIRouter(prefix="/beneficios", tags=["beneficios"])

type SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=list[BeneficioResposta])
def carregar_beneficios(session: SessionDep):
    dados = session.scalars(select(Beneficio)).all()

    if not dados:
        raise HTTPException(
            status_code=HTTPStatus.OK, detail="Não há dados para mostrar"
        )

    return dados


@router.post(
    "/", response_model=CriarBeneficio, status_code=HTTPStatus.CREATED
)
def cadastrar_beneficio(beneficio: CriarBeneficio, session: SessionDep):
    """Cadastra novos benefícios"""
    novo_beneficio = Beneficio(
        nome=beneficio.nome,
        limite_renda_por_pessoa=beneficio.limite_renda_por_pessoa,
        codigo=beneficio.codigo,
    )

    try:
        session.add(novo_beneficio)
        session.commit()
        session.refresh(novo_beneficio)
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Erro de conflito ao cadastrar",
        ) from err
    return novo_beneficio


@router.patch("/{beneficio_id}", response_model=BeneficioResposta)
def alterar_limite_beneficio(
    beneficio_id: int, session: SessionDep, limite: AtualizarLimite
):
    """Altera o limite do benefício selecionado"""
    beneficio = session.scalar(
        select(Beneficio).where(Beneficio.id == beneficio_id)
    )

    if beneficio is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Benefício não encontrado.",
        )
    try:
        beneficio.limite_renda_por_pessoa = limite.novo_limite
        session.commit()
        session.refresh(beneficio)
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Erro ao atualizar limite"
        ) from err
    return beneficio


@router.post(
    "/{beneficio_id}/requisitos",
    response_model=RespostaRequisito,
    status_code=HTTPStatus.CREATED,
)
def criar_requisitos(
    beneficio_id: int,
    requisitos: CriarRequisitos,
    session: SessionDep,
):
    """Cria novos requisitos para um benefício"""
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


@router.delete("/{beneficio_id}/{requisito_id}")
def deletar_requisito(
    requisito_id: int,
    beneficio_id: int,
    session: SessionDep,
):
    """Deleta um requisito pelo ID"""

    benficio = session.scalar(
        select(Beneficio).where(Beneficio.id == beneficio_id)
    )

    if benficio is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Benefício não encontrado"
        )

    requisito = session.scalar(
        select(Requisitos).where(
            Requisitos.id == requisito_id
            and Requisitos.beneficio_id == beneficio_id
        )
    )

    if requisito is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Requisito não encontrado"
        )
    try:
        session.delete(requisito)
        session.commit()
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Erro de conflito ao deletar",
        ) from err

    return {"message": "Requisito deletado com sucesso!"}


@router.delete("/{beneficio_id}")
def deletar_beneficio(beneficio_id: int, session: SessionDep):
    """Deleta um benefício pela ID"""

    beneficio = session.scalar(
        select(Beneficio).where(Beneficio.id == beneficio_id)
    )

    if beneficio is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Benefício não encontrado"
        )
    try:
        session.delete(beneficio)
        session.commit()
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Erro de conflito ao deletar",
        ) from err
    return {"message": "Benefício deletado com sucesso!"}
