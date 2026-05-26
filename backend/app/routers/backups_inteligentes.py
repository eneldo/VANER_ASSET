# ============================================================
# ROUTER: Backups Inteligentes SaaS PRO
# Archivo: backend/app/routers/backups_inteligentes.py
# Fase 34.2.2
# ============================================================

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db, Base, engine
from app.models.backup_historial import BackupHistorial
from app.schemas.backup_historial import BackupEjecutarRequest, BackupHistorialOut, BackupStatusOut
from app.services.smart_backup_service import SmartBackupService

router = APIRouter(prefix="/backups-inteligentes", tags=["Backups Inteligentes SaaS"])


@router.on_event("startup")
def crear_tablas_backups():
    # Seguro en desarrollo y producción. No altera tablas existentes.
    Base.metadata.create_all(bind=engine, tables=[BackupHistorial.__table__])


@router.get("/status", response_model=BackupStatusOut)
def status(db: Session = Depends(get_db)):
    return SmartBackupService(db).status()


@router.get("/", response_model=list[BackupHistorialOut])
def listar(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return SmartBackupService(db).listar(limit)


@router.post("/ejecutar", response_model=BackupHistorialOut)
def ejecutar(payload: BackupEjecutarRequest, db: Session = Depends(get_db)):
    return SmartBackupService(db).ejecutar_backup(
        tipo=payload.tipo,
        incluir_db=payload.incluir_db,
        incluir_uploads=payload.incluir_uploads,
        incluir_codigo=payload.incluir_codigo,
        creado_por=payload.creado_por,
    )


@router.delete("/limpiar")
def limpiar(retencion_dias: int = Query(15, ge=1, le=365), db: Session = Depends(get_db)):
    eliminados = SmartBackupService(db).limpiar_antiguos(retencion_dias)
    return {"ok": True, "eliminados": eliminados, "mensaje": "Limpieza ejecutada"}


@router.get("/{backup_id}/descargar")
def descargar(backup_id: UUID, db: Session = Depends(get_db)):
    item = SmartBackupService(db).obtener(backup_id)
    if not item.ruta_archivo:
        return {"ok": False, "mensaje": "Backup sin archivo asociado"}
    return FileResponse(
        path=item.ruta_archivo,
        filename=item.nombre_archivo or "backup_sga.zip",
        media_type="application/zip",
    )
