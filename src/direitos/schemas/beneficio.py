from decimal import Decimal

from pydantic import BaseModel, Field


class FamiliaEntrada(BaseModel):
    inscrita_no_cadunico: bool
    renda_familiar_mensal: Decimal = Field(ge=0)
    quantidade_pessoas: int = Field(gt=0, strict=True)
    idade: int = (Field(gt=0, strict=True),)
    pcd: bool


class Beneficio(BaseModel):
    beneficio: str
    atende: bool
    motivos: list[str]


class AvaliacaoResposta(BaseModel):
    beneficios: list[Beneficio]


class CriarRequisitos(BaseModel):
    descricao: str


class CriarBeneficio(BaseModel):
    nome: str


class RespostaRequisito(CriarRequisitos):
    id: int


class BeneficioResposta(BaseModel):
    id: int
    nome: str
    requisito: list[RespostaRequisito]
