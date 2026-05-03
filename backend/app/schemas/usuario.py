# =========================================================
# SCHEMAS DE USUARIOS
# Validan creación de usuarios del sistema
# =========================================================

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class AdminCreate(BaseModel):
    # Datos para crear el primer administrador
    nombre_completo: str
    username: str
    email: EmailStr
    password: str


class UsuarioCreate(BaseModel):
    # Datos generales del usuario
    nombre_completo: str
    username: str
    email: EmailStr
    password: str

    # Roles permitidos: ADMIN, TECNICO, EMPRESA, COORDINADOR
    rol: str

    # Solo aplica para usuario EMPRESA
    empresa_id: Optional[UUID] = None