# ============================================================
# SCHEMAS: Auditoría Sistema
# Proyecto: SGA PRO
# ============================================================

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AuditoriaCreate(BaseModel):
    usuario_id: Optional[UUID] = None
    usuario_nombre: Optional[str] = None
    usuario_rol: Optional[str] = None

    modulo: str
    accion: str
    descripcion: Optional[str] = None

    entidad: Optional[str] = None
    entidad_id: Optional[UUID] = None

    ip_origen: Optional[str] = None
    user_agent: Optional[str] = None


class AuditoriaOut(AuditoriaCreate):
    id: UUID
    fecha: datetime

    class Config:
        from_attributes = True