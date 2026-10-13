from decimal import Decimal


def atende_regra_de_renda(
    renda_por_pessoa: Decimal,
    salario_minimo: Decimal,
) -> bool:
    limite = salario_minimo / 2
    return renda_por_pessoa <= limite
