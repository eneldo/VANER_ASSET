from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "j60f8b310001"
down_revision = "i59e7a2a0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuario_empresas",
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("usuario_id", "empresa_id"),
    )
    op.create_index("ix_usuario_empresas_empresa_id", "usuario_empresas", ["empresa_id"])
    op.execute(
        "DO $$ "
        "BEGIN "
        "IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sga_app') THEN "
        "EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.usuario_empresas TO sga_app'; "
        "END IF; "
        "END $$"
    )
    op.execute(
        "INSERT INTO usuario_empresas (usuario_id, empresa_id) "
        "SELECT id, empresa_id FROM usuarios "
        "WHERE rol = 'COORDINADOR' AND empresa_id IS NOT NULL "
        "ON CONFLICT DO NOTHING"
    )


def downgrade() -> None:
    op.drop_index("ix_usuario_empresas_empresa_id", table_name="usuario_empresas")
    op.drop_table("usuario_empresas")
