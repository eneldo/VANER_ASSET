# =========================================================
# FASE 31.3 - SERVICIO DE LOGS DE SEGURIDAD
# Archivo: backend/app/services/security_logger.py
# Objetivo:
#   Centralizar el registro de auditoría de seguridad sin romper endpoints.
#   Si el log falla, no debe tumbar la operación principal del sistema.
# =========================================================

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.security_event import SecurityEvent


def get_client_ip(request) -> Optional[str]:
    """Obtiene IP considerando proxy inverso Nginx/Traefik."""
    if not request:
        return None
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def registrar_evento_seguridad(
    db: Session,
    *,
    request=None,
    usuario_id=None,
    usuario_email: Optional[str] = None,
    rol: Optional[str] = None,
    empresa_id=None,
    evento: str,
    modulo: Optional[str] = None,
    permitido: bool = True,
    detalle: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Registra evento en seguridad_eventos de forma tolerante a fallos."""
    try:
        registro = SecurityEvent(
            usuario_id=usuario_id,
            usuario_email=usuario_email,
            rol=rol,
            empresa_id=empresa_id,
            evento=evento,
            modulo=modulo,
            metodo=request.method if request else None,
            ruta=str(request.url.path) if request else None,
            ip_origen=get_client_ip(request),
            user_agent=request.headers.get("User-Agent") if request else None,
            request_id=getattr(request.state, "request_id", None) if request else None,
            permitido=permitido,
            detalle=detalle,
            extra=extra,
        )
        db.add(registro)
        db.commit()
    except Exception:
        db.rollback()
