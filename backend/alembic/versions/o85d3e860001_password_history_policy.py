"""Historial de contraseñas y campos de política en usuarios.

Revision ID: o85d3e860001
Revises: n74c2f750001
"""

from alembic import op
import sqlalchemy as sa

revision = "o85d3e860001"
down_revision = "n74c2f750001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabla de historial de contraseñas
    op.create_table(
        "password_history",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "usuario_id",
            sa.UUID(),
            sa.ForeignKey("usuarios.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("empresa_id", sa.UUID(), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("motivo", sa.String(60), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_password_history_usuario_id", "password_history", ["usuario_id"])
    op.create_index("ix_password_history_empresa_id", "password_history", ["empresa_id"])
    op.create_index(
        "ix_password_history_usuario_fecha",
        "password_history",
        ["usuario_id", "created_at"],
    )

    # Campos de política de contraseñas en usuarios
    op.add_column(
        "usuarios",
        sa.Column("debe_cambiar_password", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "usuarios",
        sa.Column("password_changed_at", sa.DateTime(timezone=False), nullable=True),
    )
    op.add_column(
        "usuarios",
        sa.Column("temp_password_expires_at", sa.DateTime(timezone=False), nullable=True),
    )

    op.execute(
        "UPDATE usuarios SET debe_cambiar_password = FALSE WHERE debe_cambiar_password IS NULL"
    )


def downgrade() -> None:
    op.drop_column("usuarios", "temp_password_expires_at")
    op.drop_column("usuarios", "password_changed_at")
    op.drop_column("usuarios", "debe_cambiar_password")
    op.drop_index("ix_password_history_usuario_fecha", table_name="password_history")
    op.drop_index("ix_password_history_empresa_id", table_name="password_history")
    op.drop_index("ix_password_history_usuario_id", table_name="password_history")
    op.drop_table("password_history")
