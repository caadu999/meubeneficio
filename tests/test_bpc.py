from decimal import Decimal

import pytest

from direitos.motor.bpc import avaliar_bpc
from direitos.schemas.beneficio import FamiliaEntrada


@pytest.mark.parametrize(
    (
        "idade",
        "pcd",
        "renda_familiar",
        "quantidade_pessoas",
        "cadunico",
        "esperado_atende",
        "esperado_motivos",
        "esperada_renda_por_pessoa",
    ),
    [
        pytest.param(
            65,
            False,
            Decimal("600.00"),
            2,
            True,
            True,
            [],
            Decimal("300.00"),
            id="idade-exatamente-no-limite",
        ),
        pytest.param(
            30,
            True,
            Decimal("600.00"),
            2,
            True,
            True,
            [],
            Decimal("300.00"),
            id="pcd-abaixo-da-idade-minima",
        ),
        pytest.param(
            66,
            True,
            Decimal("600.00"),
            2,
            True,
            True,
            [],
            Decimal("300.00"),
            id="idade-e-pcd-atendem",
        ),
        pytest.param(
            64,
            False,
            Decimal("600.00"),
            2,
            True,
            False,
            ["Não atende ao critério de idade ou deficiência informado"],
            Decimal("300.00"),
            id="abaixo-da-idade-minima-sem-pcd",
        ),
        pytest.param(
            65,
            False,
            Decimal("810.50"),
            2,
            True,
            True,
            [],
            Decimal("405.25"),
            id="renda-exatamente-no-limite",
        ),
        pytest.param(
            65,
            False,
            Decimal("810.52"),
            2,
            True,
            False,
            ["Renda por pessoa acima do limite"],
            Decimal("405.26"),
            id="renda-um-centavo-acima-por-pessoa",
        ),
        pytest.param(
            30,
            True,
            Decimal("810.52"),
            2,
            True,
            False,
            ["Renda por pessoa acima do limite"],
            Decimal("405.26"),
            id="pcd-nao-dispensa-criterio-de-renda",
        ),
        pytest.param(
            65,
            False,
            Decimal("600.00"),
            2,
            False,
            False,
            ["Precisa estar inscrito(a) no CadÚnico"],
            Decimal("300.00"),
            id="sem-cadunico",
        ),
        pytest.param(
            64,
            False,
            Decimal("1000.00"),
            2,
            False,
            False,
            [
                "Não atende ao critério de idade ou deficiência informado",
                "Renda por pessoa acima do limite",
                "Precisa estar inscrito(a) no CadÚnico",
            ],
            Decimal("500.00"),
            id="falha-em-todos-os-criterios",
        ),
        pytest.param(
            65,
            False,
            Decimal("0.00"),
            1,
            True,
            True,
            [],
            Decimal("0.00"),
            id="renda-zero",
        ),
        pytest.param(
            65,
            False,
            Decimal("1200.00"),
            4,
            True,
            True,
            [],
            Decimal("300.00"),
            id="familia-com-quatro-integrantes",
        ),
    ],
)
def test_avaliar_bpc_cenarios(
    idade,
    pcd,
    renda_familiar,
    quantidade_pessoas,
    cadunico,
    esperado_atende,
    esperado_motivos,
    esperada_renda_por_pessoa,
):
    salario_minimo = Decimal("1621.00")
    idade_minima_bpc = 65

    familia = FamiliaEntrada(
        inscrita_no_cadunico=cadunico,
        renda_familiar_mensal=renda_familiar,
        quantidade_pessoas=quantidade_pessoas,
        idade=idade,
        pcd=pcd,
        renda_individual_mensal=Decimal("0.00"),
    )

    resultado = avaliar_bpc(
        familia=familia,
        salario_minimo=salario_minimo,
        idade_minima_bpc=idade_minima_bpc,
    )

    assert resultado.beneficio == "BPC"
    assert resultado.codigo == "bpc"
    assert resultado.atende is esperado_atende
    assert resultado.motivos == esperado_motivos
    assert resultado.renda_por_pessoa == esperada_renda_por_pessoa
    assert resultado.limite_renda == Decimal("405.25")
    assert resultado.idade_minima == idade_minima_bpc
