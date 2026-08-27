"""Agregar campos MFA a usuarios

Revision ID: t01a2b3c40001
Revises: s01a2b3c40001
"""

from alembic import op
import sqlalchemy as sa

revision = "t01a2b3c40001"
down_revision = "s01a2b3c40001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("mfa_enabled", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("usuarios", sa.Column("mfa_secret", sa.String(255), nullable=True))
    op.add_column("usuarios", sa.Column("mfa_backup_codes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("usuarios", "mfa_backup_codes")
    op.drop_column("usuarios", "mfa_secret")
    op.drop_column("usuarios", "mfa_enabled")
