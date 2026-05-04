# =========================================================
# SCHEMAS DE USUARIOS
# Validación de creación, edición, respuesta y reset password
# =========================================================

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class AdminCreate(BaseModel):
    # Crear primer administrador del sistema
    nombre_completo: str
    username: str
    email: EmailStr
    password: str


class UsuarioCreate(BaseModel):
    # Crear usuario normal del sistema
    nombre_completo: str
    username: str
    email: EmailStr
    password: str
    rol: str
    empresa_id: Optional[UUID] = None


class UsuarioUpdate(BaseModel):
    # Actualizar usuario parcialmente
    nombre_completo: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    empresa_id: Optional[UUID] = None
    activo: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    # Nueva contraseña del usuario
    nueva_password: str


class UsuarioOut(BaseModel):
    # Respuesta segura del usuario sin password_hash
    id: UUID
    nombre_completo: str
    username: str
    email: EmailStr
    rol: str
    empresa_id: Optional[UUID] = None
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True