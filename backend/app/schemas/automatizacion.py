# ============================================================
# SCHEMAS: Automatización SaaS PRO
# Archivo: backend/app/schemas/automatizacion.py
# ============================================================

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AutomatizacionBase(BaseModel):
    modulo: str = Field(..., min_length=2, max_length=80)
    nombre: str = Field(..., min_length=2, max_length=150)
    descripcion: Optional[str] = None
    activo: bool = False
    frecuencia_minutos: int = Field(default=60, ge=1, le=10080)
    configuracion: Optional[Dict[str, Any]] = None


class AutomatizacionUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, max_length=150)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    frecuencia_minutos: Optional[int] = Field(default=None, ge=1, le=10080)
    configuracion: Optional[Dict[str, Any]] = None


class AutomatizacionOut(AutomatizacionBase):
    id: UUID
    estado: str
    mensaje: Optional[str] = None
    ultima_ejecucion: Optional[datetime] = None
    proxima_ejecucion: Optional[datetime] = None
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class AutomatizacionLogOut(BaseModel):
    id: UUID
    modulo: str
    nivel: str
    evento: str
    mensaje: Optional[str] = None
    duracion_ms: Optional[int] = None
    metadata_json: Optional[Dict[str, Any]] = None
    creado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class SchedulerStatusOut(BaseModel):
    activo: bool
    estado: str
    jobs: List[Dict[str, Any]]


class MonitorSistemaOut(BaseModel):
    cpu_percent: float
    ram_percent: float
    ram_total_gb: float
    ram_usada_gb: float
    disco_percent: float
    disco_total_gb: float
    disco_usado_gb: float
    uptime_segundos: Optional[float] = None
