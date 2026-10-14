from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


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
