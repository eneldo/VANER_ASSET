from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Optional
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.config import settings


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Genera un hash PBKDF2-SHA256 para una contraseña."""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Comprueba una contraseña contra su hash almacenado."""
    return pwd_context.verify(password, password_hash)


def _minutes(value: Any, default: int) -> int:
    """Convierte un valor de configuración a entero de forma segura."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_access_token_minutes() -> int:
    return _minutes(getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30), 30)


def get_refresh_token_minutes() -> int:
    days = _minutes(getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7), 7)
    return max(days, 1) * 60 * 24


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    payload = data.copy()
    expire = utc_now() + (
        expires_delta or timedelta(minutes=get_access_token_minutes())
    )
    payload.update({"exp": expire, "type": "access", "jti": str(uuid4())})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> tuple[str, str, datetime]:
    payload = data.copy()
    jti = str(uuid4())
    expire = utc_now() + (
        expires_delta or timedelta(minutes=get_refresh_token_minutes())
    )
    payload.update({"exp": expire, "type": "refresh", "jti": jti})
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti, expire


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def is_token_type(payload: dict, expected_type: str) -> bool:
    return payload.get("type") == expected_type
