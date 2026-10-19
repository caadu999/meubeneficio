from decimal import Decimal

from direitos.motor.calcular_renda_por_pessoa import calcular_renda_por_pessoa
from direitos.schemas.beneficio import Beneficio, FamiliaEntrada


def avaliar_gas_do_povo(
    familia: FamiliaEntrada,
    salario_minimo: Decimal,
) -> Beneficio:
    motivos = []
    renda_por_pessoa = calcular_renda_por_pessoa(
        familia.renda_familiar_mensal,
        familia.quantidade_pessoas,
    )

    atende_renda = renda_por_pessoa <= salario_minimo / 2

    if not atende_renda:
        motivos.append("Família não atende regra de renda")
    if not familia.inscrita_no_cadunico:
        motivos.append("Família não inscrita no Cadúnico")

    return Beneficio(
        beneficio="Gás do povo",
        atende=len(motivos) == 0,
        motivos=motivos,
        renda_por_pessoa=renda_por_pessoa,
        limite_renda=salario_minimo / 2,
        idade_minima=None,
        codigo="gas_do_povo"
    )
