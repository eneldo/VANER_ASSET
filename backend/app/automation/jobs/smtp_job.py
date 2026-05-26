# ============================================================
# JOB PLACEHOLDER: smtp
# Archivo: backend/app/automation/jobs/smtp_job.py
# ============================================================

import time

from app.database import SessionLocal
from app.services.automation_service import registrar_ejecucion


def ejecutar_smtp_job() -> None:
    """Job base SMTP. Envío real se implementa en Fase 34.2.3."""
    inicio = time.perf_counter()
    db = SessionLocal()
    try:
        registrar_ejecucion(
            db=db,
            modulo="smtp",
            ok=True,
            mensaje="Job base SMTP. Envío real se implementa en Fase 34.2.3.",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    except Exception as exc:
        registrar_ejecucion(
            db=db,
            modulo="smtp",
            ok=False,
            mensaje=f"Error job smtp: {exc}",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    finally:
        db.close()
