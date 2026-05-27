# ============================================================
# SCHEMAS: DevOps SaaS PRO
# Archivo: backend/app/schemas/devops_saas.py
# FASE 34.2.6
# ============================================================

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class DevOpsServicioEstado(BaseModel):
    nombre: str
    tipo: str = "docker"
    estado: str
    imagen: Optional[str] = None
    puertos: Optional[str] = None
    creado: Optional[str] = None
    uptime: Optional[str] = None
    cpu_pct: Optional[float] = None
    memoria: Optional[str] = None
    error: Optional[str] = None


class DevOpsResumen(BaseModel):
    backend: str
    frontend: str
    postgresql: str
    traefik: str
    redis: str
    docker_disponible: bool
    servicios_total: int
    servicios_activos: int
    timestamp: datetime


class DevOpsSistema(BaseModel):
    hostname: str
    plataforma: str
    uptime_horas: float
    cpu_pct: float
    ram_pct: float
    ram_usada_gb: float
    ram_total_gb: float
    disco_pct: float
    disco_usado_gb: float
    disco_total_gb: float


class DevOpsRespuesta(BaseModel):
    resumen: DevOpsResumen
    sistema: DevOpsSistema
    servicios: list[DevOpsServicioEstado]


class DevOpsLogRespuesta(BaseModel):
    servicio: str
    lineas: list[str]
    obtenido_en: datetime


class DevOpsAccionRequest(BaseModel):
    servicio: str
    accion: str  # restart | stop | start


class DevOpsAccionRespuesta(BaseModel):
    ok: bool
    mensaje: str
    servicio: str
    accion: str
    detalle: Optional[Any] = None
