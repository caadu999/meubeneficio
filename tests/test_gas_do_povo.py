from decimal import Decimal

import pytest

from direitos.motor.gas_do_povo import avaliar_gas_do_povo
from direitos.schemas.beneficio import FamiliaEntrada


@pytest.mark.parametrize(
    (
        "quantidade_pessoas",
        "renda_familiar",
        "cadunico",
        "salario_minimo",
        "esperado_atende",
        "esperado_motivos",
        "esperada_renda_por_pessoa",
    ),
    [
        pytest.param(
            2,
            Decimal("1000.00"),
            True,
            Decimal("1621.00"),
            True,
            [],
            Decimal("500.00"),
            id="todos-os-requisitos",
        ),
        pytest.param(
            2,
            Decimal("1621.00"),
            True,
            Decimal("1621.00"),
            True,
            [],
            Decimal("810.50"),
            id="renda-exatamente-no-limite",
        ),
        pytest.param(
            2,
            Decimal("1621.02"),
            True,
            Decimal("1621.00"),
            False,
            ["Família não atende regra de renda"],
            Decimal("810.51"),
            id="renda-um-centavo-acima-por-pessoa",
        ),
        pytest.param(
            1,
            Decimal("500.00"),
            True,
            Decimal("1621.00"),
            False,
            [
                "O programa é voltado preferencialmente para famílias "
                "com 2 ou mais integrantes"
            ],
            Decimal("500.00"),
            id="apenas-um-integrante",
        ),
        pytest.param(
            2,
            Decimal("1000.00"),
            False,
            Decimal("1621.00"),
            False,
            ["Precisa estar inscrito(a) no CadÚnico"],
            Decimal("500.00"),
            id="sem-cadunico",
        ),
        pytest.param(
            1,
            Decimal("1000.00"),
            False,
            Decimal("1621.00"),
            False,
            [
                "O programa é voltado preferencialmente para famílias "
                "com 2 ou mais integrantes",
                "Família não atende regra de renda",
                "Precisa estar inscrito(a) no CadÚnico",
            ],
            Decimal("1000.00"),
            id="falha-em-todos-os-requisitos",
        ),
        pytest.param(
            2,
            Decimal("0.00"),
            True,
            Decimal("1621.00"),
            True,
            [],
            Decimal("0.00"),
            id="renda-zero",
        ),
        pytest.param(
            4,
            Decimal("2000.00"),
            True,
            Decimal("1621.00"),
            True,
            [],
            Decimal("500.00"),
            id="familia-com-quatro-integrantes",
        ),
        pytest.param(
            2,
            Decimal("2000.00"),
            True,
            Decimal("2000.00"),
            True,
            [],
            Decimal("1000.00"),
            id="limite-acompanha-salario-informado",
        ),
    ],
)
def test_avaliar_gas_do_povo(
    quantidade_pessoas,
    renda_familiar,
    cadunico,
    salario_minimo,
    esperado_atende,
    esperado_motivos,
    esperada_renda_por_pessoa,
):
    familia = FamiliaEntrada(
        inscrita_no_cadunico=cadunico,
        renda_familiar_mensal=renda_familiar,
        quantidade_pessoas=quantidade_pessoas,
        idade=30,
        pcd=False,
        renda_individual_mensal=Decimal("0.00"),
    )
    resultado = avaliar_gas_do_povo(
        familia=familia, salario_minimo=salario_minimo
    )

    assert resultado.beneficio == "Gás do Povo"
    assert resultado.codigo == "gas_do_povo"
    assert resultado.atende is esperado_atende
    assert resultado.motivos == esperado_motivos
    assert resultado.renda_por_pessoa == esperada_renda_por_pessoa
    assert resultado.limite_renda == salario_minimo / 2
    assert resultado.idade_minima is None
