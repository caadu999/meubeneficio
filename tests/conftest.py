from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.community.postgres import PostgresContainer

from direitos.app import app
from direitos.database.database import get_session
from direitos.models.beneficio import Base, Beneficio, ParametrosGerais


@pytest.fixture(scope="session")
def engine_teste():
    """Cria outro PostgreSQL, separado do banco da aplicação."""
    with PostgresContainer("postgres:18", driver="psycopg") as postgres:
        engine = create_engine(postgres.get_connection_url())

        try:
            Base.metadata.create_all(engine)
            yield engine
        finally:
            engine.dispose()


@pytest.fixture
def session_teste(engine_teste):
    with engine_teste.connect() as connection:
        transacao = connection.begin()

        session = Session(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )

        try:
            yield session
        finally:
            session.close()
            transacao.rollback()


@pytest.fixture
def client(session_teste):
    def substituir_get_session():
        yield session_teste

    anteriores = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = substituir_get_session

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anteriores)


@pytest.fixture
def dados_avaliacao(session_teste):
    parametro = ParametrosGerais(
        nome="salario_minimo",
        valor=Decimal("1600.00"),
    )

    beneficios = [
        Beneficio(
            nome="Bolsa Família",
            codigo="bolsa_familia",
            limite_renda_por_pessoa=Decimal("220.00"),
        ),
        Beneficio(
            nome="Gás do Povo",
            codigo="gas_do_povo",
        ),
        Beneficio(
            nome="BPC",
            codigo="bpc",
            idade_minima=65,
        ),
        Beneficio(
            nome="ID Jovem",
            codigo="id_jovem",
            idade_minima=15,
        ),
        Beneficio(
            nome="Carteira da Pessoa Idosa",
            codigo="carteira_da_pessoa_idosa",
            idade_minima=60,
        ),
    ]

    session_teste.add_all([parametro, *beneficios])
    session_teste.flush()

    return {
        "parametro": parametro,
        "beneficios": {
            beneficio.codigo: beneficio for beneficio in beneficios
        },
    }


@pytest.fixture
def entrada_familia():
    return {
        "inscrita_no_cadunico": True,
        "renda_familiar_mensal": "400.00",
        "quantidade_pessoas": 2,
        "idade": 20,
        "pcd": False,
        "renda_individual_mensal": "100.00",
    }
