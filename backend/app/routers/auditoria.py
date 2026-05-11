# ============================================================
# FASE 30 - ROUTER FASTAPI: AUDITORÍA PRO AVANZADA
# Archivo: backend/app/routers/auditoria.py
# Prefijo: /auditoria
# Objetivo:
#   Consultar, filtrar, crear y exportar eventos de auditoría.
#   Este router sirve para trazabilidad del sistema SGA SaaS.
# ============================================================

from datetime import datetime, date, time
from io import StringIO
import csv
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, Request
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auditoria_evento import AuditoriaEvento
from app.schemas.auditoria_schema import (
    AuditoriaEventoCreate,
    AuditoriaEventoOut,
    AuditoriaResumenOut,
)

router = APIRouter(prefix="/auditoria", tags=["Auditoría PRO"])


# ============================================================
# HELPER: registrar eventos desde otros routers
# Uso recomendado en otros módulos:
#   from app.routers.auditoria import registrar_evento_auditoria
#   registrar_evento_auditoria(db, modulo="Equipos", accion="CREAR", ...)
# ============================================================
def registrar_evento_auditoria(
    db: Session,
    modulo: str,
    accion: str,
    descripcion: str = None,
    usuario_id: UUID = None,
    usuario_nombre: str = None,
    usuario_rol: str = None,
    empresa_id: UUID = None,
    entidad: str = None,
    entidad_id: str = None,
    nivel: str = "INFO",
    metadata: dict = None,
    request: Request = None,
):
    """Registra un evento de auditoría sin romper el flujo principal."""

    try:
        ip_origen = None
        user_agent = None

        if request:
            ip_origen = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        evento = AuditoriaEvento(
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre,
            usuario_rol=usuario_rol,
            empresa_id=empresa_id,
            modulo=modulo,
            accion=accion,
            entidad=entidad,
            entidad_id=str(entidad_id) if entidad_id else None,
            descripcion=descripcion,
            ip_origen=ip_origen,
            user_agent=user_agent,
            nivel=nivel,
            metadata=metadata,
        )
        db.add(evento)
        db.commit()
        db.refresh(evento)
        return evento
    except Exception:
        # Importante: la auditoría no debe tumbar la operación principal.
        db.rollback()
        return None


@router.post("/", response_model=AuditoriaEventoOut)
def crear_evento_auditoria(
    payload: AuditoriaEventoCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Crea un evento manual de auditoría."""

    evento = AuditoriaEvento(**payload.model_dump())

    # Si no se envían datos técnicos, se toman desde la petición actual.
    if not evento.ip_origen and request.client:
        evento.ip_origen = request.client.host
    if not evento.user_agent:
        evento.user_agent = request.headers.get("user-agent")

    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


@router.get("/", response_model=list[AuditoriaEventoOut])
def listar_eventos_auditoria(
    db: Session = Depends(get_db),
    modulo: Optional[str] = Query(None),
    accion: Optional[str] = Query(None),
    nivel: Optional[str] = Query(None),
    usuario: Optional[str] = Query(None, description="Busca por nombre de usuario"),
    empresa_id: Optional[UUID] = Query(None),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Lista eventos con filtros profesionales."""

    query = db.query(AuditoriaEvento)

    if modulo:
        query = query.filter(AuditoriaEvento.modulo.ilike(f"%{modulo}%"))
    if accion:
        query = query.filter(AuditoriaEvento.accion.ilike(f"%{accion}%"))
    if nivel:
        query = query.filter(AuditoriaEvento.nivel == nivel.upper())
    if usuario:
        query = query.filter(AuditoriaEvento.usuario_nombre.ilike(f"%{usuario}%"))
    if empresa_id:
        query = query.filter(AuditoriaEvento.empresa_id == empresa_id)
    if fecha_inicio:
        query = query.filter(AuditoriaEvento.created_at >= datetime.combine(fecha_inicio, time.min))
    if fecha_fin:
        query = query.filter(AuditoriaEvento.created_at <= datetime.combine(fecha_fin, time.max))

    return query.order_by(desc(AuditoriaEvento.created_at)).offset(offset).limit(limit).all()


@router.get("/resumen", response_model=AuditoriaResumenOut)
def resumen_auditoria(db: Session = Depends(get_db)):
    """Devuelve métricas rápidas para tarjetas y gráficas del frontend."""

    inicio_hoy = datetime.combine(date.today(), time.min)

    total_eventos = db.query(func.count(AuditoriaEvento.id)).scalar() or 0
    eventos_hoy = db.query(func.count(AuditoriaEvento.id)).filter(AuditoriaEvento.created_at >= inicio_hoy).scalar() or 0
    eventos_warning = db.query(func.count(AuditoriaEvento.id)).filter(AuditoriaEvento.nivel == "WARNING").scalar() or 0
    eventos_error = db.query(func.count(AuditoriaEvento.id)).filter(AuditoriaEvento.nivel == "ERROR").scalar() or 0
    eventos_security = db.query(func.count(AuditoriaEvento.id)).filter(AuditoriaEvento.nivel == "SECURITY").scalar() or 0

    modulos = (
        db.query(AuditoriaEvento.modulo, func.count(AuditoriaEvento.id).label("total"))
        .group_by(AuditoriaEvento.modulo)
        .order_by(desc("total"))
        .limit(10)
        .all()
    )

    acciones = (
        db.query(AuditoriaEvento.accion, func.count(AuditoriaEvento.id).label("total"))
        .group_by(AuditoriaEvento.accion)
        .order_by(desc("total"))
        .limit(10)
        .all()
    )

    return {
        "total_eventos": total_eventos,
        "eventos_hoy": eventos_hoy,
        "eventos_warning": eventos_warning,
        "eventos_error": eventos_error,
        "eventos_security": eventos_security,
        "modulos": [{"nombre": item[0], "total": item[1]} for item in modulos],
        "acciones": [{"nombre": item[0], "total": item[1]} for item in acciones],
    }


@router.get("/exportar/csv")
def exportar_auditoria_csv(
    db: Session = Depends(get_db),
    modulo: Optional[str] = Query(None),
    nivel: Optional[str] = Query(None),
):
    """Exporta auditoría a CSV para análisis o soporte técnico."""

    query = db.query(AuditoriaEvento)
    if modulo:
        query = query.filter(AuditoriaEvento.modulo.ilike(f"%{modulo}%"))
    if nivel:
        query = query.filter(AuditoriaEvento.nivel == nivel.upper())

    eventos = query.order_by(desc(AuditoriaEvento.created_at)).limit(5000).all()

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "fecha", "nivel", "modulo", "accion", "usuario", "rol",
        "entidad", "entidad_id", "descripcion", "ip_origen"
    ])

    for e in eventos:
        writer.writerow([
            e.created_at, e.nivel, e.modulo, e.accion, e.usuario_nombre,
            e.usuario_rol, e.entidad, e.entidad_id, e.descripcion, e.ip_origen
        ])

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=auditoria_sga_pro.csv"},
    )
