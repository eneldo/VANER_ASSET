# ============================================================
# ROUTER: Automatización SaaS PRO
# Archivo: backend/app/routers/automatizacion.py
# Fase 34.2.1
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.automatizacion import (
    AutomatizacionOut,
    AutomatizacionUpdate,
    AutomatizacionLogOut,
    SchedulerStatusOut,
    MonitorSistemaOut,
)
from app.services.automation_service import (
    inicializar_automatizaciones,
    listar_automatizaciones,
    actualizar_automatizacion,
    listar_logs,
)
from app.services.scheduler_service import estado_scheduler
from app.services.monitor_service import obtener_estado_sistema
from app.automation.scheduler import reiniciar_jobs_sga

router = APIRouter(prefix="/automatizacion", tags=["Automatización SaaS PRO"])


@router.post("/inicializar", response_model=list[AutomatizacionOut])
def inicializar(db: Session = Depends(get_db)):
    """Crea tablas y configuraciones base si no existen."""
    registros = inicializar_automatizaciones(db)
    reiniciar_jobs_sga()
    return registros


@router.get("/", response_model=list[AutomatizacionOut])
def listar(db: Session = Depends(get_db)):
    """Lista todos los módulos de automatización."""
    inicializar_automatizaciones(db)
    return listar_automatizaciones(db)


@router.put("/{modulo}", response_model=AutomatizacionOut)
def actualizar(modulo: str, payload: AutomatizacionUpdate, db: Session = Depends(get_db)):
    """Actualiza switches, frecuencia y configuración del módulo."""
    registro = actualizar_automatizacion(db, modulo, payload.model_dump(exclude_unset=True))
    if not registro:
        raise HTTPException(status_code=404, detail="Automatización no encontrada")
    reiniciar_jobs_sga()
    return registro


@router.post("/{modulo}/toggle", response_model=AutomatizacionOut)
def toggle(modulo: str, db: Session = Depends(get_db)):
    """Activa/desactiva rápidamente una automatización."""
    registros = listar_automatizaciones(db)
    actual = next((r for r in registros if r.modulo == modulo), None)
    if not actual:
        raise HTTPException(status_code=404, detail="Automatización no encontrada")

    registro = actualizar_automatizacion(db, modulo, {"activo": not actual.activo})
    reiniciar_jobs_sga()
    return registro


@router.get("/scheduler/status", response_model=SchedulerStatusOut)
def scheduler_status():
    """Estado actual del scheduler y jobs cargados."""
    return estado_scheduler()


@router.post("/scheduler/reiniciar", response_model=SchedulerStatusOut)
def scheduler_reiniciar():
    """Re-sincroniza jobs activos desde PostgreSQL."""
    reiniciar_jobs_sga()
    return estado_scheduler()


@router.get("/monitor", response_model=MonitorSistemaOut)
def monitor():
    """Métricas del sistema. No modifica datos."""
    return obtener_estado_sistema()


@router.get("/logs", response_model=list[AutomatizacionLogOut])
def logs(limite: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    return listar_logs(db, limite=limite)
