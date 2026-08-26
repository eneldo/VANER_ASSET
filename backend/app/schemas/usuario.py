# =========================================================
# SCHEMAS DE USUARIOS
# Validación de creación, edición, respuesta y reset password
# =========================================================

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class AdminCreate(BaseModel):
    nombre_completo: str
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UsuarioCreate(BaseModel):
    nombre_completo: str
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    rol: str
    empresa_id: Optional[UUID] = None
    empresa_ids: list[UUID] = Field(default_factory=list)


class UsuarioUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    empresa_id: Optional[UUID] = None
    empresa_ids: Optional[list[UUID]] = None
    activo: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    nueva_password: str = Field(..., min_length=8, max_length=128)


class CambioPasswordRequest(BaseModel):
    password_actual: str = Field(..., min_length=1)
    nueva_password: str = Field(..., min_length=8, max_length=128)
    confirmar_password: str = Field(..., min_length=1)


class UsuarioOut(BaseModel):
    id: UUID
    nombre_completo: str
    username: str
    email: str
    rol: str
    empresa_id: Optional[UUID] = None
    empresa_ids: list[UUID] = Field(default_factory=list)
    activo: bool
    debe_cambiar_password: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
