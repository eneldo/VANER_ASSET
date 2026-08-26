# ============================================================
# SCHEDULER GLOBAL SGA SaaS PRO
# Archivo: backend/app/automation/scheduler.py
# Fase 34.2.1
# ============================================================
# El scheduler arranca junto con FastAPI. Sus jobs de esta fase
# son seguros: registran estado y preparan la base para próximas
# subfases sin tocar módulos actuales.
# ============================================================

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

from app.database import SessionLocal
from app.services.automation_service import inicializar_automatizaciones, listar_automatizaciones
from app.automation.jobs.monitor_job import ejecutar_monitor_job
from app.automation.jobs.backup_job import ejecutar_backup_job
from app.automation.jobs.smtp_job import ejecutar_smtp_job
from app.automation.jobs.whatsapp_job import ejecutar_whatsapp_job
from app.automation.jobs.cleanup_job import ejecutar_cleanup_job
from app.automation.jobs.mantenimiento_job import ejecutar_mantenimiento_job
from app.automation.jobs.vida_util_job import ejecutar_vida_util_job

_scheduler = BackgroundScheduler(
    executors={"default": ThreadPoolExecutor(5)},
    job_defaults={"coalesce": True, "max_instances": 1},
    timezone="UTC",
)

JOB_FUNCTIONS = {
    "monitor": ejecutar_monitor_job,
    "backups": ejecutar_backup_job,
    "smtp": ejecutar_smtp_job,
    "whatsapp": ejecutar_whatsapp_job,
    "limpieza_logs": ejecutar_cleanup_job,
    "mantenimientos": ejecutar_mantenimiento_job,
    "vida_util": ejecutar_vida_util_job,
}


def obtener_scheduler() -> BackgroundScheduler:
    return _scheduler


def sincronizar_jobs_desde_bd() -> None:
    """Lee automatizaciones activas y registra jobs en APScheduler."""

    db = SessionLocal()
    try:
        automatizaciones = inicializar_automatizaciones(db)

        for auto in automatizaciones:
            job_id = f"sga_auto_{auto.modulo}"
            existente = _scheduler.get_job(job_id)

            if not auto.activo:
                if existente:
                    _scheduler.remove_job(job_id)
                continue

            funcion = JOB_FUNCTIONS.get(auto.modulo)
            if not funcion:
                continue

            trigger = IntervalTrigger(minutes=max(int(auto.frecuencia_minutos or 60), 1))

            if existente:
                existente.reschedule(trigger=trigger)
            else:
                _scheduler.add_job(
                    funcion,
                    trigger=trigger,
                    id=job_id,
                    name=auto.nombre,
                    replace_existing=True,
                )
    finally:
        db.close()


def iniciar_scheduler_sga() -> None:
    """Inicia el scheduler una sola vez."""

    sincronizar_jobs_desde_bd()
    if not _scheduler.running:
        _scheduler.start()


def detener_scheduler_sga() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)


def reiniciar_jobs_sga() -> None:
    sincronizar_jobs_desde_bd()
