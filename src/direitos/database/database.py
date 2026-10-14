from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from direitos.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


@event.listens_for(engine, "connect")
def ativar_chaves_estrangeiras(conexao, registro):
    autocommit_anterior = conexao.autocommit
    conexao.autocommit = True

    try:
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    finally:
        conexao.autocommit = autocommit_anterior


def get_session():
    with Session(engine) as session:
        yield session
