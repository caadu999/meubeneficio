from decimal import Decimal

from direitos.motor.bolsa_familia import avaliar_bolsa_familia
from direitos.motor.bpc import avaliar_bpc
from direitos.motor.gas_do_povo import avaliar_gas_do_povo
from direitos.schemas.beneficio import Beneficio, FamiliaEntrada


def verificar_beneficios(
    familia: FamiliaEntrada,
    salario_minimo=Decimal("1621.00"),
    limite=Decimal("218.00"),
    limite_renda_bpc=Decimal("405.25"),
) -> list[Beneficio]:
    bolsa = avaliar_bolsa_familia(familia=familia, limite=limite)
    gas = avaliar_gas_do_povo(familia=familia, salario_minimo=salario_minimo)
    bpc = avaliar_bpc(familia=familia, limite_renda=limite_renda_bpc)

    return [bolsa, gas, bpc]
