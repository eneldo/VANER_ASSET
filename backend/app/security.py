# =========================================================
# SEGURIDAD SGA PRO (VERSIÓN ESTABLE SIN BCRYPT)
# =========================================================

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.config import settings


# 🔥 CAMBIO IMPORTANTE: usamos pbkdf2_sha256
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Encripta contraseña de forma segura.
    """
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica contraseña.
    """
    return pwd_context.verify(password, password_hash)


def create_access_token(data: dict) -> str:
    """
    Crea token JWT.
    """
    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({"exp": expire})

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )