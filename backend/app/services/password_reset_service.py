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
import os
import secrets
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.password_reset import PasswordResetToken
from app.models.usuario import Usuario


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
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    return f"{frontend_url}/reset-password?token={token}"


def enviar_email_recuperacion(destinatario: str, reset_url: str) -> None:
    """
    Envía email si SMTP está configurado.
    En desarrollo, si no hay SMTP, imprime el enlace en consola del backend.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "no-reply@sga.local")

    if not smtp_host or not smtp_user or not smtp_password:
        print("\n=========================================================")
        print("FASE 31.7 - ENLACE DE RECUPERACIÓN EN MODO DESARROLLO")
        print(f"Email: {destinatario}")
        print(f"URL:   {reset_url}")
        print("Configura SMTP_HOST, SMTP_USER y SMTP_PASSWORD para envío real.")
        print("=========================================================\n")
        return

    msg = EmailMessage()
    msg["Subject"] = "Recuperación de contraseña - SGA PRO"
    msg["From"] = smtp_from
    msg["To"] = destinatario
    msg.set_content(
        f"""
Hola,

Recibimos una solicitud para recuperar tu contraseña en SGA PRO.

Ingresa al siguiente enlace para crear una nueva contraseña:
{reset_url}

Este enlace vence en 30 minutos. Si no solicitaste este cambio, ignora este mensaje.

SGA PRO - Plataforma empresarial SaaS
""".strip()
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
