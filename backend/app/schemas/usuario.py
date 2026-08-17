# =========================================================
# SCHEMAS DE USUARIOS
# Validación de creación, edición, respuesta y reset password
# =========================================================

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class AdminCreate(BaseModel):
    # Crear primer administrador del sistema
    nombre_completo: str
    username: str
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)


class UsuarioCreate(BaseModel):
    # Crear usuario normal del sistema
    nombre_completo: str
    username: str
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    rol: str
    empresa_id: Optional[UUID] = None
    empresa_ids: list[UUID] = Field(default_factory=list)


class UsuarioUpdate(BaseModel):
    # Actualizar usuario parcialmente
    nombre_completo: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    empresa_id: Optional[UUID] = None
    empresa_ids: Optional[list[UUID]] = None
    activo: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    # Nueva contraseña del usuario
    nueva_password: str = Field(..., min_length=12, max_length=128)


class UsuarioOut(BaseModel):
    # Respuesta segura del usuario sin password_hash
    id: UUID
    nombre_completo: str
    username: str
    email: str
    rol: str
    empresa_id: Optional[UUID] = None
    empresa_ids: list[UUID] = Field(default_factory=list)
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
