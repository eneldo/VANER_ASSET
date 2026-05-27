# ============================================================
# SERVICIO MONITOR VPS + POSTGRESQL PRO
# Archivo: backend/app/services/monitor_vps_service.py
# Fase 34.2.4 - Monitor VPS + PostgreSQL PRO
# ============================================================
# Objetivo:
# - Consultar estado del servidor VPS sin afectar módulos existentes.
# - Consultar métricas básicas de PostgreSQL usando SQLAlchemy.
# - Consultar estado Docker de forma segura y tolerante a errores.
# ============================================================

from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

import psutil
from sqlalchemy import text
from sqlalchemy.orm import Session


# ============================================================
# UTILIDADES
# ============================================================

def _bytes_to_gb(value: float | int) -> float:
    """Convierte bytes a GB con dos decimales."""
    try:
        return round(float(value) / (1024 ** 3), 2)
    except Exception:
        return 0.0


def _safe_percent(value: Any) -> float:
    """Normaliza porcentajes."""
    try:
        return round(float(value), 2)
    except Exception:
        return 0.0


def _run_command(command: List[str], timeout: int = 5) -> Dict[str, Any]:
    """Ejecuta comandos del sistema de forma segura."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except Exception as exc:
        return {
            "ok": False,
            "stdout": "",
            "stderr": str(exc),
            "returncode": -1,
        }


# ============================================================
# MONITOR VPS
# ============================================================

def obtener_estado_vps() -> Dict[str, Any]:
    """Obtiene métricas generales del VPS/servidor."""

    boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
    now = datetime.now(timezone.utc)
    uptime_seconds = int((now - boot_time).total_seconds())

    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    net = psutil.net_io_counters()

    return {
        "timestamp": now.isoformat(),
        "hostname": socket.gethostname(),
        "sistema": platform.system(),
        "plataforma": platform.platform(),
        "python_version": platform.python_version(),
        "uptime_seconds": uptime_seconds,
        "uptime_horas": round(uptime_seconds / 3600, 2),
        "cpu_percent": _safe_percent(psutil.cpu_percent(interval=0.2)),
        "cpu_cores_logicos": psutil.cpu_count(logical=True),
        "cpu_cores_fisicos": psutil.cpu_count(logical=False),
        "ram_total_gb": _bytes_to_gb(mem.total),
        "ram_usada_gb": _bytes_to_gb(mem.used),
        "ram_libre_gb": _bytes_to_gb(mem.available),
        "ram_percent": _safe_percent(mem.percent),
        "disco_total_gb": _bytes_to_gb(disk.total),
        "disco_usado_gb": _bytes_to_gb(disk.used),
        "disco_libre_gb": _bytes_to_gb(disk.free),
        "disco_percent": _safe_percent(disk.percent),
        "red_bytes_enviados_gb": _bytes_to_gb(net.bytes_sent),
        "red_bytes_recibidos_gb": _bytes_to_gb(net.bytes_recv),
    }


# ============================================================
# MONITOR POSTGRESQL
# ============================================================

def obtener_estado_postgresql(db: Session) -> Dict[str, Any]:
    """Obtiene métricas de PostgreSQL sin modificar datos."""

    info: Dict[str, Any] = {
        "ok": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mensaje": "PostgreSQL disponible",
    }

    try:
        version = db.execute(text("SELECT version() AS version")).mappings().first()
        current_db = db.execute(text("SELECT current_database() AS db")).mappings().first()
        current_user = db.execute(text("SELECT current_user AS usuario")).mappings().first()

        db_size = db.execute(
            text("SELECT pg_database_size(current_database()) AS size_bytes")
        ).mappings().first()

        conexiones = db.execute(
            text(
                """
                SELECT
                  count(*) AS total,
                  count(*) FILTER (WHERE state = 'active') AS activas,
                  count(*) FILTER (WHERE state = 'idle') AS idle
                FROM pg_stat_activity
                WHERE datname = current_database()
                """
            )
        ).mappings().first()

        tablas = db.execute(
            text(
                """
                SELECT count(*) AS total_tablas
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            )
        ).mappings().first()

        info.update(
            {
                "version": version["version"] if version else None,
                "base_datos": current_db["db"] if current_db else None,
                "usuario": current_user["usuario"] if current_user else None,
                "tamano_bytes": int(db_size["size_bytes"]) if db_size else 0,
                "tamano_gb": _bytes_to_gb(db_size["size_bytes"] if db_size else 0),
                "conexiones_total": int(conexiones["total"] or 0) if conexiones else 0,
                "conexiones_activas": int(conexiones["activas"] or 0) if conexiones else 0,
                "conexiones_idle": int(conexiones["idle"] or 0) if conexiones else 0,
                "total_tablas": int(tablas["total_tablas"] or 0) if tablas else 0,
            }
        )

    except Exception as exc:
        info.update(
            {
                "ok": False,
                "mensaje": f"No fue posible consultar PostgreSQL: {exc}",
            }
        )

    return info


# ============================================================
# MONITOR DOCKER
# ============================================================

def obtener_estado_docker() -> Dict[str, Any]:
    """Obtiene estado Docker si el binario está disponible en el contenedor/host."""

    if not shutil.which("docker"):
        return {
            "ok": False,
            "mensaje": "Docker CLI no está disponible dentro del contenedor backend.",
            "containers": [],
        }

    cmd = _run_command(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}|{{.Status}}|{{.Image}}|{{.Ports}}",
        ],
        timeout=6,
    )

    if not cmd["ok"]:
        return {
            "ok": False,
            "mensaje": cmd["stderr"] or "No fue posible consultar Docker.",
            "containers": [],
        }

    containers = []
    for line in cmd["stdout"].splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            containers.append(
                {
                    "nombre": parts[0],
                    "estado": parts[1],
                    "imagen": parts[2],
                    "puertos": parts[3],
                }
            )

    return {
        "ok": True,
        "mensaje": "Docker disponible",
        "containers": containers,
        "total_containers": len(containers),
    }


# ============================================================
# RESUMEN GENERAL
# ============================================================

def obtener_resumen_monitor(db: Session) -> Dict[str, Any]:
    """Resumen único para dashboard frontend."""

    vps = obtener_estado_vps()
    postgres = obtener_estado_postgresql(db)
    docker = obtener_estado_docker()

    alertas = []

    if vps.get("cpu_percent", 0) >= 85:
        alertas.append("CPU alta")
    if vps.get("ram_percent", 0) >= 90:
        alertas.append("RAM alta")
    if vps.get("disco_percent", 0) >= 85:
        alertas.append("Disco con poco espacio")
    if not postgres.get("ok"):
        alertas.append("PostgreSQL no disponible")

    return {
        "ok": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vps": vps,
        "postgresql": postgres,
        "docker": docker,
        "alertas": alertas,
        "estado_general": "ALERTA" if alertas else "OK",
    }
