"""Campos de responsable, vida útil e historial de equipos.

Revision ID: m63b1e640001
Revises: l62a0d530001
"""

from alembic import op
import sqlalchemy as sa


revision = "m63b1e640001"
down_revision = "l62a0d530001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("equipos", sa.Column("responsable_id", sa.UUID(), nullable=True))
    op.add_column("equipos", sa.Column("vida_util_meses", sa.Integer(), nullable=True))
    op.add_column("equipos", sa.Column("historial_cambios", sa.JSON(), nullable=True))
    op.create_foreign_key(
        "fk_equipos_responsable_id_usuarios",
        "equipos",
        "usuarios",
        ["responsable_id"],
        ["id"],
    )
    op.create_index("ix_equipos_responsable_id", "equipos", ["responsable_id"])
    op.create_check_constraint(
        "ck_equipos_vida_util_meses_positiva",
        "equipos",
        "vida_util_meses IS NULL OR vida_util_meses > 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_equipos_vida_util_meses_positiva", "equipos", type_="check")
    op.drop_index("ix_equipos_responsable_id", table_name="equipos")
    op.drop_constraint("fk_equipos_responsable_id_usuarios", "equipos", type_="foreignkey")
    op.drop_column("equipos", "historial_cambios")
    op.drop_column("equipos", "vida_util_meses")
    op.drop_column("equipos", "responsable_id")
