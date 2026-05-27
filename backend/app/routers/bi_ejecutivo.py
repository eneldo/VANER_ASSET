# ============================================================
# BI EJECUTIVO AVANZADO PRO
# Archivo: backend/app/routers/bi_ejecutivo.py
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db

# ============================================================
# IMPORTAR MODELOS
# ============================================================

from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.equipo import Equipo
from app.models.usuario import Usuario
from app.models.mantenimiento import Mantenimiento

# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/bi-ejecutivo",
    tags=["BI Ejecutivo PRO"]
)

# ============================================================
# KPI GENERALES
# ============================================================

@router.get("/kpis")
def obtener_kpis(db: Session = Depends(get_db)):

    try:

        total_empresas = db.query(Empresa).count()
        total_sedes = db.query(Sede).count()
        total_equipos = db.query(Equipo).count()
        total_usuarios = db.query(Usuario).count()
        total_mantenimientos = db.query(Mantenimiento).count()

        return {
            "total_empresas": total_empresas,
            "total_sedes": total_sedes,
            "total_equipos": total_equipos,
            "total_usuarios": total_usuarios,
            "total_mantenimientos": total_mantenimientos
        }

    except Exception as e:

        print("ERROR KPI:", str(e))

        return {
            "total_empresas": 0,
            "total_sedes": 0,
            "total_equipos": 0,
            "total_usuarios": 0,
            "total_mantenimientos": 0
        }


# ============================================================
# MANTENIMIENTOS POR ESTADO
# ============================================================

@router.get("/mantenimientos-estado")
def mantenimientos_estado(db: Session = Depends(get_db)):

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
                "estado": r[0] if r[0] else "SIN_ESTADO",
                "total": r[1]
            }
            for r in resultados
        ]

    except Exception as e:

        print("ERROR mantenimientos_estado:", str(e))

        return []


# ============================================================
# EQUIPOS POR EMPRESA
# ============================================================

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
                "total": r[1]
            }
            for r in resultados
        ]

    except Exception as e:

        print("ERROR equipos_empresa:", str(e))

        return []


# ============================================================
# COSTOS POR EMPRESA
# ============================================================

@router.get("/costos-empresa")
def costos_empresa(db: Session = Depends(get_db)):

    try:

        # ====================================================
        # COMPATIBLE CON BD ACTUAL
        # SI NO EXISTE "costo"
        # USA CONTEO DE MANTENIMIENTOS
        # ====================================================

        resultados = (
            db.query(
                Empresa.nombre,
                func.count(Mantenimiento.id).label("total")
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
                "costo": r[1]
            }
            for r in resultados
        ]

    except Exception as e:

        print("ERROR costos_empresa:", str(e))

        return []


# ============================================================
# TECNICOS PRODUCTIVOS
# ============================================================

@router.get("/tecnicos-productivos")
def tecnicos_productivos(db: Session = Depends(get_db)):

    try:

        resultados = (
            db.query(
                Usuario.nombre,
                func.count(Mantenimiento.id).label("total")
            )
            .join(
                Mantenimiento,
                Mantenimiento.tecnico_id == Usuario.id
            )
            .group_by(Usuario.nombre)
            .all()
        )

        return [
            {
                "tecnico": r[0],
                "total": r[1]
            }
            for r in resultados
        ]

    except Exception as e:

        print("ERROR tecnicos_productivos:", str(e))

        return []


# ============================================================
# EQUIPOS CRITICOS
# ============================================================

@router.get("/equipos-criticos")
def equipos_criticos(db: Session = Depends(get_db)):

    try:

        resultados = (
            db.query(
                Equipo.nombre,
                Empresa.nombre,
                func.count(Mantenimiento.id).label("total")
            )
            .outerjoin(
                Mantenimiento,
                Mantenimiento.equipo_id == Equipo.id
            )
            .outerjoin(
                Empresa,
                Equipo.empresa_id == Empresa.id
            )
            .group_by(
                Equipo.nombre,
                Empresa.nombre
            )
            .order_by(
                func.count(Mantenimiento.id).desc()
            )
            .limit(10)
            .all()
        )

        return [
            {
                "equipo": r[0],
                "empresa": r[1],
                "mantenimientos": r[2]
            }
            for r in resultados
        ]

    except Exception as e:

        print("ERROR equipos_criticos:", str(e))

        return []