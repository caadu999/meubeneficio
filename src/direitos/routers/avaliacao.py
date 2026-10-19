from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from direitos.database.database import get_session
from direitos.models.beneficio import Beneficio
from direitos.motor.verificar_beneficios import verificar_beneficios
from direitos.schemas.beneficio import AvaliacaoResposta, FamiliaEntrada

router = APIRouter()

type SessionDB = Annotated[Session, Depends(get_session)]


@router.post(
    "/avaliar", status_code=HTTPStatus.OK, response_model=AvaliacaoResposta
)
def avaliar(familia: FamiliaEntrada, session: SessionDB):
    """Avalia elegibilidade do usuário para os benefícios"""

    bolsa_familia = session.scalar(
        select(Beneficio).where(Beneficio.codigo == "bolsa_familia")
    )

    if bolsa_familia is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Benefício não encontrado"
        )

    limite = bolsa_familia.limite_renda_por_pessoa

    if limite is None:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Limite não cadastrado",
        )

    bpc = session.scalar(select(Beneficio).where(Beneficio.codigo == "bpc"))

    if bpc is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Benefício não encontrado"
        )

    limite_renda_bpc = bpc.limite_renda_por_pessoa

    if limite_renda_bpc is None:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Limite não cadastrado",
        )

    beneficios = verificar_beneficios(
        limite=limite, familia=familia, limite_renda_bpc=limite_renda_bpc
    )
    return {"beneficios": beneficios}
