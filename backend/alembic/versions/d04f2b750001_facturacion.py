"""facturación administrativa

Revision ID: d04f2b750001
Revises: c93e1a640001
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "d04f2b750001"
down_revision: Union[str, Sequence[str], None] = "c93e1a640001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "facturas",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creado_por_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("numero", sa.String(50), nullable=False, unique=True),
        sa.Column("concepto", sa.String(220), nullable=False),
        sa.Column("detalle", postgresql.JSONB(), nullable=False),
        sa.Column("moneda", sa.String(3), server_default="COP", nullable=False),
        sa.Column("subtotal", sa.Numeric(14, 2), nullable=False),
        sa.Column("impuesto_porcentaje", sa.Numeric(5, 2), server_default="0", nullable=False),
        sa.Column("impuesto", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("total", sa.Numeric(14, 2), nullable=False),
        sa.Column("estado", sa.String(20), server_default="BORRADOR", nullable=False),
        sa.Column("periodo_inicio", sa.Date(), nullable=False),
        sa.Column("periodo_fin", sa.Date(), nullable=False),
        sa.Column("fecha_emision", sa.Date(), nullable=False),
        sa.Column("fecha_vencimiento", sa.Date(), nullable=False),
        sa.Column("fecha_pago", sa.Date(), nullable=True),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("estado IN ('BORRADOR', 'EMITIDA', 'PAGADA', 'ANULADA')", name="ck_factura_estado"),
        sa.CheckConstraint("subtotal >= 0 AND impuesto >= 0 AND total >= 0", name="ck_factura_valores"),
        sa.CheckConstraint("periodo_fin >= periodo_inicio AND fecha_vencimiento >= fecha_emision", name="ck_factura_fechas"),
    )
    op.create_index("ix_facturas_empresa_estado", "facturas", ["empresa_id", "estado"])
    op.create_index("ix_facturas_vencimiento", "facturas", ["fecha_vencimiento"])


def downgrade() -> None:
    op.drop_index("ix_facturas_vencimiento", table_name="facturas")
    op.drop_index("ix_facturas_empresa_estado", table_name="facturas")
    op.drop_table("facturas")
