# =========================================================
# SERVICIO DE AUDITORÍA PRO
# Archivo: backend/app/services/audit_service.py
# =========================================================
# Funciones reutilizables para registrar eventos desde:
# - routers,
# - middleware,
# - autenticación,
# - permisos,
# - acciones críticas.
# =========================================================

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.auditoria_pro import AuditoriaProEvento


def get_client_ip(request: Optional[Request]) -> Optional[str]:
    """Obtiene IP real considerando proxy reverso o request directo."""
    if not request:
        return None

    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    return request.client.host if request.client else None


def get_request_id(request: Optional[Request]) -> Optional[str]:
    """Obtiene request_id creado por el middleware de seguridad."""
    if not request:
        return None
    return getattr(request.state, "request_id", None) or request.headers.get("x-request-id")


def _safe_uuid(value: Any) -> Optional[UUID]:
    """Convierte valores compatibles a UUID sin romper auditoría."""
    if not value:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except Exception:
        return None


def registrar_auditoria(
    db: Session,
    *,
    request: Optional[Request] = None,
    usuario: Any = None,
    modulo: str = "SISTEMA",
    accion: str = "EVENTO",
    recurso_tipo: Optional[str] = None,
    recurso_id: Optional[str] = None,
    permitido: bool = True,
    severidad: str = "INFO",
    detalle: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    status_code: Optional[int] = None,
) -> AuditoriaProEvento:
    """
    Registra un evento de auditoría de forma segura.

    Importante:
    - No lanza excepción hacia el usuario final si falla la auditoría.
    - Hace rollback del INSERT de auditoría si se presenta error.
    """
    try:
        evento = AuditoriaProEvento(
            usuario_id=_safe_uuid(getattr(usuario, "id", None)),
            usuario_email=getattr(usuario, "email", None) or getattr(usuario, "username", None),
            usuario_nombre=getattr(usuario, "nombre_completo", None),
            rol=getattr(usuario, "rol", None),
            empresa_id=_safe_uuid(getattr(usuario, "empresa_id", None)),
            modulo=(modulo or "SISTEMA").upper(),
            accion=(accion or "EVENTO").upper(),
            recurso_tipo=recurso_tipo,
            recurso_id=str(recurso_id) if recurso_id else None,
            metodo=request.method if request else None,
            ruta=str(request.url.path) if request else None,
            status_code=status_code,
            ip_origen=get_client_ip(request),
            user_agent=request.headers.get("user-agent") if request else None,
            request_id=get_request_id(request),
            permitido=permitido,
            severidad=(severidad or "INFO").upper(),
            detalle=detalle,
            metadata=metadata,
        )
        db.add(evento)
        db.commit()
        db.refresh(evento)
        return evento
    except Exception:
        db.rollback()
        return None
