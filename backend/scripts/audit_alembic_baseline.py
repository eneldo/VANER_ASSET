"""Audita de forma read-only si una base existente puede recibir un Alembic stamp."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import inspect, text

from app.database import Base, engine

# Cargar toda la metadata que también usa Alembic.
import app.models.auditoria  # noqa: F401,E402
import app.models.auditoria_evento  # noqa: F401,E402
import app.models.auditoria_pro  # noqa: F401,E402
import app.models.automatizacion  # noqa: F401,E402
import app.models.backup_historial  # noqa: F401,E402
import app.models.categoria  # noqa: F401,E402
import app.models.configuracion  # noqa: F401,E402
import app.models.configuracion_saas  # noqa: F401,E402
import app.models.devops_evento  # noqa: F401,E402
import app.models.empresa  # noqa: F401,E402
import app.models.equipo  # noqa: F401,E402
import app.models.equipo_hoja_vida  # noqa: F401,E402
import app.models.evidencia  # noqa: F401,E402
import app.models.factura  # noqa: F401,E402
import app.models.formato_dinamico  # noqa: F401,E402
import app.models.formato_mantenimiento  # noqa: F401,E402
import app.models.hist_mantenimiento  # noqa: F401,E402
import app.models.historial_mantenimiento  # noqa: F401,E402
import app.models.login_attempt  # noqa: F401,E402
import app.models.log_sistema  # noqa: F401,E402
import app.models.mantenimiento  # noqa: F401,E402
import app.models.monitor_estado  # noqa: F401,E402
import app.models.notificacion  # noqa: F401,E402
import app.models.ot_incidencia  # noqa: F401,E402
import app.models.ot_repuesto  # noqa: F401,E402
import app.models.password_reset  # noqa: F401,E402
import app.models.permiso  # noqa: F401,E402
import app.models.plantilla_reporte  # noqa: F401,E402
import app.models.refresh_token  # noqa: F401,E402
import app.models.reporte_publicado  # noqa: F401,E402
import app.models.security_event  # noqa: F401,E402
import app.models.scheduler_inteligente  # noqa: F401,E402
import app.models.sede  # noqa: F401,E402
import app.models.solicitud_correctiva  # noqa: F401,E402
import app.models.smtp_log  # noqa: F401,E402
import app.models.tecnico  # noqa: F401,E402
import app.models.usuario  # noqa: F401,E402


def auditar() -> dict:
    inspector = inspect(engine)
    tablas_db = set(inspector.get_table_names(schema="public"))
    tablas_modelo = set(Base.metadata.tables)
    faltantes = sorted(tablas_modelo - tablas_db)
    extras = sorted(tablas_db - tablas_modelo - {"alembic_version"})
    columnas_faltantes = {}

    for tabla in sorted(tablas_modelo & tablas_db):
        reales = {item["name"] for item in inspector.get_columns(tabla)}
        esperadas = set(Base.metadata.tables[tabla].columns.keys())
        diferencia = sorted(esperadas - reales)
        if diferencia:
            columnas_faltantes[tabla] = diferencia

    with engine.connect() as connection:
        revision = connection.execute(
            text(
                "SELECT version_num FROM alembic_version LIMIT 1"
                if "alembic_version" in tablas_db
                else "SELECT NULL"
            )
        ).scalar()

    return {
        "revision_actual": revision,
        "tablas_modelo": len(tablas_modelo),
        "tablas_db": len(tablas_db),
        "tablas_faltantes": faltantes,
        "columnas_faltantes": columnas_faltantes,
        "tablas_extra": extras,
        "baseline_compatible": not faltantes and not columnas_faltantes,
        "advertencia": (
            "Compatible solo por presencia de tablas/columnas; haga backup y revise tipos, "
            "constraints e índices antes de ejecutar alembic stamp."
        ),
    }


if __name__ == "__main__":
    resultado = auditar()
    print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str))
    sys.exit(0 if resultado["baseline_compatible"] else 2)
