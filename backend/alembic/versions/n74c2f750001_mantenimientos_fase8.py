"""Campos de diagnóstico, costos, cierre y trazabilidad de mantenimientos.

Revision ID: n74c2f750001
Revises: m63b1e640001
"""

from alembic import op
import sqlalchemy as sa


revision = "n74c2f750001"
down_revision = "m63b1e640001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Prioridad
    op.add_column("mantenimientos", sa.Column("prioridad", sa.String(20), nullable=True))

    # Diagnóstico y trabajo
    op.add_column("mantenimientos", sa.Column("falla_incidencia", sa.Text(), nullable=True))
    op.add_column("mantenimientos", sa.Column("diagnostico", sa.Text(), nullable=True))
    op.add_column("mantenimientos", sa.Column("trabajo_realizado", sa.Text(), nullable=True))

    # Repuestos (JSON array)
    op.add_column("mantenimientos", sa.Column("repuestos", sa.JSON(), nullable=True))

    # Costos detallados
    op.add_column("mantenimientos", sa.Column("costo_mano_obra", sa.Numeric(12, 2), nullable=True))
    op.add_column("mantenimientos", sa.Column("costo_repuestos", sa.Numeric(12, 2), nullable=True))
    op.add_column("mantenimientos", sa.Column("costo_total", sa.Numeric(12, 2), nullable=True))

    # Evidencias (JSON arrays)
    op.add_column("mantenimientos", sa.Column("evidencia_fotos", sa.JSON(), nullable=True))
    op.add_column("mantenimientos", sa.Column("evidencia_documentos", sa.JSON(), nullable=True))

    # Cierre
    op.add_column("mantenimientos", sa.Column("solucion", sa.Text(), nullable=True))
    op.add_column("mantenimientos", sa.Column("cerrado", sa.Boolean(), nullable=True))
    op.add_column("mantenimientos", sa.Column("fecha_cierre", sa.DateTime(), nullable=True))

    # Responsable
    op.add_column("mantenimientos", sa.Column("responsable_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_mantenimientos_responsable_id_usuarios",
        "mantenimientos",
        "usuarios",
        ["responsable_id"],
        ["id"],
    )
    op.create_index("ix_mantenimientos_responsable_id", "mantenimientos", ["responsable_id"])

    # Trazabilidad de movimiento
    op.add_column("mantenimientos", sa.Column("tipo_movimiento", sa.String(50), nullable=True))
    op.add_column("mantenimientos", sa.Column("activo_afectado_id", sa.UUID(), nullable=True))
    op.add_column("mantenimientos", sa.Column("activo_afectado_tipo", sa.String(50), nullable=True))

    # Valor por defecto para cerrado
    op.execute("UPDATE mantenimientos SET cerrado = FALSE WHERE cerrado IS NULL")


def downgrade() -> None:
    op.drop_index("ix_mantenimientos_responsable_id", table_name="mantenimientos")
    op.drop_constraint("fk_mantenimientos_responsable_id_usuarios", "mantenimientos", type_="foreignkey")
    op.drop_column("mantenimientos", "responsable_id")
    op.drop_column("mantenimientos", "activo_afectado_tipo")
    op.drop_column("mantenimientos", "activo_afectado_id")
    op.drop_column("mantenimientos", "tipo_movimiento")
    op.drop_column("mantenimientos", "fecha_cierre")
    op.drop_column("mantenimientos", "cerrado")
    op.drop_column("mantenimientos", "solucion")
    op.drop_column("mantenimientos", "evidencia_documentos")
    op.drop_column("mantenimientos", "evidencia_fotos")
    op.drop_column("mantenimientos", "costo_total")
    op.drop_column("mantenimientos", "costo_repuestos")
    op.drop_column("mantenimientos", "costo_mano_obra")
    op.drop_column("mantenimientos", "repuestos")
    op.drop_column("mantenimientos", "trabajo_realizado")
    op.drop_column("mantenimientos", "diagnostico")
    op.drop_column("mantenimientos", "falla_incidencia")
    op.drop_column("mantenimientos", "prioridad")
