"""RLS completo — cobertura total de tablas tenant-scoped

Revision ID: s01a2b3c40001
Revises: r01a1b2c30001
"""

from alembic import op

revision = "s01a2b3c40001"
down_revision = "r01a1b2c30001"
branch_labels = None
depends_on = None

ADMIN = "current_setting('app.is_platform_admin', true) = 'true'"
TENANT = "NULLIF(current_setting('app.current_tenant', true), '')::uuid"

# Tablas con empresa_id directo (política estándar)
DIRECTAS = {
    "notificaciones": "empresa_id",
    "password_history": "empresa_id",
    "categorias_repuestos": "empresa_id",
    "repuestos": "empresa_id",
    "bodegas": "empresa_id",
    "existencias_repuestos": "empresa_id",
    "movimientos_repuestos": "empresa_id",
    "solicitudes_repuestos": "empresa_id",
    "proveedores_repuestos": "empresa_id",
}

# Tablas sin empresa_id que dependen de repuestos (FK directa)
INDIRECTAS_REPUESTOS = {
    "repuesto_proveedor": (
        "EXISTS (SELECT 1 FROM repuestos r WHERE r.id = repuesto_proveedor.repuesto_id "
        "AND r.empresa_id = {tenant})"
    ),
    "repuestos_compatibilidad": (
        "EXISTS (SELECT 1 FROM repuestos r WHERE r.id = repuestos_compatibilidad.repuesto_id "
        "AND r.empresa_id = {tenant})"
    ),
}


def _crear_politica(tabla: str, alcance: str) -> None:
    expresion = f"({ADMIN}) OR ({alcance})"
    op.execute(f'ALTER TABLE "{tabla}" ENABLE ROW LEVEL SECURITY')
    op.execute(f'ALTER TABLE "{tabla}" FORCE ROW LEVEL SECURITY')
    op.execute(
        f'CREATE POLICY "tenant_isolation" ON "{tabla}" '
        f"FOR ALL USING ({expresion}) WITH CHECK ({expresion})"
    )


def upgrade() -> None:
    for tabla, columna in DIRECTAS.items():
        _crear_politica(tabla, f"{columna} = {TENANT}")

    for tabla, expresion in INDIRECTAS_REPUESTOS.items():
        _crear_politica(tabla, expresion.format(tenant=TENANT))


def downgrade() -> None:
    tablas = [*DIRECTAS.keys(), *INDIRECTAS_REPUESTOS.keys()]
    for tabla in reversed(tablas):
        op.execute(f'DROP POLICY IF EXISTS "tenant_isolation" ON "{tabla}"')
        op.execute(f'ALTER TABLE "{tabla}" NO FORCE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE "{tabla}" DISABLE ROW LEVEL SECURITY')
