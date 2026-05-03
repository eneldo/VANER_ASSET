# =========================================================
# SCHEMAS EQUIPO
# Validan datos básicos del equipo - PASO 1
# =========================================================

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class EquipoBase(BaseModel):
    # Relaciones principales
    empresa_id: UUID
    sede_id: UUID
    categoria_id: Optional[UUID] = None

    # Datos básicos del equipo
    nombre: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    ubicacion: Optional[str] = None
    invima: Optional[str] = None
    codigo_id: Optional[str] = None

    # Estado y criticidad
    estado: str = "OPERATIVO"
    criticidad: str = "MEDIA"

    # Estado lógico
    activo: bool = True


class EquipoCreate(EquipoBase):
    # Schema para crear equipo básico
    pass


class EquipoUpdate(BaseModel):
    # Schema para actualizar parcialmente el equipo
    empresa_id: Optional[UUID] = None
    sede_id: Optional[UUID] = None
    categoria_id: Optional[UUID] = None

    nombre: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    ubicacion: Optional[str] = None
    invima: Optional[str] = None
    codigo_id: Optional[str] = None

    estado: Optional[str] = None
    criticidad: Optional[str] = None
    activo: Optional[bool] = None


class EquipoOut(EquipoBase):
    # Respuesta completa de equipo
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True