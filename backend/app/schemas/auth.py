# =========================================================
# SCHEMAS DE AUTENTICACIÓN
# Define los datos que entran y salen del login
# =========================================================

from pydantic import BaseModel


class LoginRequest(BaseModel):
    # Puede ser username o correo
    username: str

    # Contraseña enviada desde el frontend
    password: str


class TokenResponse(BaseModel):
    # Token JWT generado
    access_token: str

    # Tipo de token
    token_type: str = "bearer"

    # Datos del usuario autenticado
    usuario_id: str
    nombre_completo: str
    rol: str