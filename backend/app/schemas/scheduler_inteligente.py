# ============================================================
# SCHEMAS - SCHEDULER INTELIGENTE PRO
# Archivo: backend/app/schemas/scheduler_inteligente.py
# Fase 34.2.7
# ============================================================

from datetime import date, datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SchedulerReglaBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=180)
    descripcion: Optional[str] = None

    # IMPORTANTE:
    # En SGA SaaS, equipos.id y tecnicos.id son UUID.
    equipo_id: UUID
    tecnico_id: Optional[UUID] = None

    tipo_mantenimiento: str = "PREVENTIVO"
    frecuencia_dias: int = Field(30, ge=1, le=3650)
    fecha_inicio: date
    proxima_fecha: Optional[date] = None

    prioridad: str = "MEDIA"
    estado_inicial: str = "PROGRAMADO"

    # MANUAL / SEMIAUTOMATICO / AUTOMATICO
    modo: str = "SEMIAUTOMATICO"

    activo: bool = True
    configuracion: Dict[str, Any] = {}


class SchedulerReglaCreate(SchedulerReglaBase):
    pass


class SchedulerReglaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

    equipo_id: Optional[UUID] = None
    tecnico_id: Optional[UUID] = None

    tipo_mantenimiento: Optional[str] = None
    frecuencia_dias: Optional[int] = Field(None, ge=1, le=3650)
    fecha_inicio: Optional[date] = None
    proxima_fecha: Optional[date] = None

    prioridad: Optional[str] = None
    estado_inicial: Optional[str] = None
    modo: Optional[str] = None
    activo: Optional[bool] = None

    configuracion: Optional[Dict[str, Any]] = None


class SchedulerReglaOut(SchedulerReglaBase):
    id: UUID

    # En tu tabla mantenimientos el id continúa siendo INTEGER.
    ultimo_mantenimiento_id: Optional[int] = None

    ultima_ejecucion: Optional[datetime] = None
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class SchedulerSugerenciaOut(BaseModel):
    id: UUID
    regla_id: UUID

    equipo_id: UUID
    tecnico_id: Optional[UUID] = None

    tipo_mantenimiento: str
    fecha_programada: date
    prioridad: str
    estado: str
    mensaje: Optional[str] = None

    # En tu tabla mantenimientos el id continúa siendo INTEGER.
    mantenimiento_id: Optional[int] = None

    creado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class SchedulerLogOut(BaseModel):
    id: UUID
    nivel: str
    evento: str
    mensaje: Optional[str] = None
    metadata_json: Dict[str, Any] | None = None
    creado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class SchedulerRunResult(BaseModel):
    ok: bool
    mensaje: str
    reglas_revisadas: int = 0
    sugerencias_creadas: int = 0
    mantenimientos_creados: int = 0