from decimal import Decimal

from direitos.motor.bolsa_familia import avaliar_bolsa_familia
from direitos.motor.bpc import avaliar_bpc
from direitos.motor.gas_do_povo import avaliar_gas_do_povo
from direitos.motor.id_jovem import verificar_id_jovem
from direitos.schemas.beneficio import Beneficio, FamiliaEntrada


def verificar_beneficios(
    limite: Decimal,
    familia: FamiliaEntrada,
    salario_minimo: Decimal,
    idade_minima_bpc: int,
) -> list[Beneficio]:

    bolsa = avaliar_bolsa_familia(familia=familia, limite=limite)
    gas = avaliar_gas_do_povo(familia=familia, salario_minimo=salario_minimo)
    bpc = avaliar_bpc(
        familia=familia,
        salario_minimo=salario_minimo,
        idade_minima_bpc=idade_minima_bpc,
    )
    id_jovem = verificar_id_jovem(
        familia=familia, salario_minimo=salario_minimo
    )

    return [bolsa, gas, bpc, id_jovem]
