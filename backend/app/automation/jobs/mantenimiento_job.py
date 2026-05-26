# ============================================================
# JOB PLACEHOLDER: mantenimientos
# Archivo: backend/app/automation/jobs/mantenimiento_job.py
# ============================================================

import time

from app.database import SessionLocal
from app.services.automation_service import registrar_ejecucion


def ejecutar_mantenimiento_job() -> None:
    """Job base de automatización de mantenimientos."""
    inicio = time.perf_counter()
    db = SessionLocal()
    try:
        registrar_ejecucion(
            db=db,
            modulo="mantenimientos",
            ok=True,
            mensaje="Job base de automatización de mantenimientos.",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    except Exception as exc:
        registrar_ejecucion(
            db=db,
            modulo="mantenimientos",
            ok=False,
            mensaje=f"Error job mantenimientos: {exc}",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    finally:
        db.close()
