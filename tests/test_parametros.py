from http import HTTPStatus

import pytest
from pydantic import ValidationError

from direitos.schemas.beneficio import AtualizarParametro


def test_atualizar_parametro_rejeita_nome_vazio():
    with pytest.raises(ValidationError):
        AtualizarParametro(nome="")


def test_atualizar_parametro_omite_nome_ausente():
    parametro = AtualizarParametro(valor="100.00")
    assert parametro.nome is None
    assert parametro.model_dump(exclude_unset=True) == {
        "valor": parametro.valor
    }


def test_listar_parametros_vazios(client):
    response = client.get("/gerais/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []
