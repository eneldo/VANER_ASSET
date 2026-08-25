from alembic import op


revision = "k61f9c420001"
down_revision = "j60f8b310001"
branch_labels = None
depends_on = None


INDEXES = (
    ("ix_equipos_empresa_id", "equipos", "empresa_id"),
    ("ix_equipos_sede_id", "equipos", "sede_id"),
    ("ix_equipos_categoria_id", "equipos", "categoria_id"),
    ("ix_equipos_created_at", "equipos", "created_at"),
    ("ix_equipos_empresa_estado", "equipos", "empresa_id, estado"),
    ("ix_equipos_empresa_created_at", "equipos", "empresa_id, created_at DESC"),
    ("ix_sedes_empresa_id", "sedes", "empresa_id"),
    ("ix_evidencias_mantenimiento_id", "evidencias", "mantenimiento_id"),
    ("ix_evidencias_equipo_id", "evidencias", "equipo_id"),
    ("ix_evidencias_created_at", "evidencias", "created_at"),
    ("ix_evidencias_equipo_created_at", "evidencias", "equipo_id, created_at DESC"),
    ("ix_usuarios_empresa_id", "usuarios", "empresa_id"),
    ("ix_usuarios_rol", "usuarios", "rol"),
)


def upgrade() -> None:
    for name, table, columns in INDEXES:
        op.execute(f'CREATE INDEX IF NOT EXISTS "{name}" ON "{table}" ({columns})')


def downgrade() -> None:
    for name, _table, _columns in reversed(INDEXES):
        op.execute(f'DROP INDEX IF EXISTS "{name}"')
