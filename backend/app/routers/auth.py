# =========================================================
# ROUTER AUTH - FASE 31.4 HARDENING BACKEND PRO
# Archivo: backend/app/routers/auth.py
#
# Incluye:
# - Login seguro
# - JWT access token
# - JWT refresh token
# - Endpoint /auth/refresh
# - Usuario actual
# =========================================================

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse
from app.security import verify_password, create_access_token
from app.services.security_logger import registrar_evento_seguridad, get_client_ip

router = APIRouter(prefix="/auth", tags=["Autenticación"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =========================================================
# SCHEMA REFRESH TOKEN
# =========================================================

class RefreshTokenRequest(BaseModel):
    refresh_token: str


# =========================================================
# CONFIG JWT
# =========================================================

def _jwt_secret_key():
    return getattr(settings, "SECRET_KEY", None) or getattr(settings, "secret_key", None)


def _jwt_algorithm():
    return getattr(settings, "ALGORITHM", None) or getattr(settings, "algorithm", "HS256")


def _crear_payload_usuario(usuario: Usuario, tipo: str = "access"):
    empresa_id = str(usuario.empresa_id) if usuario.empresa_id else None

    return {
        "sub": str(usuario.id),
        "email": usuario.email,
        "username": usuario.username,
        "nombre_completo": usuario.nombre_completo,
        "rol": usuario.rol,
        "empresa_id": empresa_id,
        "type": tipo,
    }


# =========================================================
# USUARIO ACTUAL
# =========================================================

def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credenciales_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            _jwt_secret_key(),
            algorithms=[_jwt_algorithm()],
        )

        usuario_id = payload.get("sub")
        tipo = payload.get("type")

        if not usuario_id:
            raise credenciales_error

        if tipo and tipo != "access":
            raise credenciales_error

    except JWTError:
        raise credenciales_error

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario or not usuario.activo:
        raise credenciales_error

    return usuario


get_current_user = obtener_usuario_actual
get_usuario_actual = obtener_usuario_actual


# =========================================================
# CONFIGURACIÓN BLOQUEO LOGIN
# =========================================================

MAX_LOGIN_FALLIDOS = 5
BLOQUEO_MINUTOS = 15
VENTANA_MINUTOS = 15


def _request_id(request: Request):
    return getattr(request.state, "request_id", None)


def _registrar_intento_login(
    db: Session,
    *,
    request: Request,
    username: str,
    exitoso: bool,
    motivo: str,
    intentos_fallidos: int = 0,
    bloqueado_hasta=None,
):
    db.execute(
        text(
            """
            INSERT INTO login_intentos
                (username, ip_origen, exitoso, motivo, user_agent, request_id,
                 intentos_fallidos, bloqueado_hasta)
            VALUES
                (:username, :ip_origen, :exitoso, :motivo, :user_agent, :request_id,
                 :intentos_fallidos, :bloqueado_hasta)
            """
        ),
        {
            "username": username,
            "ip_origen": get_client_ip(request),
            "exitoso": exitoso,
            "motivo": motivo,
            "user_agent": request.headers.get("User-Agent"),
            "request_id": _request_id(request),
            "intentos_fallidos": intentos_fallidos,
            "bloqueado_hasta": bloqueado_hasta,
        },
    )
    db.commit()


def _contar_fallidos_recientes(db: Session, username: str, ip_origen: str) -> int:
    desde = datetime.utcnow() - timedelta(minutes=VENTANA_MINUTOS)

    total = db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM login_intentos
            WHERE exitoso = false
              AND creado_en >= :desde
              AND (LOWER(username) = LOWER(:username) OR ip_origen = :ip_origen)
            """
        ),
        {
            "desde": desde,
            "username": username,
            "ip_origen": ip_origen,
        },
    ).scalar()

    return int(total or 0)


def _bloqueo_activo(db: Session, username: str, ip_origen: str):
    bloqueo = db.execute(
        text(
            """
            SELECT MAX(bloqueado_hasta)
            FROM login_intentos
            WHERE bloqueado_hasta IS NOT NULL
              AND bloqueado_hasta > NOW()
              AND (LOWER(username) = LOWER(:username) OR ip_origen = :ip_origen)
            """
        ),
        {
            "username": username,
            "ip_origen": ip_origen,
        },
    ).scalar()

    return bloqueo


# =========================================================
# LOGIN
# =========================================================

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    username = data.username.strip()
    ip_origen = get_client_ip(request)

    bloqueo = _bloqueo_activo(db, username, ip_origen)

    if bloqueo:
        registrar_evento_seguridad(
            db,
            request=request,
            usuario_email=username,
            evento="LOGIN_BLOQUEADO",
            modulo="AUTH",
            permitido=False,
            detalle=f"Login bloqueado temporalmente hasta {bloqueo}",
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos fallidos. Intenta nuevamente después de {bloqueo}.",
        )

    usuario = (
        db.query(Usuario)
        .filter(
            or_(
                Usuario.username == username,
                Usuario.email == username,
            )
        )
        .first()
    )

    if not usuario:
        fallidos = _contar_fallidos_recientes(db, username, ip_origen) + 1

        bloqueado_hasta = (
            datetime.utcnow() + timedelta(minutes=BLOQUEO_MINUTOS)
            if fallidos >= MAX_LOGIN_FALLIDOS
            else None
        )

        _registrar_intento_login(
            db,
            request=request,
            username=username,
            exitoso=False,
            motivo="USUARIO_NO_EXISTE",
            intentos_fallidos=fallidos,
            bloqueado_hasta=bloqueado_hasta,
        )

        registrar_evento_seguridad(
            db,
            request=request,
            usuario_email=username,
            evento="LOGIN_FALLIDO",
            modulo="AUTH",
            permitido=False,
            detalle="Usuario no existe",
            extra={"fallidos_recientes": fallidos},
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    if not usuario.activo:
        _registrar_intento_login(
            db,
            request=request,
            username=username,
            exitoso=False,
            motivo="USUARIO_INACTIVO",
        )

        registrar_evento_seguridad(
            db,
            request=request,
            usuario_id=usuario.id,
            usuario_email=usuario.email,
            rol=usuario.rol,
            empresa_id=usuario.empresa_id,
            evento="LOGIN_USUARIO_INACTIVO",
            modulo="AUTH",
            permitido=False,
            detalle="Intento de ingreso con usuario inactivo",
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    if not verify_password(data.password, usuario.password_hash):
        fallidos = _contar_fallidos_recientes(db, username, ip_origen) + 1

        bloqueado_hasta = (
            datetime.utcnow() + timedelta(minutes=BLOQUEO_MINUTOS)
            if fallidos >= MAX_LOGIN_FALLIDOS
            else None
        )

        _registrar_intento_login(
            db,
            request=request,
            username=username,
            exitoso=False,
            motivo="PASSWORD_INCORRECTO",
            intentos_fallidos=fallidos,
            bloqueado_hasta=bloqueado_hasta,
        )

        registrar_evento_seguridad(
            db,
            request=request,
            usuario_id=usuario.id,
            usuario_email=usuario.email,
            rol=usuario.rol,
            empresa_id=usuario.empresa_id,
            evento="LOGIN_FALLIDO",
            modulo="AUTH",
            permitido=False,
            detalle="Contraseña incorrecta",
            extra={
                "fallidos_recientes": fallidos,
                "bloqueado": bool(bloqueado_hasta),
            },
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    access_token = create_access_token(
        _crear_payload_usuario(usuario, tipo="access")
    )

    refresh_token = create_access_token(
        _crear_payload_usuario(usuario, tipo="refresh"),
        expires_delta=timedelta(days=7),
    )

    _registrar_intento_login(
        db,
        request=request,
        username=username,
        exitoso=True,
        motivo="LOGIN_OK",
        intentos_fallidos=0,
    )

    registrar_evento_seguridad(
        db,
        request=request,
        usuario_id=usuario.id,
        usuario_email=usuario.email,
        rol=usuario.rol,
        empresa_id=usuario.empresa_id,
        evento="LOGIN_OK",
        modulo="AUTH",
        permitido=True,
        detalle="Ingreso exitoso al sistema",
    )

    empresa_id = str(usuario.empresa_id) if usuario.empresa_id else None

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600,
        usuario_id=str(usuario.id),
        nombre_completo=usuario.nombre_completo,
        rol=usuario.rol,
        empresa_id=empresa_id,
    )


# =========================================================
# REFRESH TOKEN
# =========================================================

@router.post("/refresh")
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    credenciales_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            data.refresh_token,
            _jwt_secret_key(),
            algorithms=[_jwt_algorithm()],
        )

        usuario_id = payload.get("sub")
        tipo = payload.get("type")

        if not usuario_id or tipo != "refresh":
            raise credenciales_error

    except JWTError:
        raise credenciales_error

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario or not usuario.activo:
        raise credenciales_error

    nuevo_access_token = create_access_token(
        _crear_payload_usuario(usuario, tipo="access")
    )

    nuevo_refresh_token = create_access_token(
        _crear_payload_usuario(usuario, tipo="refresh"),
        expires_delta=timedelta(days=7),
    )

    return {
        "access_token": nuevo_access_token,
        "refresh_token": nuevo_refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "usuario_id": str(usuario.id),
        "nombre_completo": usuario.nombre_completo,
        "rol": usuario.rol,
        "empresa_id": str(usuario.empresa_id) if usuario.empresa_id else None,
    }


# =========================================================
# PERFIL AUTENTICADO
# =========================================================

@router.get("/me")
def auth_me(usuario: Usuario = Depends(obtener_usuario_actual)):
    return {
        "usuario_id": str(usuario.id),
        "nombre_completo": usuario.nombre_completo,
        "username": usuario.username,
        "email": usuario.email,
        "rol": usuario.rol,
        "empresa_id": str(usuario.empresa_id) if usuario.empresa_id else None,
        "activo": usuario.activo,
    }