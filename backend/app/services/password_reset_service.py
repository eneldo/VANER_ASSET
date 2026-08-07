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

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.password_reset import PasswordResetToken
from app.models.usuario import Usuario
from app.config import settings
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


def marcar_token_usado(db: Session, registro: PasswordResetToken) -> None:
    """Marca el token como usado para evitar reutilización."""
    registro.usado = True
    registro.usado_en = datetime.utcnow()
    db.commit()


def construir_reset_url(token: str) -> str:
    """Construye URL frontend de recuperación."""
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    return f"{frontend_url}/reset-password?token={token}"


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
        asunto="Recuperación de contraseña - SGAHolding",
        mensaje=mensaje,
        plantilla="password_reset",
        html=html,
    )
