# ============================================================
# ROUTER RECOVERY & RESTORE PRO
# ============================================================

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.recovery_service import RecoveryService
from app.schemas.recovery_schema import RestoreRequest

router = APIRouter(
    prefix="/recovery",
    tags=["Recovery & Restore PRO"]
)


# ============================================================
# CREAR BACKUP
# ============================================================

@router.post("/backup")
def crear_backup():

    try:

        backup = RecoveryService.crear_backup()

        return {
            "success": True,
            "backup": backup
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# LISTAR BACKUPS
# ============================================================

@router.get("/backups")
def listar_backups():

    return RecoveryService.listar_backups()


# ============================================================
# DESCARGAR BACKUP
# ============================================================

@router.get("/download/{archivo}")
def descargar_backup(archivo: str):

    backups = RecoveryService.listar_backups()

    encontrado = next(
        (b for b in backups if b["nombre"] == archivo),
        None
    )

    if not encontrado:
        raise HTTPException(
            status_code=404,
            detail="Backup no encontrado"
        )

    return FileResponse(
        encontrado["ruta"],
        filename=archivo,
        media_type="application/sql"
    )


# ============================================================
# RESTAURAR BACKUP
# ============================================================

@router.post("/restore")
def restaurar(data: RestoreRequest):

    try:

        if data.confirmacion != "RESTAURAR_BASE_DE_DATOS":
            raise HTTPException(
                status_code=400,
                detail="Confirmación de restauración inválida"
            )

        return RecoveryService.ejecutar_restore(
            data.archivo_backup
        )

    except HTTPException:

        raise

    except PermissionError as e:

        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="No fue posible restaurar la base de datos"
        )


# ============================================================
# ESTADO SISTEMA
# ============================================================

@router.get("/status")
def estado_sistema():

    return RecoveryService.estado_sistema()
