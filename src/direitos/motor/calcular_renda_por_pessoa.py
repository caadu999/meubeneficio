from decimal import Decimal


def calcular_renda_por_pessoa(
    renda_familiar: Decimal,
    quantidade_pessoas: int,
) -> Decimal:
    return renda_familiar / quantidade_pessoas
