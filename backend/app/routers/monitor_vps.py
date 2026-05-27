# ============================================================
# ROUTER MONITOR VPS + POSTGRESQL PRO
# Archivo: backend/app/routers/monitor_vps.py
# Fase 34.2.4
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.monitor_vps_service import (
    obtener_estado_docker,
    obtener_estado_postgresql,
    obtener_estado_vps,
    obtener_resumen_monitor,
)

router = APIRouter(
    prefix="/monitor-vps",
    tags=["Monitor VPS + PostgreSQL PRO"],
)


@router.get("/resumen")
def resumen_monitor(db: Session = Depends(get_db)):
    """Dashboard consolidado: VPS + PostgreSQL + Docker."""
    return obtener_resumen_monitor(db)


@router.get("/vps")
def estado_vps():
    """Métricas del VPS/servidor."""
    return obtener_estado_vps()


@router.get("/postgresql")
def estado_postgresql(db: Session = Depends(get_db)):
    """Métricas PostgreSQL."""
    return obtener_estado_postgresql(db)


@router.get("/docker")
def estado_docker():
    """Estado Docker si el CLI está disponible."""
    return obtener_estado_docker()


@router.get("/health")
def health_monitor():
    """Healthcheck simple del módulo."""
    return {
        "ok": True,
        "modulo": "Monitor VPS + PostgreSQL PRO",
        "fase": "34.2.4",
    }
