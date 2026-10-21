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

    atende_quantidade = familia.quantidade_pessoas >= 2
    atende_cadunico = familia.inscrita_no_cadunico
    limite_renda = salario_minimo / 2
    atende_renda = renda_por_pessoa <= limite_renda

    if not atende_quantidade:
        motivos.append(
            "O programa é voltado preferencialmente para famílias com 2 ou mais integrantes"
        )
    if not atende_renda:
        motivos.append("Família não atende regra de renda")
    if not atende_cadunico:
        motivos.append("Precisa estar inscrito(a) no CadÚnico")

    return Beneficio(
        beneficio="Gás do Povo",
        atende=not motivos,
        motivos=motivos,
        renda_por_pessoa=renda_por_pessoa,
        limite_renda=limite_renda,
        idade_minima=None,
        codigo="gas_do_povo",
    )
