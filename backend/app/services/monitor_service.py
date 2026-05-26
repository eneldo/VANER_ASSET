# ============================================================
# SERVICIO: Monitor Sistema SaaS
# Archivo: backend/app/services/monitor_service.py
# ============================================================

import time
from functools import lru_cache
from typing import Dict, Any

import psutil


@lru_cache(maxsize=1)
def _boot_time() -> float:
    return psutil.boot_time()


def obtener_estado_sistema() -> Dict[str, Any]:
    """Obtiene métricas básicas del VPS/contenedor sin modificar nada."""

    ram = psutil.virtual_memory()
    disco = psutil.disk_usage("/")

    return {
        "cpu_percent": float(psutil.cpu_percent(interval=0.1)),
        "ram_percent": float(ram.percent),
        "ram_total_gb": round(ram.total / (1024 ** 3), 2),
        "ram_usada_gb": round(ram.used / (1024 ** 3), 2),
        "disco_percent": float(disco.percent),
        "disco_total_gb": round(disco.total / (1024 ** 3), 2),
        "disco_usado_gb": round(disco.used / (1024 ** 3), 2),
        "uptime_segundos": round(time.time() - _boot_time(), 2),
    }
