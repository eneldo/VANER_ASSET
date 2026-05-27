# ============================================================
# SERVICE: DevOps SaaS PRO
# Archivo: backend/app/services/devops_service.py
# FASE 34.2.6
# ============================================================
# Servicio defensivo: si Docker CLI no está disponible dentro del
# contenedor backend, responde sin romper la aplicación.
# ============================================================

import os
import platform
import socket
import subprocess
from datetime import datetime, timezone
from typing import Any

import psutil

from app.schemas.devops_saas import (
    DevOpsAccionRespuesta,
    DevOpsLogRespuesta,
    DevOpsRespuesta,
    DevOpsResumen,
    DevOpsServicioEstado,
    DevOpsSistema,
)


SERVICIOS_CLAVE = {
    "backend": ["sga_backend", "backend"],
    "frontend": ["sga_frontend", "frontend"],
    "postgresql": ["sga_postgres", "postgres"],
    "traefik": ["traefik", "dokploy-traefik"],
    "redis": ["redis", "dokploy-redis"],
}


def _ejecutar_comando(comando: list[str], timeout: int = 6) -> tuple[bool, str]:
    """Ejecuta comandos del sistema de manera segura."""
    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        salida = (resultado.stdout or resultado.stderr or "").strip()
        return resultado.returncode == 0, salida
    except FileNotFoundError:
        return False, f"Comando no disponible: {comando[0]}"
    except subprocess.TimeoutExpired:
        return False, "Tiempo de espera agotado ejecutando comando"
    except Exception as exc:
        return False, str(exc)


def _docker_disponible() -> bool:
    ok, _ = _ejecutar_comando(["docker", "ps", "--format", "{{.Names}}"], timeout=4)
    return ok


def obtener_sistema() -> DevOpsSistema:
    """Obtiene métricas del servidor visible desde el contenedor."""
    memoria = psutil.virtual_memory()
    disco = psutil.disk_usage("/")
    boot = psutil.boot_time()
    uptime_horas = round((datetime.now().timestamp() - boot) / 3600, 2)

    return DevOpsSistema(
        hostname=socket.gethostname(),
        plataforma=platform.platform(),
        uptime_horas=uptime_horas,
        cpu_pct=round(psutil.cpu_percent(interval=0.2), 2),
        ram_pct=round(memoria.percent, 2),
        ram_usada_gb=round(memoria.used / (1024 ** 3), 2),
        ram_total_gb=round(memoria.total / (1024 ** 3), 2),
        disco_pct=round(disco.percent, 2),
        disco_usado_gb=round(disco.used / (1024 ** 3), 2),
        disco_total_gb=round(disco.total / (1024 ** 3), 2),
    )


def listar_servicios_docker() -> tuple[bool, list[DevOpsServicioEstado]]:
    """Lista contenedores Docker si el CLI está disponible."""
    formato = "{{.Names}}||{{.Image}}||{{.Status}}||{{.Ports}}||{{.RunningFor}}"
    ok, salida = _ejecutar_comando(["docker", "ps", "-a", "--format", formato], timeout=6)

    if not ok:
        return False, [
            DevOpsServicioEstado(
                nombre="Docker CLI",
                tipo="docker",
                estado="NO DISPONIBLE",
                error=salida,
            )
        ]

    servicios: list[DevOpsServicioEstado] = []
    for linea in salida.splitlines():
        partes = linea.split("||")
        while len(partes) < 5:
            partes.append("")
        nombre, imagen, estado, puertos, creado = partes[:5]
        servicios.append(
            DevOpsServicioEstado(
                nombre=nombre,
                imagen=imagen,
                estado=estado,
                puertos=puertos,
                creado=creado,
            )
        )

    return True, servicios


def _estado_por_alias(servicios: list[DevOpsServicioEstado], aliases: list[str]) -> str:
    for servicio in servicios:
        nombre = servicio.nombre.lower()
        if any(alias.lower() in nombre for alias in aliases):
            if "up" in servicio.estado.lower():
                return "Online"
            return servicio.estado or "Detectado"
    return "No detectado"


def obtener_estado_devops() -> DevOpsRespuesta:
    docker_ok, servicios = listar_servicios_docker()
    activos = sum(1 for s in servicios if "up" in (s.estado or "").lower())

    resumen = DevOpsResumen(
        backend=_estado_por_alias(servicios, SERVICIOS_CLAVE["backend"]),
        frontend=_estado_por_alias(servicios, SERVICIOS_CLAVE["frontend"]),
        postgresql=_estado_por_alias(servicios, SERVICIOS_CLAVE["postgresql"]),
        traefik=_estado_por_alias(servicios, SERVICIOS_CLAVE["traefik"]),
        redis=_estado_por_alias(servicios, SERVICIOS_CLAVE["redis"]),
        docker_disponible=docker_ok,
        servicios_total=len(servicios),
        servicios_activos=activos,
        timestamp=datetime.now(timezone.utc),
    )

    return DevOpsRespuesta(
        resumen=resumen,
        sistema=obtener_sistema(),
        servicios=servicios,
    )


def obtener_logs_servicio(servicio: str, lineas: int = 80) -> DevOpsLogRespuesta:
    """Devuelve logs rápidos de un contenedor."""
    servicio_seguro = "".join(c for c in servicio if c.isalnum() or c in "_-.")[:80]
    lineas = max(10, min(int(lineas or 80), 300))

    ok, salida = _ejecutar_comando(
        ["docker", "logs", "--tail", str(lineas), servicio_seguro],
        timeout=8,
    )

    if not ok:
        salida = salida or "No fue posible leer logs del servicio."

    return DevOpsLogRespuesta(
        servicio=servicio_seguro,
        lineas=salida.splitlines(),
        obtenido_en=datetime.now(timezone.utc),
    )


def ejecutar_accion_servicio(servicio: str, accion: str) -> DevOpsAccionRespuesta:
    """Control opcional de contenedores. Desactivado por defecto."""
    permitir_control = os.getenv("DEVOPS_ALLOW_CONTROL", "false").lower() == "true"
    servicio_seguro = "".join(c for c in servicio if c.isalnum() or c in "_-.")[:80]
    accion = (accion or "").lower().strip()

    if accion not in {"restart", "stop", "start"}:
        return DevOpsAccionRespuesta(
            ok=False,
            mensaje="Acción no permitida. Use restart, stop o start.",
            servicio=servicio_seguro,
            accion=accion,
        )

    if not permitir_control:
        return DevOpsAccionRespuesta(
            ok=False,
            mensaje=(
                "Control DevOps deshabilitado por seguridad. "
                "Active DEVOPS_ALLOW_CONTROL=true solo si montó Docker de forma segura."
            ),
            servicio=servicio_seguro,
            accion=accion,
        )

    ok, salida = _ejecutar_comando(["docker", accion, servicio_seguro], timeout=15)
    return DevOpsAccionRespuesta(
        ok=ok,
        mensaje="Acción ejecutada" if ok else "No fue posible ejecutar la acción",
        servicio=servicio_seguro,
        accion=accion,
        detalle=salida,
    )
