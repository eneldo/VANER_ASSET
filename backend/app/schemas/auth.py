# =========================================================
# SCHEMAS AUTH - FASE 31.1 JWT PRO
# Define las entradas/salidas del login, refresh, logout y sesión.
# =========================================================

from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    usuario_id: str
    nombre_completo: str
    rol: str
    empresa_id: Optional[str] = None
    empresa_ids: list[str] = Field(default_factory=list)
    debe_cambiar_password: bool = False


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    usuario_id: str
    nombre_completo: str
    rol: str
    empresa_id: Optional[str] = None
    empresa_ids: list[str] = Field(default_factory=list)


class MeResponse(BaseModel):
    usuario_id: str
    nombre_completo: str
    username: str
    email: str
    rol: str
    empresa_id: Optional[str] = None
    empresa_ids: list[str] = Field(default_factory=list)
    activo: bool
