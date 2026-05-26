# ============================================================
# JOB: Backup Automático SaaS
# Archivo: backend/app/automation/jobs/backup_job.py
# Fase 34.2.2
# ============================================================

from app.database import SessionLocal
from app.services.smart_backup_service import SmartBackupService


def ejecutar_backup_automatico():
    """Job invocado por el scheduler. No se activa si el módulo backups está OFF."""
    db = SessionLocal()
    try:
        service = SmartBackupService(db)
        return service.ejecutar_backup(
            tipo="AUTOMATICO",
            incluir_db=True,
            incluir_uploads=True,
            incluir_codigo=False,
            creado_por="scheduler",
        )
    finally:
        db.close()
