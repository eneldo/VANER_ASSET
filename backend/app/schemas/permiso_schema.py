# ================================================================
# SGAHolding - FASE 31.2
# Archivo: backend/app/schemas/permiso_schema.py
# Objetivo:
#   Esquemas Pydantic para exponer roles, permisos y asignaciones.
# ================================================================

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class PermisoOut(BaseModel):
    id: UUID
    codigo: str
    modulo: str
    accion: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True


class RolOut(BaseModel):
    id: UUID
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
    permisos: List[PermisoOut] = []

    class Config:
        from_attributes = True


class RolPermisosUpdate(BaseModel):
    permiso_ids: List[UUID] = Field(default_factory=list)


class UsuarioPermisosUpdate(BaseModel):
    permiso_ids: List[UUID] = Field(default_factory=list)


class UsuarioPermisosOut(BaseModel):
    usuario_id: UUID
    rol: Optional[str] = None
    permisos_rol: List[str] = []
    permisos_directos: List[str] = []
    permisos_finales: List[str] = []
