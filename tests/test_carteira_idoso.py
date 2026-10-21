from decimal import Decimal

import pytest

from direitos.motor.carteira_da_pessoa_idosa import (
    avaliar_carteira_da_pessoa_idosa,
)
from direitos.schemas.beneficio import FamiliaEntrada


@pytest.mark.parametrize(
    (
        "idade",
        "salario_minimo",
        "cadunico",
        "renda_individual",
        "esperado_atende",
        "esperado_motivos",
    ),
    [
        pytest.param(
            59,
            Decimal("1621.00"),
            True,
            Decimal("1500.00"),
            False,
            ["Não atende aos requisitos de idade"],
            id="idade-abaixo-da-idade-minima",
        ),
        pytest.param(
            60,
            Decimal("1621.00"),
            True,
            Decimal("3242.00"),
            True,
            [],
            id="tudo-atende-no-limite",
        ),
        pytest.param(
            61,
            Decimal("1621.00"),
            True,
            Decimal("3244.00"),
            False,
            ["Não atende aos requisitos de renda"],
            id="renda-acima-do-limite",
        ),
        pytest.param(
            61,
            Decimal("1621.00"),
            False,
            Decimal("1500.00"),
            False,
            ["Precisa estar inscrito(a) no cadUnico"],
            id="nao-inscrito-no-cadunico",
        ),
        pytest.param(
            59,
            Decimal("1621.00"),
            False,
            Decimal("3242.01"),
            False,
            [
                "Precisa estar inscrito(a) no cadUnico",
                "Não atende aos requisitos de idade",
                "Não atende aos requisitos de renda",
            ],
            id="falha-em-todos-os-requisitos",
        ),
    ],
)
def test_validar_carteira_idoso(
    idade,
    salario_minimo,
    cadunico,
    esperado_atende,
    renda_individual,
    esperado_motivos,
):
    idade_minima = 60
    limite_renda = Decimal(salario_minimo * 2)

    familia = FamiliaEntrada(
        inscrita_no_cadunico=cadunico,
        renda_familiar_mensal=Decimal("0.00"),
        quantidade_pessoas=1,
        idade=idade,
        pcd=False,
        renda_individual_mensal=renda_individual,
    )

    resultado = avaliar_carteira_da_pessoa_idosa(
        familia=familia,
        idade_minima=idade_minima,
        salario_minimo=salario_minimo,
    )

    assert resultado.beneficio == "Carteira da Pessoa Idosa"
    assert resultado.atende is esperado_atende
    assert resultado.motivos == esperado_motivos
    assert resultado.renda_por_pessoa is None
    assert resultado.limite_renda == limite_renda
    assert resultado.idade_minima == idade_minima
    assert resultado.codigo == "carteira_da_pessoa_idosa"
