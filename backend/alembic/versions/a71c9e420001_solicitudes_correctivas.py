"""solicitudes correctivas de emergencia

Revision ID: a71c9e420001
Revises: f284acc97939
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a71c9e420001"
down_revision: Union[str, Sequence[str], None] = "f284acc97939"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "solicitudes_correctivas",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sede_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("equipo_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("solicitante_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mantenimiento_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("client_request_id", sa.String(80), nullable=True, unique=True),
        sa.Column("titulo", sa.String(160), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("prioridad", sa.String(20), server_default="EMERGENCIA", nullable=False),
        sa.Column("estado", sa.String(30), server_default="NUEVA", nullable=False),
        sa.Column("contacto_nombre", sa.String(150), nullable=True),
        sa.Column("contacto_telefono", sa.String(50), nullable=True),
        sa.Column("respuesta_coordinador", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("atendida_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["equipo_id"], ["equipos.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["solicitante_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["mantenimiento_id"], ["mantenimientos.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("prioridad IN ('ALTA', 'CRITICA', 'EMERGENCIA')", name="ck_solicitud_prioridad"),
        sa.CheckConstraint("estado IN ('NUEVA', 'EN_REVISION', 'APROBADA', 'CONVERTIDA_OT', 'RECHAZADA', 'CERRADA')", name="ck_solicitud_estado"),
    )
    op.create_index("ix_solicitudes_tenant_estado", "solicitudes_correctivas", ["empresa_id", "estado"])
    op.create_index("ix_solicitudes_tenant_fecha", "solicitudes_correctivas", ["empresa_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_solicitudes_tenant_fecha", table_name="solicitudes_correctivas")
    op.drop_index("ix_solicitudes_tenant_estado", table_name="solicitudes_correctivas")
    op.drop_table("solicitudes_correctivas")
