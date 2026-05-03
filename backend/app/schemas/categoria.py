# =========================================================
# SCHEMAS CATEGORIA
# Validan entrada y salida de categorías
# =========================================================

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CategoriaBase(BaseModel):
    # Nombre de la categoría
    nombre: str

    # Descripción opcional
    descripcion: Optional[str] = None

    # Estado lógico
    activo: bool = True


class CategoriaCreate(CategoriaBase):
    # Schema para crear categoría
    pass


class CategoriaUpdate(BaseModel):
    # Schema para actualizar categoría parcialmente
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class CategoriaOut(CategoriaBase):
    # Respuesta completa de categoría
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True