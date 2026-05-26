# ============================================================
# JOB: Monitor Sistema
# Archivo: backend/app/automation/jobs/monitor_job.py
# ============================================================

import time

from app.database import SessionLocal
from app.services.automation_service import registrar_ejecucion
from app.services.monitor_service import obtener_estado_sistema


def ejecutar_monitor_job() -> None:
    inicio = time.perf_counter()
    db = SessionLocal()
    try:
        estado = obtener_estado_sistema()
        mensaje = (
            f"CPU {estado['cpu_percent']}% | RAM {estado['ram_percent']}% | "
            f"Disco {estado['disco_percent']}%"
        )
        registrar_ejecucion(
            db=db,
            modulo="monitor",
            ok=True,
            mensaje=mensaje,
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    except Exception as exc:
        registrar_ejecucion(
            db=db,
            modulo="monitor",
            ok=False,
            mensaje=f"Error monitor: {exc}",
            duracion_ms=int((time.perf_counter() - inicio) * 1000),
        )
    finally:
        db.close()
