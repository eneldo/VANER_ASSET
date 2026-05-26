# ============================================================
# JOB PLACEHOLDER: whatsapp
# Archivo: backend/app/automation/jobs/whatsapp_job.py
# ============================================================

import time

from app.database import SessionLocal
from app.services.automation_service import registrar_ejecucion


def ejecutar_whatsapp_job() -> None:
    """Job base WhatsApp. Integración real se implementa en Fase 34.2.4."""
    inicio = time.perf_counter()
    db = SessionLocal()
    try:
        registrar_ejecucion(
            db=db,
            modulo="whatsapp",
            ok=True,
            mensaje="Job base WhatsApp. Integración real se implementa en Fase 34.2.4.",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    except Exception as exc:
        registrar_ejecucion(
            db=db,
            modulo="whatsapp",
            ok=False,
            mensaje=f"Error job whatsapp: {exc}",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    finally:
        db.close()
