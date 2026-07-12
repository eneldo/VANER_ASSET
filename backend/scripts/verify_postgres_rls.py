"""Prueba RLS real con dos tenants y un rol PostgreSQL sin BYPASSRLS."""

from __future__ import annotations

import os
import uuid

from sqlalchemy import create_engine, text


OWNER_URL = os.environ.get("RLS_OWNER_DATABASE_URL")
APP_URL = os.environ.get("RLS_APP_DATABASE_URL")

if not OWNER_URL or not APP_URL:
    raise SystemExit(
        "Defina RLS_OWNER_DATABASE_URL y RLS_APP_DATABASE_URL para ejecutar esta prueba."
    )

owner = create_engine(OWNER_URL)
app = create_engine(APP_URL)
tenant_a, tenant_b = uuid.uuid4(), uuid.uuid4()


def contexto(connection, tenant="", admin=False):
    connection.execute(
        text(
            "SELECT set_config('app.current_tenant', :tenant, false), "
            "set_config('app.is_platform_admin', :admin, false)"
        ),
        {"tenant": str(tenant), "admin": "true" if admin else "false"},
    )


try:
    with owner.begin() as connection:
        connection.execute(
            text("INSERT INTO empresas (id, nombre, nit) VALUES (:a, 'RLS A', :na), (:b, 'RLS B', :nb)"),
            {"a": tenant_a, "b": tenant_b, "na": f"RLS-{tenant_a}", "nb": f"RLS-{tenant_b}"},
        )
        connection.execute(
            text("INSERT INTO sedes (id, empresa_id, nombre) VALUES (:id, :tenant, 'Sede B')"),
            {"id": uuid.uuid4(), "tenant": tenant_b},
        )

    with app.connect() as connection:
        contexto(connection, tenant_a)
        visibles = connection.execute(
            text("SELECT id FROM empresas WHERE id IN (:a, :b) ORDER BY id"),
            {"a": tenant_a, "b": tenant_b},
        ).scalars().all()
        assert visibles == [tenant_a], f"Fuga entre tenants: {visibles}"

        sedes_otro_tenant = connection.execute(
            text("SELECT count(*) FROM sedes WHERE empresa_id = :tenant"),
            {"tenant": tenant_b},
        ).scalar_one()
        assert sedes_otro_tenant == 0, "El tenant A pudo leer sedes del tenant B"
        connection.rollback()

        contexto(connection, admin=True)
        total_admin = connection.execute(
            text("SELECT count(*) FROM empresas WHERE id IN (:a, :b)"),
            {"a": tenant_a, "b": tenant_b},
        ).scalar_one()
        assert total_admin == 2, "El contexto ADMIN no obtuvo alcance global"
        connection.rollback()

    print("RLS PostgreSQL verificado: tenant aislado y ADMIN con alcance global.")
finally:
    with owner.begin() as connection:
        connection.execute(
            text("DELETE FROM sedes WHERE empresa_id IN (:a, :b)"),
            {"a": tenant_a, "b": tenant_b},
        )
        connection.execute(
            text("DELETE FROM empresas WHERE id IN (:a, :b)"),
            {"a": tenant_a, "b": tenant_b},
        )
    owner.dispose()
    app.dispose()
