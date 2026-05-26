# ============================================================
# JOB PLACEHOLDER: limpieza_logs
# Archivo: backend/app/automation/jobs/cleanup_job.py
# ============================================================

import time

from app.database import SessionLocal
from app.services.automation_service import registrar_ejecucion


def ejecutar_cleanup_job() -> None:
    """Job base de limpieza de logs. Limpieza real se implementa luego."""
    inicio = time.perf_counter()
    db = SessionLocal()
    try:
        registrar_ejecucion(
            db=db,
            modulo="limpieza_logs",
            ok=True,
            mensaje="Job base de limpieza de logs. Limpieza real se implementa luego.",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    except Exception as exc:
        registrar_ejecucion(
            db=db,
            modulo="limpieza_logs",
            ok=False,
            mensaje=f"Error job limpieza_logs: {exc}",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    finally:
        db.close()
