from decimal import Decimal

import pytest

from direitos.motor.id_jovem import verificar_id_jovem
from direitos.schemas.beneficio import FamiliaEntrada


@pytest.mark.parametrize(
    (
        "idade",
        "renda",
        "cadunico",
        "salario_minimo",
        "esperado_atende",
        "esperado_motivos",
    ),
    [
        pytest.param(
            15,
            Decimal("1000.00"),
            True,
            Decimal("1621.00"),
            True,
            [],
            id="todos-atendem",
        ),
        pytest.param(
            14,
            Decimal("1000.00"),
            True,
            Decimal("1621.00"),
            False,
            ["Não atende requisito de idade"],
            id="nao-atende-requisito-de-idade",
        ),
        pytest.param(
            29,
            Decimal("1000.00"),
            True,
            Decimal("1621.00"),
            True,
            [],
            id="idade-dentro-do-limite",
        ),
        pytest.param(
            30,
            Decimal("1500.00"),
            True,
            Decimal("1621.00"),
            False,
            ["Não atende requisito de idade"],
            id="idade-acima-do-limite-maximo",
        ),
        pytest.param(
            35,
            Decimal("4000.00"),
            False,
            Decimal("1621.00"),
            False,
            [
                "Não atende requisitos de renda",
                "Não atende requisito de idade",
                "Você precisa estar cadastrado(a) no CadÚnico",
            ],
            id="sem-cadunico-e-idade-e-renda-acima-do-limite",
        ),
        pytest.param(
            20,
            Decimal("3500.00"),
            True,
            Decimal("2000.00"),
            True,
            [],
            id="dados-diferentes-para-verificar-motor",
        ),
        pytest.param(
            20,
            Decimal("3242.00"),
            True,
            Decimal("1621.00"),
            True,
            [],
            id="renda-exatamente-no-limite",
        ),
        pytest.param(
            20,
            Decimal("3242.01"),
            True,
            Decimal("1621.00"),
            False,
            ["Não atende requisitos de renda"],
            id="renda-um-centavo-acima-do-limite",
        ),
        pytest.param(
            20,
            Decimal("1000.00"),
            False,
            Decimal("1621.00"),
            False,
            ["Você precisa estar cadastrado(a) no CadÚnico"],
            id="somente-cadunico-nao-atende",
        ),
    ],
)
def test_verificar_id_jovem_cenarios(
    idade, renda, cadunico, salario_minimo, esperado_atende, esperado_motivos
):
    familia = FamiliaEntrada(
        idade=idade,
        renda_familiar_mensal=renda,
        inscrita_no_cadunico=cadunico,
        quantidade_pessoas=2,
        pcd=False,
        renda_individual_mensal=Decimal("0.00"),
    )

    resultado = verificar_id_jovem(
        familia=familia,
        salario_minimo=salario_minimo,
    )

    assert resultado.beneficio == "ID Jovem"
    assert resultado.codigo == "id_jovem"
    assert resultado.atende is esperado_atende
    assert resultado.motivos == esperado_motivos
    assert resultado.limite_renda == salario_minimo * 2
    assert resultado.renda_por_pessoa is None
    assert resultado.idade_minima == 15
