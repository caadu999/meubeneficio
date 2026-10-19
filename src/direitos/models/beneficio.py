from decimal import Decimal

from sqlalchemy import ForeignKey, MetaData, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

convention = {
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


class Beneficio(Base):
    __tablename__ = "beneficios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String)
    requisito = relationship(
        "Requisitos",
        back_populates="beneficio",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    limite_renda_por_pessoa: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )
    codigo: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class Requisitos(Base):
    __tablename__ = "requisitos"
    id: Mapped[int] = mapped_column(primary_key=True)
    descricao: Mapped[str] = mapped_column(String)
    beneficio_id: Mapped[int] = mapped_column(
        ForeignKey(
            "beneficios.id", name="fk_requisitos_beneficio", ondelete="CASCADE"
        )
    )
    beneficio = relationship("Beneficio", back_populates="requisito")
