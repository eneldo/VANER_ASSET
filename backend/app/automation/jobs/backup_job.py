# ============================================================
# JOB PLACEHOLDER: backups
# Archivo: backend/app/automation/jobs/backup_job.py
# ============================================================

import time

from app.database import SessionLocal
from app.services.automation_service import registrar_ejecucion


def ejecutar_backup_job() -> None:
    """Job base de backups. Ejecución real se implementa en Fase 34.2.2."""
    inicio = time.perf_counter()
    db = SessionLocal()
    try:
        registrar_ejecucion(
            db=db,
            modulo="backups",
            ok=True,
            mensaje="Job base de backups. Ejecución real se implementa en Fase 34.2.2.",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    except Exception as exc:
        registrar_ejecucion(
            db=db,
            modulo="backups",
            ok=False,
            mensaje=f"Error job backups: {exc}",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    finally:
        db.close()
