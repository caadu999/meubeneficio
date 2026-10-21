from decimal import Decimal

import pytest

from direitos.motor.bolsa_familia import avaliar_bolsa_familia
from direitos.schemas.beneficio import FamiliaEntrada


@pytest.mark.parametrize(
    (
        "renda_familiar",
        "quantidade_pessoas",
        "cadunico",
        "esperado_atende",
        "esperado_motivos",
        "esperada_renda_por_pessoa",
    ),
    [
        pytest.param(
            Decimal("400.00"),
            2,
            True,
            True,
            [],
            Decimal("200.00"),
            id="renda-abaixo-do-limite",
        ),
        pytest.param(
            Decimal("436.00"),
            2,
            True,
            True,
            [],
            Decimal("218.00"),
            id="renda-exatamente-no-limite",
        ),
        pytest.param(
            Decimal("436.02"),
            2,
            True,
            False,
            ["Família não atende regra de renda"],
            Decimal("218.01"),
            id="renda-acima-do-limite",
        ),
        pytest.param(
            Decimal("400.00"),
            2,
            False,
            False,
            ["Família não inscrita no Cadúnico"],
            Decimal("200.00"),
            id="sem-cadunico",
        ),
        pytest.param(
            Decimal("600.00"),
            2,
            False,
            False,
            [
                "Família não inscrita no Cadúnico",
                "Família não atende regra de renda",
            ],
            Decimal("300.00"),
            id="sem-cadunico-e-renda-acima",
        ),
        pytest.param(
            Decimal("0.00"),
            1,
            True,
            True,
            [],
            Decimal("0.00"),
            id="renda-zero",
        ),
        pytest.param(
            Decimal("600.00"),
            3,
            True,
            True,
            [],
            Decimal("200.00"),
            id="mesma-renda-com-mais-pessoas",
        ),
        pytest.param(
            Decimal("654.01"),
            3,
            True,
            False,
            [
                "Família não atende regra de renda",
            ],
            Decimal("654.01") / Decimal("3"),
            id="renda-ligeiramente-maior",
        ),
    ],
)
def test_bolsa_familia_cenarios(
    renda_familiar,
    quantidade_pessoas,
    cadunico,
    esperado_atende,
    esperado_motivos,
    esperada_renda_por_pessoa,
):
    limite = Decimal("218.00")

    familia = FamiliaEntrada(
        inscrita_no_cadunico=cadunico,
        renda_familiar_mensal=renda_familiar,
        quantidade_pessoas=quantidade_pessoas,
        idade=20,
        pcd=False,
        renda_individual_mensal=Decimal("0.00"),
    )

    resultado = avaliar_bolsa_familia(
        familia=familia,
        limite=limite,
    )

    assert resultado.beneficio == "Bolsa Família"
    assert resultado.codigo == "bolsa_familia"
    assert resultado.atende is esperado_atende
    assert resultado.motivos == esperado_motivos
    assert resultado.renda_por_pessoa == esperada_renda_por_pessoa
    assert resultado.limite_renda == limite
    assert resultado.idade_minima is None
