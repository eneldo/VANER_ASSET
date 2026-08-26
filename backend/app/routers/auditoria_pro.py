# ============================================================
# ROUTER AUDITORÍA PRO
# Archivo: backend/app/routers/auditoria_pro.py
#
# Soluciona:
# - RecursionError en FastAPI jsonable_encoder.
# - No retorna modelos SQLAlchemy directos.
# - Devuelve diccionarios planos seguros.
# ============================================================

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.auditoria_pro import AuditoriaProEvento
from app.schemas.auditoria_schema import (
    AuditoriaEventosResponse,
    AuditoriaResumenResponse,
)

router = APIRouter(
    prefix="/auditoria-pro",
    tags=["Auditoría PRO"],
)


# ============================================================
# SERIALIZADOR SEGURO
# ============================================================

def serializar_evento(evento: AuditoriaProEvento):
    """
    Convierte un evento SQLAlchemy a diccionario plano.
    Evita relaciones circulares y RecursionError.
    """

    return {
        "id": evento.id,
        "usuario_id": evento.usuario_id,
        "usuario_email": evento.usuario_email,
        "usuario_nombre": evento.usuario_nombre,
        "rol": evento.rol,
        "empresa_id": evento.empresa_id,
        "modulo": evento.modulo,
        "accion": evento.accion,
        "recurso_tipo": evento.recurso_tipo,
        "recurso_id": evento.recurso_id,
        "metodo": evento.metodo,
        "ruta": evento.ruta,
        "status_code": evento.status_code,
        "ip_origen": evento.ip_origen,
        "user_agent": evento.user_agent,
        "request_id": evento.request_id,
        "permitido": evento.permitido,
        "severidad": evento.severidad,
        "detalle": evento.detalle,
        "datos_extra": evento.datos_extra,
        "creado_en": evento.creado_en,
    }


# ============================================================
# LISTAR EVENTOS
# GET /auditoria-pro/eventos
# ============================================================

@router.get("/eventos", response_model=AuditoriaEventosResponse)
def listar_eventos(
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    modulo: Optional[str] = Query(None),
    accion: Optional[str] = Query(None),
    usuario_email: Optional[str] = Query(None),
    ruta: Optional[str] = Query(None),
    severidad: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(AuditoriaProEvento)

    if modulo:
        query = query.filter(AuditoriaProEvento.modulo.ilike(f"%{modulo}%"))

    if accion:
        query = query.filter(AuditoriaProEvento.accion.ilike(f"%{accion}%"))

    if usuario_email:
        query = query.filter(
            AuditoriaProEvento.usuario_email.ilike(f"%{usuario_email}%")
        )

    if ruta:
        query = query.filter(AuditoriaProEvento.ruta.ilike(f"%{ruta}%"))

    if severidad:
        query = query.filter(AuditoriaProEvento.severidad == severidad)

    total = query.count()

    eventos = (
        query.order_by(AuditoriaProEvento.creado_en.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "eventos": [serializar_evento(e) for e in eventos],
    }


# ============================================================
# RESUMEN AUDITORÍA
# GET /auditoria-pro/resumen
# ============================================================

@router.get("/resumen", response_model=AuditoriaResumenResponse)
def resumen_auditoria(db: Session = Depends(get_db)):
    total_eventos = db.query(AuditoriaProEvento).count()

    permitidos = (
        db.query(AuditoriaProEvento)
        .filter(AuditoriaProEvento.permitido.is_(True))
        .count()
    )

    denegados = (
        db.query(AuditoriaProEvento)
        .filter(AuditoriaProEvento.permitido.is_(False))
        .count()
    )

    errores = (
        db.query(AuditoriaProEvento)
        .filter(AuditoriaProEvento.status_code >= 400)
        .count()
    )

    return {
        "total_eventos": total_eventos,
        "permitidos": permitidos,
        "denegados": denegados,
        "errores": errores,
    }


# ============================================================
# DETALLE EVENTO
# GET /auditoria-pro/eventos/{evento_id}
# ============================================================

@router.get("/eventos/{evento_id}")
def detalle_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
):
    evento = (
        db.query(AuditoriaProEvento)
        .filter(AuditoriaProEvento.id == evento_id)
        .first()
    )

    if not evento:
        return {"detail": "Evento no encontrado"}

    return serializar_evento(evento)


# ============================================================
# LIMPIEZA DE AUDITORÍA
# POST /auditoria-pro/limpiar?dias=90
# ============================================================

@router.post("/limpiar")
def limpiar_auditoria_antigua(
    dias: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db),
):
    """Elimina eventos de auditoría más antiguos que N días."""
    from datetime import datetime, timedelta, timezone
    from app.models.security_event import SecurityEvent

    limite = datetime.now(timezone.utc) - timedelta(days=dias)

    eliminados_auditoria = (
        db.query(AuditoriaProEvento)
        .filter(AuditoriaProEvento.creado_en < limite)
        .delete()
    )

    eliminados_seguridad = (
        db.query(SecurityEvent)
        .filter(SecurityEvent.creado_en < limite)
        .delete()
    )

    db.commit()

    return {
        "ok": True,
        "dias_retencion": dias,
        "eventos_auditoria_eliminados": eliminados_auditoria,
        "eventos_seguridad_eliminados": eliminados_seguridad,
    }