"""
===========================================================
ROUTER EVIDENCIAS PRO SEGURAS
FASE 31.8
===========================================================
"""

import os
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException
)

from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.evidencia import Evidencia
from app.services.evidencia_service import save_secure_file

router = APIRouter(
    prefix="/evidencias",
    tags=["Evidencias PRO"]
)


# ===========================================================
# SUBIR EVIDENCIA
# ===========================================================

@router.post("/subir")

async def subir_evidencia(
    mantenimiento_id: str = Form(...),
    tipo: str = Form(...),
    descripcion: str = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    try:

        # ===================================================
        # GUARDADO SEGURO
        # ===================================================

        saved = await save_secure_file(archivo)

        nueva = Evidencia(
            mantenimiento_id=mantenimiento_id,
            tipo=tipo,
            descripcion=descripcion,
            nombre_original=archivo.filename,
            archivo_url=saved["filename"]
        )

        db.add(nueva)
        db.commit()
        db.refresh(nueva)

        return {
            "message": "Archivo subido correctamente",
            "archivo": nueva.archivo_url
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ===========================================================
# DESCARGA SEGURA
# ===========================================================

@router.get("/descargar/{filename}")

def descargar_archivo(filename: str):

    base_dir = "app/uploads/evidencias"

    safe_name = os.path.basename(filename)

    path = os.path.join(base_dir, safe_name)

    if not os.path.exists(path):
        raise HTTPException(404, "Archivo no encontrado")

    return FileResponse(
        path,
        filename=safe_name
    )


# ===========================================================
# ELIMINAR EVIDENCIA
# ===========================================================

@router.delete("/{id}")

def eliminar_evidencia(
    id: str,
    db: Session = Depends(get_db)
):

    evidencia = db.query(Evidencia).filter(
        Evidencia.id == id
    ).first()

    if not evidencia:
        raise HTTPException(404, "No encontrada")

    path = f"app/uploads/evidencias/{evidencia.archivo_url}"

    if os.path.exists(path):
        os.remove(path)

    db.delete(evidencia)

    db.commit()

    return {
        "message": "Evidencia eliminada"
    }