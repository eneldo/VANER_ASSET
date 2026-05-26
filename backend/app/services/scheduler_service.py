# ============================================================
# SERVICIO: Scheduler SaaS PRO
# Archivo: backend/app/services/scheduler_service.py
# ============================================================

from typing import Dict, Any, List

from app.automation.scheduler import obtener_scheduler


def estado_scheduler() -> Dict[str, Any]:
    scheduler = obtener_scheduler()
    jobs: List[Dict[str, Any]] = []

    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "nombre": job.name,
            "proxima_ejecucion": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        })

    return {
        "activo": scheduler.running,
        "estado": "ONLINE" if scheduler.running else "OFFLINE",
        "jobs": jobs,
    }
