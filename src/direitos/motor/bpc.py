from decimal import Decimal

from direitos.motor.calcular_renda_por_pessoa import calcular_renda_por_pessoa
from direitos.schemas.beneficio import Beneficio, FamiliaEntrada


def avaliar_bpc(
    familia: FamiliaEntrada, salario_minimo: Decimal, idade_minima_bpc: int
) -> Beneficio:
    motivos = []
    limite_renda = salario_minimo / 4
    atende_regra = familia.idade >= idade_minima_bpc or familia.pcd
    atende_cadunico = familia.inscrita_no_cadunico

    renda = calcular_renda_por_pessoa(
        familia.renda_familiar_mensal, familia.quantidade_pessoas
    )
    atende_renda = renda <= limite_renda
    atende = atende_renda and atende_regra and atende_cadunico

    if not atende_regra:
        motivos.append(
            "Não atende ao critério de idade ou deficiência informado"
        )
    if not atende_renda:
        motivos.append("Renda por pessoa acima do limite")

    if not atende_cadunico:
        motivos.append("Precisa estar inscrito(a) no CadÚnico")

    return Beneficio(
        beneficio="BPC",
        atende=atende,
        motivos=motivos,
        limite_renda=limite_renda,
        renda_por_pessoa=renda,
        idade_minima=idade_minima_bpc,
        codigo="bpc",
    )
