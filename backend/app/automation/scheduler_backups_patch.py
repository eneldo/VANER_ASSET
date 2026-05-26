# ============================================================
# PATCH OPCIONAL: Integración Scheduler 34.2.2
# Archivo: backend/app/automation/scheduler_backups_patch.py
# Uso: referencia para agregar job de backups al scheduler 34.2.1
# ============================================================

from app.automation.jobs.backup_job import ejecutar_backup_automatico


def registrar_job_backups(scheduler):
    """
    Agregar dentro de tu scheduler.py si deseas activar job automático real:

    registrar_job_backups(scheduler)
    """
    if not scheduler.get_job("backup_automatico_sga"):
        scheduler.add_job(
            ejecutar_backup_automatico,
            "interval",
            minutes=1440,
            id="backup_automatico_sga",
            replace_existing=True,
            max_instances=1,
        )
