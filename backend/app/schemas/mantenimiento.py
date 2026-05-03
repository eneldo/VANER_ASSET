# =========================================================
# SCHEMAS MANTENIMIENTO
# Validan creación, actualización y cambios de estado
# =========================================================

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class MantenimientoBase(BaseModel):
    # Equipo asociado
    equipo_id: UUID

    # Técnico asignado, puede ir vacío al programar
    tecnico_id: Optional[UUID] = None

    # Tipo de mantenimiento
    tipo: str

    # Estado inicial
    estado: str = "PROGRAMADO"

    # Fecha programada
    fecha_programada: datetime

    # Información operativa
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    estado_inicial: Optional[str] = None
    acciones_realizadas: Optional[str] = None
    resultado_final: Optional[str] = None
    observaciones: Optional[str] = None


class MantenimientoCreate(MantenimientoBase):
    # Schema para crear mantenimiento
    pass


class MantenimientoUpdate(BaseModel):
    # Actualización parcial
    equipo_id: Optional[UUID] = None
    tecnico_id: Optional[UUID] = None
    tipo: Optional[str] = None
    estado: Optional[str] = None
    fecha_programada: Optional[datetime] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    estado_inicial: Optional[str] = None
    acciones_realizadas: Optional[str] = None
    resultado_final: Optional[str] = None
    observaciones: Optional[str] = None


class CambioEstadoMantenimiento(BaseModel):
    # Nuevo estado del mantenimiento
    estado_nuevo: str

    # Usuario que realiza el cambio
    usuario_id: Optional[UUID] = None

    # Comentario opcional
    comentario: Optional[str] = None


class MantenimientoOut(MantenimientoBase):
    # Respuesta completa
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True