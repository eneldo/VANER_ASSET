from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CategoriaBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    activo: bool = True


class CategoriaCreate(CategoriaBase):
    code: Optional[str] = Field(default=None, max_length=50)


class CategoriaUpdate(BaseModel):
    code: Optional[str] = Field(default=None, max_length=50)
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class CategoriaOut(CategoriaBase):
    id: UUID
    code: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
