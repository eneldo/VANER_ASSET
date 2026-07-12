"""repuestos e incidencias estructurados por OT

Revision ID: e15a3c860001
Revises: d04f2b750001
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "e15a3c860001"
down_revision: Union[str, Sequence[str], None] = "d04f2b750001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ot_repuestos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mantenimiento_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("descripcion", sa.String(250), nullable=False),
        sa.Column("referencia", sa.String(120), nullable=True),
        sa.Column("cantidad", sa.Numeric(12, 3), nullable=False),
        sa.Column("unidad", sa.String(30), server_default="UNIDAD", nullable=False),
        sa.Column("costo_unitario", sa.Numeric(14, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mantenimiento_id"], ["mantenimientos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("cantidad > 0 AND (costo_unitario IS NULL OR costo_unitario >= 0)", name="ck_ot_repuesto_valores"),
    )
    op.create_index("ix_ot_repuestos_tenant_ot", "ot_repuestos", ["empresa_id", "mantenimiento_id"])
    op.create_table(
        "ot_incidencias",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mantenimiento_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tipo", sa.String(40), server_default="TECNICA", nullable=False),
        sa.Column("severidad", sa.String(20), server_default="MEDIA", nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("resuelta", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mantenimiento_id"], ["mantenimientos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("severidad IN ('BAJA', 'MEDIA', 'ALTA', 'CRITICA')", name="ck_ot_incidencia_severidad"),
    )
    op.create_index("ix_ot_incidencias_tenant_ot", "ot_incidencias", ["empresa_id", "mantenimiento_id"])


def downgrade() -> None:
    op.drop_index("ix_ot_incidencias_tenant_ot", table_name="ot_incidencias")
    op.drop_table("ot_incidencias")
    op.drop_index("ix_ot_repuestos_tenant_ot", table_name="ot_repuestos")
    op.drop_table("ot_repuestos")
