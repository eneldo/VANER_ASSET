"""
FASE 31.6 - ROUTER CLIENTE SEGURO PRO
Archivo: backend/app/routers/cliente_seguro.py

Objetivo:
- Endpoints de ejemplo seguros para portal cliente.
- Filtran por empresa_id desde el token, no desde el frontend.

Ajusta los imports de modelos si tus nombres son diferentes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.multiempresa import require_empresa_scope

# Ajusta estos imports si tus modelos tienen otro nombre/ruta.
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.equipo import Equipo
from app.models.mantenimiento import Mantenimiento

# Ajusta este import a tu dependencia real de autenticación.
try:
    from app.auth.dependencies import get_current_user
except Exception:  # fallback para proyectos donde esté en security/auth.py
    from app.security.auth import get_current_user

router = APIRouter(prefix="/cliente-seguro", tags=["Cliente Seguro PRO"])


@router.get("/dashboard")
def dashboard_cliente_seguro(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Dashboard cliente filtrado SIEMPRE por empresa del token."""
    empresa_id = require_empresa_scope(current_user)

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    total_sedes = db.query(Sede).filter(Sede.empresa_id == empresa_id).count()
    total_equipos = db.query(Equipo).filter(Equipo.empresa_id == empresa_id).count()
    total_mantenimientos = db.query(Mantenimiento).filter(Mantenimiento.empresa_id == empresa_id).count()

    pendientes = (
        db.query(Mantenimiento)
        .filter(Mantenimiento.empresa_id == empresa_id)
        .filter(Mantenimiento.estado.in_(["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO"]))
        .count()
    )

    finalizados = (
        db.query(Mantenimiento)
        .filter(Mantenimiento.empresa_id == empresa_id)
        .filter(Mantenimiento.estado == "FINALIZADO")
        .count()
    )

    return {
        "empresa_id": str(empresa_id),
        "empresa": getattr(empresa, "nombre", "Empresa"),
        "total_sedes": total_sedes,
        "total_equipos": total_equipos,
        "total_mantenimientos": total_mantenimientos,
        "mantenimientos_pendientes": pendientes,
        "mantenimientos_finalizados": finalizados,
    }


@router.get("/sedes")
def listar_sedes_cliente_seguro(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista solo sedes de la empresa autenticada."""
    empresa_id = require_empresa_scope(current_user)
    sedes = db.query(Sede).filter(Sede.empresa_id == empresa_id).all()
    return sedes


@router.get("/equipos")
def listar_equipos_cliente_seguro(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista solo equipos de la empresa autenticada."""
    empresa_id = require_empresa_scope(current_user)
    equipos = db.query(Equipo).filter(Equipo.empresa_id == empresa_id).all()
    return equipos


@router.get("/mantenimientos")
def listar_mantenimientos_cliente_seguro(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista solo mantenimientos de la empresa autenticada."""
    empresa_id = require_empresa_scope(current_user)
    mantenimientos = db.query(Mantenimiento).filter(Mantenimiento.empresa_id == empresa_id).all()
    return mantenimientos
