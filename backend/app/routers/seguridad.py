# =========================================================
# FASE 31.3 - ROUTER SEGURIDAD PRO
# Archivo: backend/app/routers/seguridad.py
# Objetivo:
#   Permitir al ADMIN consultar eventos de seguridad, intentos de login
#   y validar el estado del hardening backend.
# =========================================================

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db

router = APIRouter(prefix="/seguridad", tags=["Seguridad PRO"])


@router.get("/health")
def seguridad_health():
    """Verificación rápida de que la Fase 31.3 está cargada."""
    return {
        "fase": "31.3",
        "modulo": "Hardening de Seguridad Backend PRO",
        "estado": "activo",
        "protecciones": [
            "request_id",
            "security_headers",
            "rate_limit",
            "login_lockout",
            "security_events",
        ],
    }


@router.get("/eventos")
def listar_eventos_seguridad(
    db: Session = Depends(get_db),
    limite: int = Query(100, ge=1, le=500),
    evento: Optional[str] = None,
):
    """
    Lista eventos recientes de seguridad.
    Recomendación: en la Fase 31.2 proteger esta ruta con permiso SEGURIDAD_VER_EVENTOS.
    """
    sql = """
        SELECT id, usuario_email, rol, evento, modulo, metodo, ruta,
               ip_origen, permitido, detalle, request_id, creado_en
        FROM seguridad_eventos
        WHERE (:evento IS NULL OR evento = :evento)
        ORDER BY creado_en DESC
        LIMIT :limite
    """
    rows = db.execute(text(sql), {"evento": evento, "limite": limite}).mappings().all()
    return [dict(r) for r in rows]


@router.get("/login-intentos")
def listar_intentos_login(
    db: Session = Depends(get_db),
    limite: int = Query(100, ge=1, le=500),
    username: Optional[str] = None,
):
    """Consulta intentos recientes de login para auditoría de fuerza bruta."""
    sql = """
        SELECT id, username, ip_origen, exitoso, motivo, intentos_fallidos,
               bloqueado_hasta, request_id, creado_en
        FROM login_intentos
        WHERE (:username IS NULL OR username ILIKE :username_like)
        ORDER BY creado_en DESC
        LIMIT :limite
    """
    rows = db.execute(
        text(sql),
        {"username": username, "username_like": f"%{username}%" if username else None, "limite": limite},
    ).mappings().all()
    return [dict(r) for r in rows]
