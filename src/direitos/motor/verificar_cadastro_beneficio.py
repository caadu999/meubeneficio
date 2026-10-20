from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from direitos.models.beneficio import Beneficio


def verificar_cadastro_beneficio(session: Session, codigo: str) -> Beneficio:
    """Verifica se o benefício está cadastrado na API"""
    beneficio = session.scalar(
        select(Beneficio).where(Beneficio.codigo == codigo)
    )
    if beneficio is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Benefício não encontrado: {codigo}",
        )
    return beneficio
