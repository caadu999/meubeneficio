from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from direitos.database.database import get_session
from direitos.models.beneficio import Beneficio, Requisitos
from direitos.schemas.beneficio import (
    AtualizarBeneficio,
    BeneficioResposta,
    CriarBeneficio,
    CriarRequisitos,
    RespostaRequisito,
)
from direitos.utils.senha_hash import get_current_active_user

router = APIRouter(prefix="/beneficios", tags=["beneficios"])

type SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=list[BeneficioResposta])
def carregar_beneficios(session: SessionDep):
    """Retorna benefícios cadastrados"""
    dados = session.scalars(select(Beneficio)).all()

    return dados


@router.post(
    "/",
    response_model=BeneficioResposta,
    dependencies=[Depends(get_current_active_user)],
    status_code=HTTPStatus.CREATED,
)
def cadastrar_beneficio(beneficio: CriarBeneficio, session: SessionDep):
    """Cadastra novos benefícios"""
    novo_beneficio = Beneficio(
        nome=beneficio.nome,
        limite_renda_por_pessoa=beneficio.limite_renda_por_pessoa,
        codigo=beneficio.codigo,
        idade_minima=beneficio.idade_minima,
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


@router.patch(
    "/{beneficio_id}",
    response_model=BeneficioResposta,
    dependencies=[Depends(get_current_active_user)],
)
def atualizar_atributos(
    beneficio_id: int, session: SessionDep, beneficio: AtualizarBeneficio
):
    """Atualiza atributos de um benefício"""
    beneficioDB = session.scalar(
        select(Beneficio).where(Beneficio.id == beneficio_id)
    )

    if beneficioDB is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Benefício não encontrado"
        )
    alteracoes = beneficio.model_dump(exclude_unset=True)

    for campo in ("nome", "codigo"):
        if campo in alteracoes and alteracoes[campo] is None:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail=f"O campo {campo} não pode ser null",
            )

    for key, value in alteracoes.items():
        setattr(beneficioDB, key, value)

    try:
        session.commit()
        session.refresh(beneficioDB)
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Não foi possível atualizar o benefício",
        ) from err

    return beneficioDB


@router.post(
    "/{beneficio_id}/requisitos",
    response_model=RespostaRequisito,
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(get_current_active_user)],
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


@router.put(
    "/{beneficio_id}/{requisito_id}",
    dependencies=[Depends(get_current_active_user)],
    response_model=RespostaRequisito,
)
def atualizar_requisito(
    session: SessionDep,
    beneficio_id: int,
    requisito_id: int,
    requisitos: CriarRequisitos,
):
    beneficio = session.scalar(
        select(Beneficio).where(Beneficio.id == beneficio_id)
    )
    if beneficio is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Benefício não encontrado"
        )
    requisito = session.scalar(
        select(Requisitos).where(
            Requisitos.id == requisito_id,
            Requisitos.beneficio_id == beneficio_id,
        )
    )
    if requisito is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Requisito não encontrado"
        )
    requisito.descricao = requisitos.descricao

    try:
        session.commit()
        session.refresh(requisito)
    except IntegrityError as err:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Não foi possível alterar o requisito",
        ) from err

    return requisito


@router.delete(
    "/{beneficio_id}/{requisito_id}",
    dependencies=[Depends(get_current_active_user)],
)
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
            Requisitos.id == requisito_id,
            Requisitos.beneficio_id == beneficio_id,
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


@router.delete(
    "/{beneficio_id}", dependencies=[Depends(get_current_active_user)]
)
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
