# ============================================================
# BACKUP JOB - SGA SaaS PRO
# Archivo: app/automation/jobs/backup_job.py
# FASE 34.2.2
# ============================================================

from datetime import datetime

from app.database import SessionLocal
from app.services.smart_backup_service import SmartBackupService


def ejecutar_backup_job():
    """
    Job principal de backups automáticos.
    """

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db = SessionLocal()

    try:
        backup = SmartBackupService(db).ejecutar_backup(
            tipo="AUTOMATICO",
            incluir_db=True,
            incluir_uploads=True,
            incluir_codigo=False,
            creado_por="scheduler",
        )
        return {
            "ok": True,
            "mensaje": "Backup automático ejecutado",
            "fecha": ahora,
            "backup_id": str(backup.id),
            "archivo": backup.nombre_archivo,
        }
    finally:
        db.close()
