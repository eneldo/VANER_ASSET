# =========================================================
# SEGURIDAD SGA PRO
# Manejo de contraseñas y token JWT
# =========================================================

from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.config import settings


# Configuración para encriptar contraseñas
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Encripta una contraseña antes de guardarla en BD.
    """
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica si la contraseña ingresada coincide con el hash guardado.
    """
    return pwd_context.verify(password, password_hash)


def create_access_token(data: dict) -> str:
    """
    Crea un token JWT con tiempo de expiración.
    """
    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({"exp": expire})

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token