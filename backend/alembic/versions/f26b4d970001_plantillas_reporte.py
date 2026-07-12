"""plantillas configurables de reporte

Revision ID: f26b4d970001
Revises: e15a3c860001
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "f26b4d970001"
down_revision: Union[str, Sequence[str], None] = "e15a3c860001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plantillas_reporte",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("creado_por_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("tipo", sa.String(20), server_default="AMBOS", nullable=False),
        sa.Column("titulo", sa.String(220), nullable=False),
        sa.Column("color_primario", sa.String(7), server_default="#1E3A8A", nullable=False),
        sa.Column("pie_pagina", sa.Text(), nullable=True),
        sa.Column("incluir_logo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("incluir_evidencias", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("incluir_firmas", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("incluir_costos", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("tipo IN ('OT', 'MENSUAL', 'AMBOS')", name="ck_plantilla_reporte_tipo"),
        sa.CheckConstraint("color_primario ~ '^#[0-9A-Fa-f]{6}$'", name="ck_plantilla_color"),
    )
    op.create_index("ix_plantillas_reporte_scope", "plantillas_reporte", ["empresa_id", "tipo", "activo"])


def downgrade() -> None:
    op.drop_index("ix_plantillas_reporte_scope", table_name="plantillas_reporte")
    op.drop_table("plantillas_reporte")
