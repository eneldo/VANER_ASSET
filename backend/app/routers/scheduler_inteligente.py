# ============================================================
# ROUTER - SCHEDULER INTELIGENTE PRO
# Archivo: backend/app/routers/scheduler_inteligente.py
# Fase 34.2.7
# ============================================================

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import scheduler_inteligente  # noqa: F401 - registra modelos
from app.schemas.scheduler_inteligente import (
    SchedulerLogOut,
    SchedulerReglaCreate,
    SchedulerReglaOut,
    SchedulerReglaUpdate,
    SchedulerRunResult,
    SchedulerSugerenciaOut,
)
from app.services.scheduler_inteligente_service import (
    actualizar_regla,
    aprobar_sugerencia,
    crear_regla,
    dashboard_scheduler,
    ejecutar_revision,
    eliminar_regla,
    listar_reglas,
    listar_sugerencias,
    rechazar_sugerencia,
)
from app.models.scheduler_inteligente import SchedulerLog

router = APIRouter(prefix="/scheduler-inteligente", tags=["Scheduler Inteligente PRO"])


@router.post("/inicializar")
def inicializar_tablas():
    """Compatibilidad: las tablas se administran exclusivamente con Alembic."""
    return {"ok": True, "mensaje": "Esquema Scheduler administrado por Alembic"}


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return dashboard_scheduler(db)


@router.get("/reglas", response_model=list[SchedulerReglaOut])
def reglas(db: Session = Depends(get_db)):
    return listar_reglas(db)


@router.post("/reglas", response_model=SchedulerReglaOut)
def crear(data: SchedulerReglaCreate, db: Session = Depends(get_db)):
    return crear_regla(db, data)


@router.put("/reglas/{regla_id}", response_model=SchedulerReglaOut)
def actualizar(regla_id: UUID, data: SchedulerReglaUpdate, db: Session = Depends(get_db)):
    regla = actualizar_regla(db, regla_id, data)
    if not regla:
        raise HTTPException(status_code=404, detail="Regla no encontrada")
    return regla


@router.delete("/reglas/{regla_id}")
def eliminar(regla_id: UUID, db: Session = Depends(get_db)):
    ok = eliminar_regla(db, regla_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Regla no encontrada")
    return {"ok": True, "mensaje": "Regla eliminada"}


@router.post("/ejecutar", response_model=SchedulerRunResult)
def ejecutar(db: Session = Depends(get_db)):
    """Ejecuta manualmente la revisión de reglas."""
    return ejecutar_revision(db)


@router.get("/sugerencias", response_model=list[SchedulerSugerenciaOut])
def sugerencias(estado: str | None = Query(None), db: Session = Depends(get_db)):
    return listar_sugerencias(db, estado=estado)


@router.post("/sugerencias/{sugerencia_id}/aprobar", response_model=SchedulerSugerenciaOut)
def aprobar(sugerencia_id: UUID, db: Session = Depends(get_db)):
    sugerencia = aprobar_sugerencia(db, sugerencia_id)
    if not sugerencia:
        raise HTTPException(status_code=404, detail="Sugerencia no encontrada")
    return sugerencia


@router.post("/sugerencias/{sugerencia_id}/rechazar", response_model=SchedulerSugerenciaOut)
def rechazar(sugerencia_id: UUID, db: Session = Depends(get_db)):
    sugerencia = rechazar_sugerencia(db, sugerencia_id)
    if not sugerencia:
        raise HTTPException(status_code=404, detail="Sugerencia no encontrada")
    return sugerencia


@router.get("/logs", response_model=list[SchedulerLogOut])
def logs(limit: int = Query(80, ge=1, le=500), db: Session = Depends(get_db)):
    return db.query(SchedulerLog).order_by(SchedulerLog.creado_en.desc()).limit(limit).all()
