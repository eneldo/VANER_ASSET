# =========================================================
# ROUTER AUDITORÍA Y MONITOREO PRO SAAS
# Archivo: backend/app/routers/auditoria_pro.py
# =========================================================
# Endpoints administrativos para consultar:
# - eventos de auditoría,
# - resumen de seguridad,
# - actividad reciente,
# - actividad sospechosa.
# =========================================================

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auditoria_pro import AuditoriaProEvento
from app.routers.auth import obtener_usuario_actual
from app.services.audit_service import registrar_auditoria

router = APIRouter(prefix="/auditoria-pro", tags=["Auditoría PRO"])


# =========================================================
# HELPERS
# =========================================================

def _es_admin(usuario) -> bool:
    rol = (getattr(usuario, "rol", "") or "").upper()
    return rol in ("ADMIN", "COORDINADOR")


def _validar_admin(usuario):
    if not _es_admin(usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para consultar auditoría.",
        )


def _evento_to_dict(e: AuditoriaProEvento) -> dict:
    return {
        "id": str(e.id),
        "usuario_id": str(e.usuario_id) if e.usuario_id else None,
        "usuario_email": e.usuario_email,
        "usuario_nombre": e.usuario_nombre,
        "rol": e.rol,
        "empresa_id": str(e.empresa_id) if e.empresa_id else None,
        "modulo": e.modulo,
        "accion": e.accion,
        "recurso_tipo": e.recurso_tipo,
        "recurso_id": e.recurso_id,
        "metodo": e.metodo,
        "ruta": e.ruta,
        "status_code": e.status_code,
        "ip_origen": e.ip_origen,
        "user_agent": e.user_agent,
        "request_id": e.request_id,
        "permitido": e.permitido,
        "severidad": e.severidad,
        "detalle": e.detalle,
        "metadata": e.metadata,
        "creado_en": e.creado_en.isoformat() if e.creado_en else None,
    }


# =========================================================
# RESUMEN KPI
# =========================================================

@router.get("/resumen")
def resumen_auditoria(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
):
    """KPIs principales de auditoría y monitoreo."""
    _validar_admin(usuario_actual)

    ahora = datetime.utcnow()
    desde_24h = ahora - timedelta(hours=24)
    desde_7d = ahora - timedelta(days=7)

    total = db.query(func.count(AuditoriaProEvento.id)).scalar() or 0
    eventos_24h = db.query(func.count(AuditoriaProEvento.id)).filter(AuditoriaProEvento.creado_en >= desde_24h).scalar() or 0
    eventos_7d = db.query(func.count(AuditoriaProEvento.id)).filter(AuditoriaProEvento.creado_en >= desde_7d).scalar() or 0
    denegados = db.query(func.count(AuditoriaProEvento.id)).filter(AuditoriaProEvento.permitido == False).scalar() or 0
    criticos = db.query(func.count(AuditoriaProEvento.id)).filter(AuditoriaProEvento.severidad.in_(["ALTA", "CRITICA"])).scalar() or 0
    usuarios_activos = db.query(func.count(func.distinct(AuditoriaProEvento.usuario_id))).filter(AuditoriaProEvento.usuario_id.isnot(None)).scalar() or 0
    ips = db.query(func.count(func.distinct(AuditoriaProEvento.ip_origen))).filter(AuditoriaProEvento.ip_origen.isnot(None)).scalar() or 0

    por_severidad = dict(
        db.query(AuditoriaProEvento.severidad, func.count(AuditoriaProEvento.id))
        .group_by(AuditoriaProEvento.severidad)
        .all()
    )

    por_modulo = [
        {"modulo": modulo or "SIN_MODULO", "total": total_modulo}
        for modulo, total_modulo in db.query(AuditoriaProEvento.modulo, func.count(AuditoriaProEvento.id))
        .group_by(AuditoriaProEvento.modulo)
        .order_by(func.count(AuditoriaProEvento.id).desc())
        .limit(10)
        .all()
    ]

    return {
        "total_eventos": total,
        "eventos_24h": eventos_24h,
        "eventos_7d": eventos_7d,
        "eventos_denegados": denegados,
        "eventos_criticos": criticos,
        "usuarios_activos": usuarios_activos,
        "ips_detectadas": ips,
        "por_severidad": por_severidad,
        "por_modulo": por_modulo,
    }


# =========================================================
# LISTADO PAGINADO Y FILTRADO
# =========================================================

@router.get("/eventos")
def listar_eventos(
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
    q: Optional[str] = Query(None),
    modulo: Optional[str] = Query(None),
    accion: Optional[str] = Query(None),
    severidad: Optional[str] = Query(None),
    permitido: Optional[bool] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Consulta eventos con filtros para el dashboard PRO."""
    _validar_admin(usuario_actual)

    query = db.query(AuditoriaProEvento)
    filtros = []

    if q:
        like = f"%{q.strip()}%"
        filtros.append(
            or_(
                AuditoriaProEvento.usuario_email.ilike(like),
                AuditoriaProEvento.usuario_nombre.ilike(like),
                AuditoriaProEvento.ruta.ilike(like),
                AuditoriaProEvento.detalle.ilike(like),
                AuditoriaProEvento.ip_origen.ilike(like),
                AuditoriaProEvento.request_id.ilike(like),
            )
        )

    if modulo:
        filtros.append(AuditoriaProEvento.modulo == modulo.upper())

    if accion:
        filtros.append(AuditoriaProEvento.accion == accion.upper())

    if severidad:
        filtros.append(AuditoriaProEvento.severidad == severidad.upper())

    if permitido is not None:
        filtros.append(AuditoriaProEvento.permitido == permitido)

    if fecha_desde:
        filtros.append(AuditoriaProEvento.creado_en >= datetime.fromisoformat(fecha_desde))

    if fecha_hasta:
        filtros.append(AuditoriaProEvento.creado_en <= datetime.fromisoformat(fecha_hasta))

    if filtros:
        query = query.filter(and_(*filtros))

    total = query.count()
    eventos = (
        query.order_by(AuditoriaProEvento.creado_en.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    registrar_auditoria(
        db,
        request=request,
        usuario=usuario_actual,
        modulo="AUDITORIA",
        accion="CONSULTAR_EVENTOS",
        severidad="INFO",
        detalle="Consulta de eventos de auditoría PRO.",
        metadata={"total_resultados": total, "limit": limit, "offset": offset},
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [_evento_to_dict(e) for e in eventos],
    }


# =========================================================
# ACTIVIDAD RECIENTE
# =========================================================

@router.get("/actividad-reciente")
def actividad_reciente(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
    limit: int = Query(10, ge=1, le=50),
):
    """Últimos eventos para timeline de monitoreo."""
    _validar_admin(usuario_actual)

    eventos = (
        db.query(AuditoriaProEvento)
        .order_by(AuditoriaProEvento.creado_en.desc())
        .limit(limit)
        .all()
    )

    return [_evento_to_dict(e) for e in eventos]


# =========================================================
# ACTIVIDAD SOSPECHOSA
# =========================================================

@router.get("/sospechosa")
def actividad_sospechosa(
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
):
    """Detecta señales básicas de riesgo operacional."""
    _validar_admin(usuario_actual)

    desde = datetime.utcnow() - timedelta(hours=24)

    ips_fallidas = [
        {"ip_origen": ip, "total": total}
        for ip, total in db.query(AuditoriaProEvento.ip_origen, func.count(AuditoriaProEvento.id))
        .filter(AuditoriaProEvento.creado_en >= desde)
        .filter(AuditoriaProEvento.permitido == False)
        .filter(AuditoriaProEvento.ip_origen.isnot(None))
        .group_by(AuditoriaProEvento.ip_origen)
        .having(func.count(AuditoriaProEvento.id) >= 3)
        .order_by(func.count(AuditoriaProEvento.id).desc())
        .limit(10)
        .all()
    ]

    errores_500 = db.query(func.count(AuditoriaProEvento.id)).filter(
        AuditoriaProEvento.creado_en >= desde,
        AuditoriaProEvento.status_code >= 500,
    ).scalar() or 0

    accesos_denegados = db.query(func.count(AuditoriaProEvento.id)).filter(
        AuditoriaProEvento.creado_en >= desde,
        AuditoriaProEvento.permitido == False,
    ).scalar() or 0

    return {
        "ventana": "24h",
        "ips_con_fallos_repetidos": ips_fallidas,
        "errores_500": errores_500,
        "accesos_denegados": accesos_denegados,
    }


# =========================================================
# REGISTRO MANUAL DE EVENTOS
# =========================================================

@router.post("/registrar")
def registrar_evento_manual(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual=Depends(obtener_usuario_actual),
):
    """Permite registrar eventos desde frontend o módulos especiales."""
    evento = registrar_auditoria(
        db,
        request=request,
        usuario=usuario_actual,
        modulo=payload.get("modulo", "SISTEMA"),
        accion=payload.get("accion", "EVENTO"),
        recurso_tipo=payload.get("recurso_tipo"),
        recurso_id=payload.get("recurso_id"),
        permitido=payload.get("permitido", True),
        severidad=payload.get("severidad", "INFO"),
        detalle=payload.get("detalle"),
        metadata=payload.get("metadata"),
    )

    return {"ok": True, "id": str(evento.id) if evento else None}
