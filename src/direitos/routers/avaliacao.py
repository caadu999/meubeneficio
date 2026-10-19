from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from direitos.database.database import get_session
from direitos.motor.verificar_beneficios import verificar_beneficios
from direitos.motor.verificar_cadastro_beneficio import (
    verificar_cadastro_beneficio,
)
from direitos.motor.verificar_cadastro_parametro import (
    verificar_cadastro_parametro,
)
from direitos.schemas.beneficio import AvaliacaoResposta, FamiliaEntrada

router = APIRouter(prefix="/avaliar", tags=["avaliação"])

type SessionDB = Annotated[Session, Depends(get_session)]


@router.post("/", status_code=HTTPStatus.OK, response_model=AvaliacaoResposta)
def avaliar(familia: FamiliaEntrada, session: SessionDB):
    """Avalia elegibilidade do usuário para os benefícios"""

    parametro = verificar_cadastro_parametro(session, "salario_minimo")

    salario_minimo = parametro.valor

    bolsa_familia = verificar_cadastro_beneficio(session, "bolsa_familia")

    limite = bolsa_familia.limite_renda_por_pessoa
    if limite is None:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Limite não cadastrado",
        )

    verificar_cadastro_beneficio(session, "gas_do_povo")

    bpc = verificar_cadastro_beneficio(session, "bpc")

    idade_minima_bpc = bpc.idade_minima
    if idade_minima_bpc is None:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Idade mínima não cadastrada",
        )

    beneficios = verificar_beneficios(
        limite=limite,
        familia=familia,
        idade_minima_bpc=idade_minima_bpc,
        salario_minimo=salario_minimo,
    )
    return {"beneficios": beneficios}
