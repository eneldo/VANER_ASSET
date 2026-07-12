"""RLS multi-tenant para datos operativos

Revision ID: g37c5e080001
Revises: f26b4d970001
"""

from alembic import op


revision = "g37c5e080001"
down_revision = "f26b4d970001"
branch_labels = None
depends_on = None


ADMIN = "current_setting('app.is_platform_admin', true) = 'true'"
TENANT = "NULLIF(current_setting('app.current_tenant', true), '')::uuid"


DIRECTAS = {
    "sedes": "empresa_id",
    "equipos": "empresa_id",
    "mantenimientos": "empresa_id",
    "solicitudes_correctivas": "empresa_id",
    "reportes_publicados": "empresa_id",
    "facturas": "empresa_id",
    "ot_repuestos": "empresa_id",
    "ot_incidencias": "empresa_id",
    "auditoria_eventos": "empresa_id",
    "auditoria_pro_eventos": "empresa_id",
    "seguridad_eventos": "empresa_id",
}

INDIRECTAS = {
    "tecnicos": "EXISTS (SELECT 1 FROM usuarios u WHERE u.id = tecnicos.usuario_id AND u.empresa_id = {tenant})",
    "equipo_hoja_vida": "EXISTS (SELECT 1 FROM equipos e WHERE e.id = equipo_hoja_vida.equipo_id AND e.empresa_id = {tenant})",
    "evidencias": "EXISTS (SELECT 1 FROM mantenimientos m WHERE m.id = evidencias.mantenimiento_id AND m.empresa_id = {tenant})",
    "formatos_mantenimiento": "EXISTS (SELECT 1 FROM mantenimientos m WHERE m.id = formatos_mantenimiento.mantenimiento_id AND m.empresa_id = {tenant})",
    "hist_mantenimiento": "EXISTS (SELECT 1 FROM mantenimientos m WHERE m.id = hist_mantenimiento.mantenimiento_id AND m.empresa_id = {tenant})",
    "historial_mantenimiento": "EXISTS (SELECT 1 FROM mantenimientos m WHERE m.id = historial_mantenimiento.mantenimiento_id AND m.empresa_id = {tenant})",
    "bitacoras_dinamicas": "EXISTS (SELECT 1 FROM mantenimientos m WHERE m.id = bitacoras_dinamicas.mantenimiento_id AND m.empresa_id = {tenant})",
    "bitacoras_respuestas": "EXISTS (SELECT 1 FROM bitacoras_dinamicas b JOIN mantenimientos m ON m.id = b.mantenimiento_id WHERE b.id = bitacoras_respuestas.bitacora_id AND m.empresa_id = {tenant})",
}


def _crear_politica(tabla: str, alcance: str) -> None:
    expresion = f"({ADMIN}) OR ({alcance})"
    op.execute(f'ALTER TABLE "{tabla}" ENABLE ROW LEVEL SECURITY')
    op.execute(f'ALTER TABLE "{tabla}" FORCE ROW LEVEL SECURITY')
    op.execute(
        f'CREATE POLICY "tenant_isolation" ON "{tabla}" '
        f'FOR ALL USING ({expresion}) WITH CHECK ({expresion})'
    )


def upgrade() -> None:
    _crear_politica("empresas", f"id = {TENANT}")

    for tabla, columna in DIRECTAS.items():
        _crear_politica(tabla, f"{columna} = {TENANT}")

    # Las plantillas globales son legibles por cualquier tenant; solo las rutas
    # ADMIN permiten modificarlas, manteniendo la escritura controlada por RBAC.
    _crear_politica("plantillas_reporte", f"empresa_id IS NULL OR empresa_id = {TENANT}")

    for tabla, expresion in INDIRECTAS.items():
        _crear_politica(tabla, expresion.format(tenant=TENANT))


def downgrade() -> None:
    tablas = [
        "empresas",
        *DIRECTAS.keys(),
        "plantillas_reporte",
        *INDIRECTAS.keys(),
    ]
    for tabla in reversed(tablas):
        op.execute(f'DROP POLICY IF EXISTS "tenant_isolation" ON "{tabla}"')
        op.execute(f'ALTER TABLE "{tabla}" NO FORCE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE "{tabla}" DISABLE ROW LEVEL SECURITY')
