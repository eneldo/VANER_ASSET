# =========================================================
# SCHEMAS AUTH - FASE 31.1 JWT PRO
# Define las entradas/salidas del login, refresh, logout y sesión.
# =========================================================

from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario_id: str
    nombre_completo: str
    rol: str
    empresa_id: Optional[str] = None


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario_id: str
    nombre_completo: str
    rol: str
    empresa_id: Optional[str] = None


class MeResponse(BaseModel):
    usuario_id: str
    nombre_completo: str
    username: str
    email: str
    rol: str
    empresa_id: Optional[str] = None
    activo: bool
