# =========================================================
# SEGURIDAD SGA PRO - FASE 31.1
# JWT PRO + REFRESH TOKENS + LOGOUT SEGURO
#
# Este archivo reemplaza/actualiza backend/app/security.py
# Mantiene pbkdf2_sha256 para evitar problemas conocidos de bcrypt
# en Windows, y agrega:
#   - Access token corto
#   - Refresh token largo
#   - Hash SHA-256 de refresh token
#   - Validación de tokens con tipo: access / refresh
# =========================================================

from datetime import datetime, timedelta
from hashlib import sha256
from typing import Any, Optional
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# =========================================================
# PASSWORD HASHING
# =========================================================

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """Encripta una contraseña usando PBKDF2-SHA256."""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica si una contraseña coincide con su hash."""
    return pwd_context.verify(password, password_hash)


# =========================================================
# JWT HELPERS
# =========================================================

def _minutes(value: Any, default: int) -> int:
    """Convierte valores de configuración a entero de forma segura."""
    try:
        return int(value)
    except Exception:
        return default


def get_access_token_minutes() -> int:
    """Minutos de vida del access token."""
    return _minutes(getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30), 30)


def get_refresh_token_minutes() -> int:
    """Minutos de vida del refresh token. Default: 7 días."""
    return _minutes(getattr(settings, "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7), 60 * 24 * 7)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un access token JWT.
    Uso: Autorización normal contra endpoints protegidos.
    Duración recomendada: corta.
    """
    payload = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=get_access_token_minutes()))

    payload.update({
        "exp": expire,
        "type": "access",
        "jti": str(uuid4()),
    })

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, str, datetime]:
    """
    Crea un refresh token JWT.
    Retorna:
      - token plano para enviarlo al frontend
      - jti para guardarlo en BD
      - fecha de expiración
    """
    payload = data.copy()
    jti = str(uuid4())
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=get_refresh_token_minutes()))

    payload.update({
        "exp": expire,
        "type": "refresh",
        "jti": jti,
    })

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti, expire


def decode_token(token: str) -> dict:
    """Decodifica un token JWT y lanza JWTError si no es válido."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def hash_token(token: str) -> str:
    """Genera hash SHA-256 del refresh token para guardar en BD."""
    return sha256(token.encode("utf-8")).hexdigest()


def is_token_type(payload: dict, expected_type: str) -> bool:
    """Valida que el token sea del tipo esperado: access o refresh."""
    return payload.get("type") == expected_type


# --- Agrega estos imports arriba en app/security.py ---
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db, establecer_contexto_tenant
from app.models.usuario import Usuario
# -----------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Usuario:
    """
    Valida el token JWT y retorna el objeto Usuario desde la BD.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if not is_token_type(payload, "access"):
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise credentials_exception

    establecer_contexto_tenant(db, user)
    return user
