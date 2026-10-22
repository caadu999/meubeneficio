from decimal import Decimal
from http import HTTPStatus

import pytest


def test_avaliar_retorna_beneficios(client, dados_avaliacao, entrada_familia):
    response = client.post("/avaliar/", json=entrada_familia)

    assert response.status_code == HTTPStatus.OK

    resultados = {
        item["codigo"]: item for item in response.json()["beneficios"]
    }

    assert len(response.json()["beneficios"]) == 5
    assert set(resultados) == {
        "bolsa_familia",
        "gas_do_povo",
        "bpc",
        "id_jovem",
        "carteira_da_pessoa_idosa",
    }

    assert resultados["bolsa_familia"]["atende"] is True
    assert resultados["gas_do_povo"]["atende"] is True
    assert resultados["bpc"]["atende"] is False
    assert resultados["id_jovem"]["atende"] is True
    assert resultados["carteira_da_pessoa_idosa"]["atende"] is False

    assert Decimal(resultados["bolsa_familia"]["renda_por_pessoa"]) == Decimal(
        "200.00"
    )

    assert Decimal(resultados["bolsa_familia"]["limite_renda"]) == Decimal(
        "220.00"
    )

    assert Decimal(resultados["gas_do_povo"]["limite_renda"]) == Decimal(
        "800.00"
    )

    assert Decimal(resultados["bpc"]["limite_renda"]) == Decimal("400.00")


def test_avaliar_utiliza_limite_do_banco(
    client, session_teste, dados_avaliacao, entrada_familia
):
    bolsa = dados_avaliacao["beneficios"]["bolsa_familia"]
    bolsa.limite_renda_por_pessoa = Decimal("150.00")
    session_teste.flush()

    response = client.post("/avaliar/", json=entrada_familia)

    assert response.status_code == HTTPStatus.OK

    bolsa_resultado = next(
        item
        for item in response.json()["beneficios"]
        if item["codigo"] == "bolsa_familia"
    )

    assert bolsa_resultado["atende"] is False
    assert bolsa_resultado["motivos"]
    assert Decimal(bolsa_resultado["limite_renda"]) == Decimal("150.00")


def test_avaliar_sem_salario_minimo(
    client, session_teste, dados_avaliacao, entrada_familia
):
    session_teste.delete(dados_avaliacao["parametro"])
    session_teste.flush()

    response = client.post("/avaliar/", json=entrada_familia)

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert isinstance(response.json()["detail"], str)


@pytest.mark.parametrize(
    ("codigo", "campo", "mensagem"),
    [
        (
            "bolsa_familia",
            "limite_renda_por_pessoa",
            "Limite não cadastrado",
        ),
        (
            "bpc",
            "idade_minima",
            "Idade mínima não cadastrada",
        ),
        (
            "carteira_da_pessoa_idosa",
            "idade_minima",
            "Idade mínima não cadastrada",
        ),
    ],
)
def test_avaliar_com_configuracao_incompleta(
    client,
    session_teste,
    dados_avaliacao,
    entrada_familia,
    codigo,
    campo,
    mensagem,
):
    beneficio = dados_avaliacao["beneficios"][codigo]
    setattr(beneficio, campo, None)
    session_teste.flush()

    response = client.post("/avaliar/", json=entrada_familia)

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == mensagem


def test_avaliar_rejeita_quantidade_zero(
    client, dados_avaliacao, entrada_familia
):
    entrada_familia["quantidade_pessoas"] = 0

    response = client.post("/avaliar/", json=entrada_familia)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert any(
        erro["loc"] == ["body", "quantidade_pessoas"]
        for erro in response.json()["detail"]
    )
