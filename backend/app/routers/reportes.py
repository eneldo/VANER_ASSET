# ============================================================
# ROUTER: Reportes PRO
# Proyecto: SGA PRO
# Ruta base: /reportes
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.equipo import Equipo
from app.models.mantenimiento import Mantenimiento
from app.models.tecnico import Tecnico
from app.models.auditoria import AuditoriaSistema

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/resumen")
def resumen_general(db: Session = Depends(get_db)):
    total_empresas = db.query(func.count(Empresa.id)).scalar() or 0
    total_sedes = db.query(func.count(Sede.id)).scalar() or 0
    total_equipos = db.query(func.count(Equipo.id)).scalar() or 0
    total_mantenimientos = db.query(func.count(Mantenimiento.id)).scalar() or 0
    total_tecnicos = db.query(func.count(Tecnico.id)).scalar() or 0
    total_auditoria = db.query(func.count(AuditoriaSistema.id)).scalar() or 0

    return {
        "empresas": total_empresas,
        "sedes": total_sedes,
        "equipos": total_equipos,
        "mantenimientos": total_mantenimientos,
        "tecnicos": total_tecnicos,
        "auditoria": total_auditoria,
    }


@router.get("/mantenimientos-por-estado")
def mantenimientos_por_estado(db: Session = Depends(get_db)):
    data = (
        db.query(
            Mantenimiento.estado.label("estado"),
            func.count(Mantenimiento.id).label("total"),
        )
        .group_by(Mantenimiento.estado)
        .all()
    )

    return [{"estado": item.estado or "SIN_ESTADO", "total": item.total} for item in data]


@router.get("/equipos-por-estado")
def equipos_por_estado(db: Session = Depends(get_db)):
    data = (
        db.query(
            Equipo.estado.label("estado"),
            func.count(Equipo.id).label("total"),
        )
        .group_by(Equipo.estado)
        .all()
    )

    return [{"estado": item.estado or "SIN_ESTADO", "total": item.total} for item in data]


@router.get("/auditoria-reciente")
def auditoria_reciente(db: Session = Depends(get_db)):
    registros = (
        db.query(AuditoriaSistema)
        .order_by(AuditoriaSistema.fecha.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "id": str(r.id),
            "usuario": r.usuario_nombre,
            "rol": r.usuario_rol,
            "modulo": r.modulo,
            "accion": r.accion,
            "descripcion": r.descripcion,
            "fecha": r.fecha,
        }
        for r in registros
    ]