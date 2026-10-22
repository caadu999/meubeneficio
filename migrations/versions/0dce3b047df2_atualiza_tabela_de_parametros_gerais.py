"""atualiza tabela de parametros gerais

Revision ID: 0dce3b047df2
Revises: 683e25353ef8
Create Date: 2026-10-19 12:42:01.382646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0dce3b047df2'
down_revision: Union[str, Sequence[str], None] = '683e25353ef8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('parametros', sa.Column('nome', sa.String(), nullable=True))
    op.add_column('parametros', sa.Column('valor', sa.Numeric(10, 2), nullable=True))
    # O maior ID é o cadastro mais recente; os demais continuam preservados.
    op.execute(sa.text("""
        UPDATE parametros
        SET nome = CASE WHEN id = (SELECT max(id) FROM parametros)
                        THEN 'salario_minimo'
                        ELSE 'salario_minimo_legado_' || id::text END,
            valor = salario_minimo
    """))
    op.alter_column('parametros', 'nome', nullable=False)
    op.alter_column('parametros', 'valor', nullable=False)
    op.drop_constraint(op.f('uq_parametros_salario_minimo'), 'parametros', type_='unique')
    op.create_unique_constraint(op.f('uq_parametros_nome'), 'parametros', ['nome'])
    op.drop_column('parametros', 'salario_minimo')


def downgrade() -> None:
    """Restaura os salários sem descartar parâmetros de outros tipos."""
    connection = op.get_bind()
    invalidos = connection.scalar(sa.text("""
        SELECT count(*) FROM parametros
        WHERE nome <> 'salario_minimo'
          AND nome NOT LIKE 'salario_minimo_legado_%'
    """))
    if invalidos:
        raise ValueError('Downgrade exige remover ou exportar parâmetros não salariais')
    op.add_column('parametros', sa.Column('salario_minimo', sa.Numeric(), nullable=True))
    op.execute(sa.text('UPDATE parametros SET salario_minimo = valor'))
    op.alter_column('parametros', 'salario_minimo', nullable=False)
    op.drop_constraint(op.f('uq_parametros_nome'), 'parametros', type_='unique')
    op.create_unique_constraint(op.f('uq_parametros_salario_minimo'), 'parametros', ['salario_minimo'])
    op.drop_column('parametros', 'valor')
    op.drop_column('parametros', 'nome')
