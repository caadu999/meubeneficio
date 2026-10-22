from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text

VERSOES = Path(__file__).resolve().parents[1] / "migrations" / "versions"


def carregar_migracao(revisao):
    caminho = next(VERSOES.glob(f"{revisao}_*.py"))
    spec = spec_from_file_location(revisao, caminho)
    modulo = module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_migracoes_preservam_banco_preenchido(engine_teste):
    with engine_teste.connect() as connection:
        transaction = connection.begin()
        try:
            # Schema isolado: o rollback remove toda a estrutura deste teste.
            connection.execute(text("CREATE SCHEMA teste_migracoes"))
            connection.execute(
                text("SET LOCAL search_path TO teste_migracoes")
            )
            context = MigrationContext.configure(connection)
            with Operations.context(context):
                carregar_migracao("09b792488e7f").upgrade()
                carregar_migracao("949a2e6b6aa6").upgrade()
                connection.execute(
                    text("""
                    INSERT INTO beneficios (nome) VALUES
                    ('Bolsa Família'), ('BPC'), ('Outro'), ('BPC'),
                    ('ID Jovem'), ('Gás do Povo'), ('Carteira da Pessoa Idosa')
                """)
                )
                carregar_migracao("b74d063e84c8").upgrade()
                codigos = (
                    connection.execute(
                        text("SELECT codigo FROM beneficios ORDER BY id")
                    )
                    .scalars()
                    .all()
                )
                assert codigos == [
                    "bolsa_familia",
                    "bpc",
                    "legado_3",
                    "legado_4",
                    "id_jovem",
                    "gas_do_povo",
                    "carteira_da_pessoa_idosa",
                ]
                carregar_migracao("a818a19eb10c").upgrade()
                carregar_migracao("1fc38d0b6d6b").upgrade()
                carregar_migracao("683e25353ef8").upgrade()
                connection.execute(
                    text("""
                    INSERT INTO parametros (salario_minimo)
                    VALUES (1500.00), (1600.00)
                """)
                )
                migracao = carregar_migracao("0dce3b047df2")
                migracao.upgrade()
                rows = connection.execute(
                    text("SELECT nome, valor FROM parametros ORDER BY id")
                ).all()
                assert rows == [
                    ("salario_minimo_legado_1", 1500),
                    ("salario_minimo", 1600),
                ]
                migracao.downgrade()
                assert connection.execute(
                    text("SELECT salario_minimo FROM parametros ORDER BY id")
                ).scalars().all() == [1500, 1600]
        finally:
            transaction.rollback()
