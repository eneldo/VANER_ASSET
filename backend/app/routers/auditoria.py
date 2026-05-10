# ============================================================
# ROUTER: Auditoría del Sistema
# Proyecto: SGA PRO
# Ruta base: /auditoria
# ============================================================

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.auditoria import AuditoriaSistema
from app.schemas.auditoria_schema import AuditoriaCreate, AuditoriaOut

router = APIRouter(prefix="/auditoria", tags=["Auditoría"])


# ============================================================
# Helper reutilizable para registrar auditoría desde otros routers
# ============================================================
def registrar_auditoria(
    db: Session,
    modulo: str,
    accion: str,
    descripcion: str = None,
    usuario_id=None,
    usuario_nombre: str = None,
    usuario_rol: str = None,
    entidad: str = None,
    entidad_id=None,
    request: Request = None,
):
    ip_origen = None
    user_agent = None

    if request:
        ip_origen = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    registro = AuditoriaSistema(
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
        usuario_rol=usuario_rol,
        modulo=modulo,
        accion=accion,
        descripcion=descripcion,
        entidad=entidad,
        entidad_id=entidad_id,
        ip_origen=ip_origen,
        user_agent=user_agent,
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    return registro


# ============================================================
# Crear registro manual de auditoría
# ============================================================
@router.post("/", response_model=AuditoriaOut)
def crear_auditoria(data: AuditoriaCreate, db: Session = Depends(get_db)):
    registro = AuditoriaSistema(**data.dict())
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


# ============================================================
# Listar auditoría con filtros PRO
# ============================================================
@router.get("/", response_model=list[AuditoriaOut])
def listar_auditoria(
    db: Session = Depends(get_db),
    modulo: Optional[str] = Query(None),
    accion: Optional[str] = Query(None),
    usuario: Optional[str] = Query(None),
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    query = db.query(AuditoriaSistema)

    if modulo:
        query = query.filter(AuditoriaSistema.modulo.ilike(f"%{modulo}%"))

    if accion:
        query = query.filter(AuditoriaSistema.accion.ilike(f"%{accion}%"))

    if usuario:
        query = query.filter(AuditoriaSistema.usuario_nombre.ilike(f"%{usuario}%"))

    if desde:
        query = query.filter(AuditoriaSistema.fecha >= desde)

    if hasta:
        query = query.filter(AuditoriaSistema.fecha <= hasta)

    return query.order_by(desc(AuditoriaSistema.fecha)).limit(limit).all()


# ============================================================
# Obtener detalle por ID
# ============================================================
@router.get("/{auditoria_id}", response_model=AuditoriaOut)
def obtener_auditoria(auditoria_id: UUID, db: Session = Depends(get_db)):
    return db.query(AuditoriaSistema).filter(AuditoriaSistema.id == auditoria_id).first()