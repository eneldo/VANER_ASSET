# ============================================================
# ROUTER MULTIEMPRESA ENTERPRISE PRO
# Archivo: backend/app/routers/multiempresa_enterprise.py
# FASE 34.3 — Panel Multiempresa Enterprise PRO
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.equipo import Equipo
from app.models.usuario import Usuario
from app.models.mantenimiento import Mantenimiento

router = APIRouter(
    prefix="/multiempresa-enterprise",
    tags=["Multiempresa Enterprise PRO"]
)


# ============================================================
# DASHBOARD REAL MULTIEMPRESA
# ============================================================

@router.get("/dashboard")
def dashboard_multiempresa(db: Session = Depends(get_db)):
    """
    Devuelve indicadores reales del sistema multiempresa.

    Cuenta:
    - Empresas reales
    - Usuarios reales
    - Equipos reales
    - Mantenimientos reales
    """

    total_empresas = db.query(func.count(Empresa.id)).scalar() or 0
    total_usuarios = db.query(func.count(Usuario.id)).scalar() or 0
    total_equipos = db.query(func.count(Equipo.id)).scalar() or 0
    total_mantenimientos = db.query(func.count(Mantenimiento.id)).scalar() or 0

    return {
        "success": True,
        "empresas": total_empresas,
        "usuarios": total_usuarios,
        "equipos": total_equipos,
        "mantenimientos": total_mantenimientos,
    }


# ============================================================
# LISTAR EMPRESAS REALES CON KPIS
# ============================================================

@router.get("/empresas")
def listar_empresas_multiempresa(db: Session = Depends(get_db)):
    """
    Lista empresas reales desde PostgreSQL.

    Por cada empresa calcula:
    - Total sedes
    - Total equipos
    - Total usuarios
    - Total mantenimientos
    """

    empresas = (
        db.query(Empresa)
        .order_by(Empresa.nombre.asc())
        .all()
    )

    resultado = []

    for empresa in empresas:

        sedes = (
            db.query(func.count(Sede.id))
            .filter(Sede.empresa_id == empresa.id)
            .scalar()
            or 0
        )

        equipos = (
            db.query(func.count(Equipo.id))
            .filter(Equipo.empresa_id == empresa.id)
            .scalar()
            or 0
        )

        usuarios = (
            db.query(func.count(Usuario.id))
            .filter(Usuario.empresa_id == empresa.id)
            .scalar()
            or 0
        )

        mantenimientos = (
            db.query(func.count(Mantenimiento.id))
            .filter(Mantenimiento.empresa_id == empresa.id)
            .scalar()
            or 0
        )

        resultado.append({
            "id": str(empresa.id),
            "nombre": empresa.nombre,
            "nit": empresa.nit,
            "telefono": empresa.telefono,
            "correo": empresa.correo,
            "direccion": empresa.direccion,
            "logo_url": empresa.logo_url,
            "activo": empresa.activo,
            "estado": "ACTIVA" if empresa.activo else "INACTIVA",
            "sedes": sedes,
            "equipos": equipos,
            "usuarios": usuarios,
            "mantenimientos": mantenimientos,
        })

    return {
        "success": True,
        "total": len(resultado),
        "empresas": resultado,
    }


# ============================================================
# DETALLE EMPRESA REAL
# ============================================================

@router.get("/empresas/{empresa_id}")
def detalle_empresa_multiempresa(
    empresa_id: str,
    db: Session = Depends(get_db)
):
    """
    Devuelve detalle real de una empresa específica.
    """

    empresa = (
        db.query(Empresa)
        .filter(Empresa.id == empresa_id)
        .first()
    )

    if not empresa:
        raise HTTPException(
            status_code=404,
            detail="Empresa no encontrada"
        )

    sedes = (
        db.query(func.count(Sede.id))
        .filter(Sede.empresa_id == empresa.id)
        .scalar()
        or 0
    )

    equipos = (
        db.query(func.count(Equipo.id))
        .filter(Equipo.empresa_id == empresa.id)
        .scalar()
        or 0
    )

    usuarios = (
        db.query(func.count(Usuario.id))
        .filter(Usuario.empresa_id == empresa.id)
        .scalar()
        or 0
    )

    mantenimientos = (
        db.query(func.count(Mantenimiento.id))
        .filter(Mantenimiento.empresa_id == empresa.id)
        .scalar()
        or 0
    )

    return {
        "success": True,
        "empresa": {
            "id": str(empresa.id),
            "nombre": empresa.nombre,
            "nit": empresa.nit,
            "telefono": empresa.telefono,
            "correo": empresa.correo,
            "direccion": empresa.direccion,
            "logo_url": empresa.logo_url,
            "activo": empresa.activo,
            "estado": "ACTIVA" if empresa.activo else "INACTIVA",
            "sedes": sedes,
            "equipos": equipos,
            "usuarios": usuarios,
            "mantenimientos": mantenimientos,
        }
    }