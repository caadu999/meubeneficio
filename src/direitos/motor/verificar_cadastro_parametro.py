from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from direitos.models.beneficio import ParametrosGerais


def verificar_cadastro_parametro(
    session: Session, nome: str
) -> ParametrosGerais:
    """Verifica se o parâmetro está cadastrado na API"""
    parametro = session.scalar(
        select(ParametrosGerais).where(ParametrosGerais.nome == nome)
    )
    if parametro is None:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Parâmetro obrigatório não encontrado: {nome}",
        )
    return parametro
