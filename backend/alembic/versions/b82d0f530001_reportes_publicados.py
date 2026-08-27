"""reportes publicados con aprobación

Revision ID: b82d0f530001
Revises: a71c9e420001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b82d0f530001"
down_revision: str | Sequence[str] | None = "a71c9e420001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reportes_publicados",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mantenimiento_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("creado_por_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("aprobado_por_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("titulo", sa.String(220), nullable=False),
        sa.Column("estado", sa.String(30), server_default="BORRADOR", nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("periodo_inicio", sa.Date(), nullable=True),
        sa.Column("periodo_fin", sa.Date(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("aprobado_at", sa.DateTime(), nullable=True),
        sa.Column("publicado_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["mantenimiento_id"], ["mantenimientos.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["creado_por_id"], ["usuarios.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["aprobado_por_id"], ["usuarios.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("tipo IN ('OT', 'MENSUAL')", name="ck_reporte_tipo"),
        sa.CheckConstraint(
            "estado IN ('BORRADOR', 'APROBADO', 'PUBLICADO')", name="ck_reporte_estado"
        ),
    )
    op.create_index(
        "ix_reportes_tenant_estado", "reportes_publicados", ["empresa_id", "estado"]
    )
    op.create_index(
        "ix_reportes_tenant_periodo",
        "reportes_publicados",
        ["empresa_id", "periodo_inicio", "periodo_fin"],
    )


def downgrade() -> None:
    op.drop_index("ix_reportes_tenant_periodo", table_name="reportes_publicados")
    op.drop_index("ix_reportes_tenant_estado", table_name="reportes_publicados")
    op.drop_table("reportes_publicados")
