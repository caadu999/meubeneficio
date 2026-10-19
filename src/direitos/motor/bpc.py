from decimal import Decimal

from direitos.motor.calcular_renda_por_pessoa import calcular_renda_por_pessoa
from direitos.schemas.beneficio import Beneficio, FamiliaEntrada


def avaliar_bpc(
    familia: FamiliaEntrada, limite_renda_bpc: Decimal, idade_minima_bpc: int
) -> Beneficio:
    motivos = []
    atende_regra = familia.idade >= idade_minima_bpc or familia.pcd

    renda = calcular_renda_por_pessoa(
        familia.renda_familiar_mensal, familia.quantidade_pessoas
    )
    atende_renda = renda <= limite_renda_bpc
    atende = atende_renda and atende_regra

    if not atende_regra:
        motivos.append(
            "Não atende ao critério de idade ou deficiência informado"
        )
    if not atende_renda:
        motivos.append("Renda por pessoa acima do limite")

    return Beneficio(beneficio="BPC", atende=atende, motivos=motivos)
