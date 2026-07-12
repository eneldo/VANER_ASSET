# =========================================================
# SCHEMAS CATEGORIA
# Validan entrada y salida de categorías
# =========================================================

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CategoriaBase(BaseModel):
    code: str
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
    # Solo la descripción es configurable; código/nombre/estado son canónicos.
    descripcion: Optional[str] = None


class CategoriaOut(CategoriaBase):
    # Respuesta completa de categoría
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
