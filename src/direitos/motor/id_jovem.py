from decimal import Decimal

from direitos.schemas.beneficio import Beneficio, FamiliaEntrada

IDADE_MAXIMA_ID_JOVEM = 29


def verificar_id_jovem(
    familia: FamiliaEntrada,
    salario_minimo: Decimal,
    idade_minima: int = 15,
) -> Beneficio:
    motivos = []

    limite_renda = salario_minimo * 2

    atende_cadUnico = familia.inscrita_no_cadunico
    atende_renda = familia.renda_familiar_mensal <= limite_renda
    atende_idade = idade_minima <= familia.idade <= IDADE_MAXIMA_ID_JOVEM

    if not atende_renda:
        motivos.append("Não atende requisitos de renda")
    if not atende_idade:
        motivos.append("Não atende requisito de idade")
    if not atende_cadUnico:
        motivos.append("Você precisa estar cadastrado(a) no CadÚnico")

    return Beneficio(
        beneficio="ID Jovem",
        atende=atende_renda and atende_idade and atende_cadUnico,
        motivos=motivos,
        renda_por_pessoa=None,
        limite_renda=limite_renda,
        idade_minima=idade_minima,
        codigo="id_jovem",
    )
