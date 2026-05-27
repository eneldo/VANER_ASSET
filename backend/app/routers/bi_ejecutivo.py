# ============================================================
# BI EJECUTIVO AVANZADO PRO
# Archivo: backend/app/routers/bi_ejecutivo.py
# Compatible con frontend actual
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.equipo import Equipo
from app.models.usuario import Usuario
from app.models.mantenimiento import Mantenimiento

router = APIRouter(
    prefix="/bi-ejecutivo",
    tags=["BI Ejecutivo PRO"]
)


@router.get("/kpis")
def obtener_kpis(db: Session = Depends(get_db)):
    try:
        return {
            "total_empresas": db.query(Empresa).count(),
            "total_sedes": db.query(Sede).count(),
            "total_equipos": db.query(Equipo).count(),
            "total_usuarios": db.query(Usuario).count(),
            "total_mantenimientos": db.query(Mantenimiento).count(),
        }
    except Exception as e:
        print("ERROR KPI BI:", str(e))
        return {
            "total_empresas": 0,
            "total_sedes": 0,
            "total_equipos": 0,
            "total_usuarios": 0,
            "total_mantenimientos": 0,
        }


@router.get("/mantenimientos-estados")
def mantenimientos_estados(db: Session = Depends(get_db)):
    try:
        resultados = (
            db.query(
                Mantenimiento.estado,
                func.count(Mantenimiento.id)
            )
            .group_by(Mantenimiento.estado)
            .all()
        )

        return [
            {
                "estado": r[0] or "SIN_ESTADO",
                "total": r[1],
            }
            for r in resultados
        ]
    except Exception as e:
        print("ERROR mantenimientos_estados BI:", str(e))
        return []


@router.get("/mantenimientos-estado")
def mantenimientos_estado_alias(db: Session = Depends(get_db)):
    return mantenimientos_estados(db)


@router.get("/equipos-empresa")
def equipos_empresa(db: Session = Depends(get_db)):
    try:
        resultados = (
            db.query(
                Empresa.nombre,
                func.count(Equipo.id)
            )
            .outerjoin(
                Equipo,
                Equipo.empresa_id == Empresa.id
            )
            .group_by(Empresa.nombre)
            .all()
        )

        return [
            {
                "empresa": r[0],
                "equipos": r[1],
                "total": r[1],
            }
            for r in resultados
        ]
    except Exception as e:
        print("ERROR equipos_empresa BI:", str(e))
        return []


@router.get("/costos-empresa")
def costos_empresa(db: Session = Depends(get_db)):
    try:
        resultados = (
            db.query(
                Empresa.nombre,
                func.count(Mantenimiento.id)
            )
            .outerjoin(
                Mantenimiento,
                Mantenimiento.empresa_id == Empresa.id
            )
            .group_by(Empresa.nombre)
            .all()
        )

        return [
            {
                "empresa": r[0],
                "costo_total": float(r[1] or 0),
                "costo": float(r[1] or 0),
            }
            for r in resultados
        ]
    except Exception as e:
        print("ERROR costos_empresa BI:", str(e))
        return []


@router.get("/tecnicos-productivos")
def tecnicos_productivos(db: Session = Depends(get_db)):
    try:
        resultados = (
            db.query(
                Usuario.nombre,
                func.count(Mantenimiento.id)
            )
            .outerjoin(
                Mantenimiento,
                Mantenimiento.tecnico_id == Usuario.id
            )
            .group_by(Usuario.nombre)
            .order_by(func.count(Mantenimiento.id).desc())
            .limit(10)
            .all()
        )

        return [
            {
                "tecnico": r[0] or "Sin nombre",
                "mantenimientos": r[1],
                "total": r[1],
            }
            for r in resultados
        ]
    except Exception as e:
        print("ERROR tecnicos_productivos BI:", str(e))
        return []


@router.get("/equipos-criticos")
def equipos_criticos(db: Session = Depends(get_db)):
    try:
        resultados = (
            db.query(
                Equipo.nombre,
                Empresa.nombre,
                func.count(Mantenimiento.id)
            )
            .outerjoin(
                Empresa,
                Equipo.empresa_id == Empresa.id
            )
            .outerjoin(
                Mantenimiento,
                Mantenimiento.equipo_id == Equipo.id
            )
            .group_by(
                Equipo.nombre,
                Empresa.nombre
            )
            .order_by(func.count(Mantenimiento.id).desc())
            .limit(10)
            .all()
        )

        return [
            {
                "equipo": r[0] or "Sin nombre",
                "empresa": r[1] or "Sin empresa",
                "mantenimientos": r[2],
                "total": r[2],
            }
            for r in resultados
        ]
    except Exception as e:
        print("ERROR equipos_criticos BI:", str(e))
        return []