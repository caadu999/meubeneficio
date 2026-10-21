from decimal import Decimal

from direitos.schemas.beneficio import Beneficio, FamiliaEntrada


def avaliar_carteira_da_pessoa_idosa(
    familia: FamiliaEntrada, idade_minima: int, salario_minimo: Decimal
) -> Beneficio:
    motivos = []
    limite_renda = salario_minimo * 2

    atende_cadUnico = familia.inscrita_no_cadunico
    if not atende_cadUnico:
        motivos.append("Precisa estar inscrito(a) no cadUnico")
    atende_idade = familia.idade >= idade_minima
    if not atende_idade:
        motivos.append("Não atende aos requisitos de idade")
    atende_renda = familia.renda_individual_mensal <= limite_renda
    if not atende_renda:
        motivos.append("Não atende aos requisitos de renda")

    return Beneficio(
        beneficio="Carteira da Pessoa Idosa",
        atende=atende_idade and atende_cadUnico and atende_renda,
        motivos=motivos,
        renda_por_pessoa=None,
        limite_renda=limite_renda,
        idade_minima=idade_minima,
        codigo="carteira_da_pessoa_idosa",
    )
