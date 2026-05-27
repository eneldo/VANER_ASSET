# ============================================================
# JOB - SCHEDULER INTELIGENTE PRO
# Archivo: backend/app/automation/jobs/scheduler_inteligente_job.py
# ============================================================

from app.database import SessionLocal
from app.services.scheduler_inteligente_service import ejecutar_revision


def ejecutar_scheduler_inteligente_job():
    """Job seguro para APScheduler: abre/cierra sesión DB."""
    db = SessionLocal()
    try:
        return ejecutar_revision(db)
    finally:
        db.close()
