# ============================================================
# SCHEMAS: Permisos PRO
# Archivo: app/schemas/permisos.py
# ============================================================

from typing import Optional, List
from pydantic import BaseModel


class PermisoOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    modulo: Optional[str] = None
    activo: bool = True

    class Config:
        from_attributes = True


class RolOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True

    class Config:
        from_attributes = True


class AsignarPermisosUsuarioRequest(BaseModel):
    usuario_id: str
    permisos: List[str]


class UsuarioPermisosOut(BaseModel):
    usuario_id: str
    permisos: List[str]


class RolPermisosOut(BaseModel):
    rol_id: int
    rol: str
    permisos: List[str]