from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Beneficio(Base):
    __tablename__ = "beneficios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String)
    requisitos: Requisitos


class Requisitos(Base):
    __tablename__ = "requisitos"
