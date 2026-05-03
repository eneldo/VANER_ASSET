# =========================================================
# SCHEMAS TECNICO
# Validan creación y respuesta de técnicos
# =========================================================

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class TecnicoBase(BaseModel):
    # Usuario con rol TECNICO
    usuario_id: UUID

    # Datos del técnico
    documento: Optional[str] = None
    telefono: Optional[str] = None
    especialidad: Optional[str] = None
    cargo: Optional[str] = None

    # Estado lógico
    activo: bool = True


class TecnicoCreate(TecnicoBase):
    pass


class TecnicoUpdate(BaseModel):
    documento: Optional[str] = None
    telefono: Optional[str] = None
    especialidad: Optional[str] = None
    cargo: Optional[str] = None
    activo: Optional[bool] = None


class TecnicoOut(TecnicoBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True