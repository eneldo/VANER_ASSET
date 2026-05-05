# =========================================================
# SCHEMAS AUTH
# =========================================================

from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario_id: str
    nombre_completo: str
    rol: str
    empresa_id: Optional[str] = None