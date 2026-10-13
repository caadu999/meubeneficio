from decimal import Decimal

from direitos.motor.calcular_renda_por_pessoa import calcular_renda_por_pessoa
from direitos.schemas.beneficio import Beneficio, FamiliaEntrada


def avaliar_bolsa_familia(
    familia: FamiliaEntrada, limite: Decimal
) -> Beneficio:
    motivos = []

    renda = calcular_renda_por_pessoa(
        familia.renda_familiar_mensal, familia.quantidade_pessoas
    )
    atende_regra = renda <= limite

    if not familia.inscrita_no_cadunico:
        motivos.append("Família não inscrita no Cadúnico")
    if not atende_regra:
        motivos.append("Família não atende regra de renda")

    return Beneficio(
        beneficio="Bolsa Família", atende=len(motivos) == 0, motivos=motivos
    )
