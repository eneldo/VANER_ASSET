"""Add activo field to mantenimientos for soft-delete.

Revision ID: p91e4f720001
Revises: o85d3e860001
"""

from alembic import op
import sqlalchemy as sa

revision = "p91e4f720001"
down_revision = "o85d3e860001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "mantenimientos",
        sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.create_index(
        "ix_mantenimientos_activo",
        "mantenimientos",
        ["activo"],
    )


def downgrade() -> None:
    op.drop_index("ix_mantenimientos_activo", table_name="mantenimientos")
    op.drop_column("mantenimientos", "activo")
