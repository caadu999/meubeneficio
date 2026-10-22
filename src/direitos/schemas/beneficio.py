from decimal import Decimal

from pydantic import BaseModel, Field


class FamiliaEntrada(BaseModel):
    inscrita_no_cadunico: bool = Field(strict=True)
    renda_familiar_mensal: Decimal = Field(ge=0)
    quantidade_pessoas: int = Field(gt=0, strict=True)
    idade: int = Field(gt=0, strict=True)
    pcd: bool = Field(strict=True)
    renda_individual_mensal: Decimal = Field(ge=0)


class Beneficio(BaseModel):
    beneficio: str
    atende: bool
    motivos: list[str]
    renda_por_pessoa: Decimal | None
    limite_renda: Decimal
    idade_minima: int | None
    codigo: str


class AvaliacaoResposta(BaseModel):
    beneficios: list[Beneficio]


class CriarRequisitos(BaseModel):
    descricao: str


class CriarBeneficio(BaseModel):
    nome: str
    limite_renda_por_pessoa: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2,
    )
    codigo: str
    idade_minima: int | None = Field(
        ge=0,
        default=None,
    )


class AtualizarBeneficio(BaseModel):
    nome: str | None = Field(min_length=1, default=None)
    limite_renda_por_pessoa: Decimal | None = Field(
        ge=0, decimal_places=2, max_digits=10, default=None
    )
    codigo: str | None = Field(min_length=1, default=None)
    idade_minima: int | None = Field(ge=0, default=None)


class RespostaRequisito(CriarRequisitos):
    id: int


class BeneficioResposta(BaseModel):
    id: int
    nome: str
    requisito: list[RespostaRequisito]
    limite_renda_por_pessoa: Decimal | None
    idade_minima: int | None
    codigo: str


class AtualizarLimite(BaseModel):
    novo_limite: Decimal = Field(ge=0, decimal_places=2)


class CriarParametro(BaseModel):
    nome: str
    valor: Decimal = Field(
        ge=0,
        decimal_places=2,
        max_digits=10,
    )


class AtualizarParametro(BaseModel):
    nome: str | None = (Field(min_length=1, default=None),)
    valor: Decimal | None = Field(
        ge=0, max_digits=10, decimal_places=2, default=None
    )


class ParametroPublic(BaseModel):
    id: int
    nome: str
    valor: Decimal
