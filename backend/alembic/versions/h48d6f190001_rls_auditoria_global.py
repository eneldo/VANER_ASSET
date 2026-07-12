"""Permite registrar auditoría previa a la autenticación bajo RLS

Revision ID: h48d6f190001
Revises: g37c5e080001
"""

from alembic import op


revision = "h48d6f190001"
down_revision = "g37c5e080001"
branch_labels = None
depends_on = None


TABLAS = ("auditoria_eventos", "auditoria_pro_eventos", "seguridad_eventos")


def upgrade() -> None:
    for tabla in TABLAS:
        op.execute(
            f'CREATE POLICY "global_audit_insert" ON "{tabla}" '
            "FOR INSERT WITH CHECK (empresa_id IS NULL)"
        )


def downgrade() -> None:
    for tabla in TABLAS:
        op.execute(f'DROP POLICY IF EXISTS "global_audit_insert" ON "{tabla}"')
