# =========================================================
# SCHEMAS EMPRESA
# Validan entrada y salida de datos de empresas
# =========================================================

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class EmpresaBase(BaseModel):
    # Datos generales de empresa
    nombre: str
    nit: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    correo: Optional[EmailStr] = None

    # Logo de empresa cliente para hoja de vida
    logo_url: Optional[str] = None

    # Estado
    activo: bool = True

    @field_validator("nit", "telefono", "direccion", "correo", "logo_url", mode="before")
    @classmethod
    def normalizar_campos_opcionales(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class EmpresaCreate(EmpresaBase):
    # Schema usado para crear empresa
    pass


class EmpresaUpdate(BaseModel):
    # Schema usado para actualizar parcialmente empresa
    nombre: Optional[str] = None
    nit: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    correo: Optional[EmailStr] = None
    logo_url: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("nit", "telefono", "direccion", "correo", "logo_url", mode="before")
    @classmethod
    def normalizar_campos_opcionales(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class EmpresaOut(EmpresaBase):
    # Respuesta completa de empresa
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
