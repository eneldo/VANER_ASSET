# =========================================================
# ROUTER AUTH - VANER ASSET
# Archivo: backend/app/routers/auth.py
#
# FIX PRODUCCIÓN:
# - Login no sensible a mayúsculas/minúsculas.
# - username/email se buscan con LOWER().
# - No bloquea globalmente por IP.
# - Bloqueo por usuario + IP.
# =========================================================

from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import or_, text, func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.refresh_token import RefreshToken
from app.models.usuario import Usuario
from app.services.coordinador_empresas import aplicar_empresa_activa, ids_empresas_autorizadas
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RefreshResponse, TokenResponse
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_access_token_minutes,
    hash_token,
    utc_now,
    verify_password,
    needs_upgrade,
    hash_password,
)
from app.services.security_logger import registrar_evento_seguridad, get_client_ip

router = APIRouter(prefix="/auth", tags=["Autenticación"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        path=settings.REFRESH_COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path=settings.REFRESH_COOKIE_PATH,
        secure=settings.REFRESH_COOKIE_SECURE,
        httponly=True,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
    )


def _refresh_token_from_request(data: RefreshRequest | LogoutRequest, request: Request) -> str | None:
    return data.refresh_token or request.cookies.get(settings.REFRESH_COOKIE_NAME)


def _guardar_refresh_token(
    db: Session,
    *,
    usuario: Usuario,
    token: str,
    jti: str,
    expires_at: datetime,
    request: Request,
) -> RefreshToken:
    registro = RefreshToken(
        usuario_id=usuario.id,
        token_hash=hash_token(token),
        jti=jti,
        expires_at=expires_at,
        user_agent=request.headers.get("User-Agent"),
        ip_address=get_client_ip(request),
    )
    db.add(registro)
    return registro


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    empresa_activa: str | None = Header(default=None, alias="X-Empresa-Activa"),
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

    aplicar_empresa_activa(db, usuario, empresa_activa)
    return usuario


get_current_user = obtener_usuario_actual
get_usuario_actual = obtener_usuario_actual


MAX_LOGIN_FALLIDOS = 5
BLOQUEO_MINUTOS = 15
VENTANA_MINUTOS = 15


def _request_id(request: Request):
    return getattr(request.state, "request_id", None)


def _normalizar_username(username: str) -> str:
    return (username or "").strip().lower()


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
                (id, username, ip_origen, exitoso, motivo, user_agent, request_id,
                 intentos_fallidos, bloqueado_hasta)
            VALUES
                (:id, :username, :ip_origen, :exitoso, :motivo, :user_agent, :request_id,
                 :intentos_fallidos, :bloqueado_hasta)
            """
        ),
        {
            "id": uuid4(),
            "username": _normalizar_username(username),
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
    desde = utc_now() - timedelta(minutes=VENTANA_MINUTOS)

    total = db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM login_intentos
            WHERE exitoso = false
              AND creado_en >= :desde
              AND LOWER(username) = LOWER(:username)
              AND ip_origen = :ip_origen
            """
        ),
        {
            "desde": desde,
            "username": _normalizar_username(username),
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
              AND LOWER(username) = LOWER(:username)
              AND ip_origen = :ip_origen
            """
        ),
        {
            "username": _normalizar_username(username),
            "ip_origen": ip_origen,
        },
    ).scalar()

    return bloqueo


def _minutos_restantes(bloqueo) -> int:
    if not bloqueo:
        return BLOQUEO_MINUTOS

    ahora = utc_now()

    try:
        diferencia = bloqueo.replace(tzinfo=None) - ahora
        minutos = int(diferencia.total_seconds() // 60) + 1
        return max(minutos, 1)
    except Exception:
        return BLOQUEO_MINUTOS


@router.post("/login", response_model=TokenResponse, response_model_exclude_none=True)
def login(data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    username_original = (data.username or "").strip()
    username_normalizado = _normalizar_username(username_original)
    ip_origen = get_client_ip(request)

    bloqueo = _bloqueo_activo(db, username_normalizado, ip_origen)

    if bloqueo:
        minutos = _minutos_restantes(bloqueo)

        registrar_evento_seguridad(
            db,
            request=request,
            usuario_email=username_original,
            evento="LOGIN_BLOQUEADO",
            modulo="AUTH",
            permitido=False,
            detalle=f"Login bloqueado temporalmente por {minutos} minutos",
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos fallidos. Intenta nuevamente en {minutos} minutos.",
        )

    usuario = (
        db.query(Usuario)
        .filter(
            or_(
                func.lower(Usuario.username) == username_normalizado,
                func.lower(Usuario.email) == username_normalizado,
            )
        )
        .first()
    )

    if not usuario:
        fallidos = _contar_fallidos_recientes(db, username_normalizado, ip_origen) + 1

        bloqueado_hasta = (
            utc_now() + timedelta(minutes=BLOQUEO_MINUTOS)
            if fallidos >= MAX_LOGIN_FALLIDOS
            else None
        )

        _registrar_intento_login(
            db,
            request=request,
            username=username_normalizado,
            exitoso=False,
            motivo="USUARIO_NO_EXISTE",
            intentos_fallidos=fallidos,
            bloqueado_hasta=bloqueado_hasta,
        )

        registrar_evento_seguridad(
            db,
            request=request,
            usuario_email=username_original,
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
            username=usuario.username,
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
        fallidos = _contar_fallidos_recientes(db, username_normalizado, ip_origen) + 1

        bloqueado_hasta = (
            utc_now() + timedelta(minutes=BLOQUEO_MINUTOS)
            if fallidos >= MAX_LOGIN_FALLIDOS
            else None
        )

        _registrar_intento_login(
            db,
            request=request,
            username=usuario.username,
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

    # Verificar si la contraseña temporal expiró
    if usuario.temp_password_expires_at and utc_now() > usuario.temp_password_expires_at:
        usuario.debe_cambiar_password = True
        db.commit()
        registrar_evento_seguridad(
            db,
            request=request,
            usuario_id=usuario.id,
            usuario_email=usuario.email,
            rol=usuario.rol,
            empresa_id=usuario.empresa_id,
            evento="PASSWORD_TEMPORARY_EXPIRED",
            modulo="AUTH",
            permitido=False,
            detalle="Contraseña temporal expirada",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu contraseña temporal ha expirado. Contacta al administrador para restablecerla.",
        )

    # Migrar hash de PBKDF2 a Argon2id si es necesario
    if needs_upgrade(usuario.password_hash):
        usuario.password_hash = hash_password(data.password)
        registrar_evento_seguridad(
            db,
            request=request,
            usuario_id=usuario.id,
            usuario_email=usuario.email,
            rol=usuario.rol,
            empresa_id=usuario.empresa_id,
            evento="PASSWORD_HASH_UPGRADED",
            modulo="AUTH",
            permitido=True,
            detalle="Hash migrado de PBKDF2 a Argon2id",
        )
        db.commit()

    access_token = create_access_token(
        _crear_payload_usuario(usuario, tipo="access")
    )

    refresh_token, refresh_jti, refresh_expires_at = create_refresh_token(
        _crear_payload_usuario(usuario, tipo="refresh")
    )

    _guardar_refresh_token(
        db,
        usuario=usuario,
        token=refresh_token,
        jti=refresh_jti,
        expires_at=refresh_expires_at,
        request=request,
    )
    db.commit()
    _set_refresh_cookie(response, refresh_token)

    _registrar_intento_login(
        db,
        request=request,
        username=usuario.username,
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
    empresa_ids = [str(value) for value in ids_empresas_autorizadas(db, usuario)]

    return TokenResponse(
        access_token=access_token,
        refresh_token=None,
        token_type="bearer",
        expires_in=get_access_token_minutes() * 60,
        usuario_id=str(usuario.id),
        nombre_completo=usuario.nombre_completo,
        rol=usuario.rol,
        empresa_id=empresa_id,
        empresa_ids=empresa_ids,
        debe_cambiar_password=usuario.debe_cambiar_password or False,
    )


@router.post("/refresh", response_model=RefreshResponse, response_model_exclude_none=True)
def refresh_token(
    data: RefreshRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    credenciales_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = _refresh_token_from_request(data, request)
        if not token:
            raise credenciales_error

        payload = decode_token(token)

        usuario_id = payload.get("sub")
        tipo = payload.get("type")
        jti = payload.get("jti")

        if not usuario_id or tipo != "refresh" or not jti:
            raise credenciales_error

    except JWTError:
        raise credenciales_error

    ahora = utc_now()
    sesion = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_token(token))
        .with_for_update()
        .first()
    )

    if (
        not sesion
        or sesion.jti != jti
        or sesion.revoked_at is not None
        or sesion.expires_at <= ahora
    ):
        raise credenciales_error

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario or not usuario.activo:
        raise credenciales_error

    nuevo_access_token = create_access_token(
        _crear_payload_usuario(usuario, tipo="access")
    )

    nuevo_refresh_token, nuevo_jti, nueva_expiracion = create_refresh_token(
        _crear_payload_usuario(usuario, tipo="refresh")
    )

    sesion.revoked_at = ahora
    sesion.replaced_by_jti = nuevo_jti
    _guardar_refresh_token(
        db,
        usuario=usuario,
        token=nuevo_refresh_token,
        jti=nuevo_jti,
        expires_at=nueva_expiracion,
        request=request,
    )
    db.commit()
    _set_refresh_cookie(response, nuevo_refresh_token)

    return {
        "access_token": nuevo_access_token,
        "refresh_token": None,
        "token_type": "bearer",
        "expires_in": get_access_token_minutes() * 60,
        "usuario_id": str(usuario.id),
        "nombre_completo": usuario.nombre_completo,
        "rol": usuario.rol,
        "empresa_id": str(usuario.empresa_id) if usuario.empresa_id else None,
        "empresa_ids": [str(value) for value in ids_empresas_autorizadas(db, usuario)],
    }


@router.get("/me")
def auth_me(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    return {
        "usuario_id": str(usuario.id),
        "nombre_completo": usuario.nombre_completo,
        "username": usuario.username,
        "email": usuario.email,
        "rol": usuario.rol,
        "empresa_id": str(usuario.empresa_id) if usuario.empresa_id else None,
        "empresa_ids": [str(value) for value in ids_empresas_autorizadas(db, usuario)],
        "activo": usuario.activo,
    }


@router.post("/logout")
def logout(
    data: LogoutRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    token = _refresh_token_from_request(data, request)

    if token:
        sesion = (
            db.query(RefreshToken)
            .filter(RefreshToken.token_hash == hash_token(token))
            .first()
        )
        if sesion and sesion.revoked_at is None:
            sesion.revoked_at = utc_now()
            db.commit()

    _clear_refresh_cookie(response)
    return {"ok": True, "message": "Sesión cerrada correctamente"}
