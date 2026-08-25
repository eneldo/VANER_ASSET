# =========================================================
# SERVICIO RECUPERACIÓN DE CONTRASEÑA PRO - FASE 31.7
# Archivo: backend/app/services/password_reset_service.py
# =========================================================
# Funciones centrales:
#   - generar token seguro,
#   - guardar hash del token,
#   - validar expiración,
#   - enviar enlace por email si hay SMTP configurado.
# =========================================================

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import quote

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.password_reset import PasswordResetToken
from app.models.refresh_token import RefreshToken
from app.models.usuario import Usuario
from app.config import settings
from app.product import PRODUCT_NAME
from app.services.smtp_inteligente_service import enviar_correo_smtp


def generar_token_plano() -> str:
    """Genera un token URL-safe suficientemente largo."""
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    """Convierte el token plano en hash SHA-256 para guardarlo seguro."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_client_ip(request: Request) -> str:
    """Obtiene IP real cuando hay proxy o IP directa en desarrollo."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def crear_token_recuperacion(
    db: Session,
    usuario: Usuario,
    request: Request,
    minutos_expiracion: int = 30,
) -> tuple[str, PasswordResetToken]:
    """Crea token temporal y retorna token plano + registro DB."""
    ahora = datetime.utcnow()
    db.query(PasswordResetToken).filter(
        PasswordResetToken.usuario_id == usuario.id,
        PasswordResetToken.usado.is_(False),
    ).update(
        {
            PasswordResetToken.usado: True,
            PasswordResetToken.usado_en: ahora,
        },
        synchronize_session=False,
    )

    token = generar_token_plano()
    token_hash = hash_token(token)

    registro = PasswordResetToken(
        usuario_id=usuario.id,
        email=usuario.email,
        token_hash=token_hash,
        expira_en=datetime.utcnow() + timedelta(minutes=minutos_expiracion),
        ip_solicitud=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    return token, registro


def buscar_token_valido(db: Session, token: str) -> Optional[PasswordResetToken]:
    """Busca token no usado y no expirado."""
    token_hash = hash_token(token)
    return (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.usado.is_(False),
            PasswordResetToken.expira_en > datetime.utcnow(),
        )
        .first()
    )


def marcar_token_usado(
    db: Session,
    registro: PasswordResetToken,
    *,
    commit: bool = True,
) -> None:
    """Marca el token como usado para evitar reutilización."""
    registro.usado = True
    registro.usado_en = datetime.utcnow()
    if commit:
        db.commit()

def revocar_sesiones_usuario(db: Session, usuario_id) -> int:
    """Revoca todas las sesiones renovables activas del usuario."""
    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.usuario_id == usuario_id,
            RefreshToken.revoked_at.is_(None),
        )
        .update(
            {RefreshToken.revoked_at: datetime.utcnow()},
            synchronize_session=False,
        )
    )

def invalidar_tokens_recuperacion_usuario(db: Session, usuario_id) -> int:
    """Invalida cualquier token de recuperación todavía activo."""
    ahora = datetime.utcnow()
    return (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.usuario_id == usuario_id,
            PasswordResetToken.usado.is_(False),
        )
        .update(
            {
                PasswordResetToken.usado: True,
                PasswordResetToken.usado_en: ahora,
            },
            synchronize_session=False,
        )
    )


def construir_reset_url(token: str) -> str:
    """Construye URL con fragmento; el token no viaja al servidor web."""
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    return f"{frontend_url}/reset-password#token={quote(token, safe='')}"


def enviar_email_recuperacion(db: Session, destinatario: str, reset_url: str) -> None:
    mensaje = (
        "Recibimos una solicitud para recuperar tu contraseña. "
        "El enlace vence en 30 minutos. Si no solicitaste el cambio, ignora este mensaje."
    )
    html = (
        "<p>Recibimos una solicitud para recuperar tu contraseña.</p>"
        f'<p><a href="{reset_url}">Crear una nueva contraseña</a></p>'
        "<p>El enlace vence en 30 minutos. Si no solicitaste el cambio, ignora este mensaje.</p>"
    )
    enviar_correo_smtp(
        db,
        destinatario=destinatario,
        asunto=f"Recuperación de contraseña - {PRODUCT_NAME}",
        mensaje=mensaje,
        plantilla="password_reset",
        html=html,
    )
