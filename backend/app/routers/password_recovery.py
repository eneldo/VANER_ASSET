# =========================================================
# ROUTER RECUPERACIÓN DE CONTRASEÑA PRO - FASE 31.7
# Archivo: backend/app/routers/password_recovery.py
# =========================================================
# Endpoints:
#   POST /auth/forgot-password
#   POST /auth/reset-password
#   POST /auth/reset-password/validate
# =========================================================

from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.services.password_reset_service import (
    buscar_token_valido,
    construir_reset_url,
    crear_token_recuperacion,
    enviar_email_recuperacion,
    invalidar_tokens_recuperacion_usuario,
    marcar_token_usado,
    revocar_sesiones_usuario,
)
from app.services.security_logger import registrar_evento_seguridad

# Import flexible del hash de contraseña para no romper entre fases.
try:
    from app.security import get_password_hash as hash_password
except ImportError:  # pragma: no cover
    try:
        from app.security import hash_password
    except ImportError:
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        def hash_password(password: str) -> str:
            return pwd_context.hash(password)

router = APIRouter(prefix="/auth", tags=["Recuperación de contraseña"])


class ForgotPasswordRequest(BaseModel):
    """Payload para solicitar recuperación."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Payload para guardar nueva contraseña."""

    token: str = Field(..., min_length=20)
    new_password: str = Field(..., min_length=12, max_length=128)

class ValidateResetTokenRequest(BaseModel):
    """Token enviado en body para evitar exposición en URLs y logs."""

    token: str = Field(..., min_length=20)


@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Solicita recuperación de contraseña.

    Seguridad:
    - Siempre responde OK aunque el email no exista.
    - Evita enumeración de usuarios.
    - Si existe usuario activo, genera token y envía email.
    """
    email = payload.email.strip().lower()

    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == email)
        .first()
    )

    # Respuesta neutra para no revelar si el correo existe.
    respuesta = {
        "message": "Si el correo está registrado, recibirás instrucciones de recuperación.",
    }

    if not usuario or not getattr(usuario, "activo", True):
        return respuesta

    token, registro = crear_token_recuperacion(db, usuario, request)
    reset_url = construir_reset_url(token)
    try:
        enviar_email_recuperacion(db, usuario.email, reset_url)
    except Exception:
        marcar_token_usado(db, registro)

    return respuesta


@router.post("/reset-password/validate")
def validate_reset_token(
    payload: ValidateResetTokenRequest,
    db: Session = Depends(get_db),
):
    """Valida si un token sigue activo antes de mostrar el formulario."""
    registro = buscar_token_valido(db, payload.token)
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace es inválido o expiró.",
        )

    return {"valid": True, "email": registro.email}


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Cambia contraseña usando token válido."""
    registro = buscar_token_valido(db, payload.token)
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace es inválido o expiró.",
        )

    usuario = db.query(Usuario).filter(Usuario.id == registro.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    usuario.password_hash = hash_password(payload.new_password)
    marcar_token_usado(db, registro, commit=False)
    revocar_sesiones_usuario(db, usuario.id)
    invalidar_tokens_recuperacion_usuario(db, usuario.id)
    db.commit()

    registrar_evento_seguridad(
        db,
        request=request,
        usuario_id=usuario.id,
        usuario_email=usuario.email,
        rol=usuario.rol,
        empresa_id=usuario.empresa_id,
        evento="PASSWORD_RESET_COMPLETADO",
        modulo="AUTH",
        permitido=True,
        detalle="Contraseña restablecida y sesiones activas revocadas",
    )

    return {"message": "Contraseña actualizada correctamente."}
