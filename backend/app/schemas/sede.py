# =========================================================
# SCHEMAS SEDE
# Validan entrada y salida de datos de sedes
# =========================================================

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class SedeBase(BaseModel):
    # Relación con empresa
    empresa_id: UUID

    # Datos principales
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    responsable: Optional[str] = None

    # Estado
    activo: bool = True


class SedeCreate(SedeBase):
    # Schema usado para crear sede
    pass


class SedeUpdate(BaseModel):
    # Schema usado para actualizar sede parcialmente
    empresa_id: Optional[UUID] = None
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    responsable: Optional[str] = None
    activo: Optional[bool] = None


class SedeOut(SedeBase):
    # Respuesta completa de sede
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True