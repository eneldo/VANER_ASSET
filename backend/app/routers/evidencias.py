"""
===========================================================
ROUTER EVIDENCIAS PRO
Archivo: backend/app/routers/evidencias.py

Funciones:
- Listar evidencias
- Subir evidencias
- Ver/descargar archivo
- Filtrar por mantenimiento
- Filtrar por equipo
- Eliminar evidencia
===========================================================
"""

import os
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.evidencia import Evidencia
from app.models.mantenimiento import Mantenimiento
from app.services.evidencia_service import save_secure_file

router = APIRouter(prefix="/evidencias", tags=["Evidencias PRO"])


# ===========================================================
# CONFIGURACIÓN DE RUTA DE ARCHIVOS
# ===========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "evidencias")

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===========================================================
# SERIALIZADOR
# ===========================================================

def serializar_evidencia(e: Evidencia):
    """
    Convierte una evidencia en diccionario listo para React.
    """

    archivo = e.archivo_url or ""

    if archivo.startswith("/uploads/"):
        archivo_url = archivo
        filename = os.path.basename(archivo)
    else:
        filename = os.path.basename(archivo)
        archivo_url = f"/uploads/evidencias/{filename}"

    return {
        "id": str(e.id),
        "mantenimiento_id": str(e.mantenimiento_id) if e.mantenimiento_id else None,
        "equipo_id": str(e.equipo_id) if e.equipo_id else None,
        "tipo": e.tipo,
        "descripcion": e.descripcion,
        "nombre_original": e.nombre_original,
        "archivo_url": archivo_url,
        "filename": filename,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


# ===========================================================
# LISTAR TODAS LAS EVIDENCIAS
# GET /evidencias/
# ===========================================================

@router.get("/")
def listar_evidencias(db: Session = Depends(get_db)):
    evidencias = db.query(Evidencia).order_by(Evidencia.created_at.desc()).all()
    return [serializar_evidencia(e) for e in evidencias]


# ===========================================================
# LISTAR POR MANTENIMIENTO
# GET /evidencias/mantenimiento/{mantenimiento_id}
# ===========================================================

@router.get("/mantenimiento/{mantenimiento_id}")
def evidencias_por_mantenimiento(
    mantenimiento_id: UUID,
    db: Session = Depends(get_db),
):
    evidencias = (
        db.query(Evidencia)
        .filter(Evidencia.mantenimiento_id == mantenimiento_id)
        .order_by(Evidencia.created_at.desc())
        .all()
    )

    return [serializar_evidencia(e) for e in evidencias]


# ===========================================================
# LISTAR POR EQUIPO
# GET /evidencias/equipo/{equipo_id}
# ===========================================================

@router.get("/equipo/{equipo_id}")
def evidencias_por_equipo(
    equipo_id: UUID,
    db: Session = Depends(get_db),
):
    evidencias = (
        db.query(Evidencia)
        .filter(Evidencia.equipo_id == equipo_id)
        .order_by(Evidencia.created_at.desc())
        .all()
    )

    return [serializar_evidencia(e) for e in evidencias]


# ===========================================================
# SUBIR EVIDENCIA
# POST /evidencias/subir
# ===========================================================

@router.post("/subir")
async def subir_evidencia(
    mantenimiento_id: UUID = Form(...),
    tipo: str = Form(...),
    descripcion: str = Form(None),
    equipo_id: UUID = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    mantenimiento = (
        db.query(Mantenimiento)
        .filter(Mantenimiento.id == mantenimiento_id)
        .first()
    )

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    equipo_final_id = equipo_id or getattr(mantenimiento, "equipo_id", None)

    if not equipo_final_id:
        raise HTTPException(
            status_code=400,
            detail="No se pudo determinar el equipo de la evidencia",
        )

    try:
        saved = await save_secure_file(archivo)

        filename = saved["filename"]

        nueva = Evidencia(
            mantenimiento_id=mantenimiento_id,
            equipo_id=equipo_final_id,
            tipo=tipo,
            descripcion=descripcion,
            nombre_original=archivo.filename,
            archivo_url=filename,
        )

        db.add(nueva)
        db.commit()
        db.refresh(nueva)

        return {
            "message": "Archivo subido correctamente",
            "evidencia": serializar_evidencia(nueva),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================================================
# DESCARGA / VISUALIZACIÓN SEGURA
# GET /evidencias/descargar/{filename}
# ===========================================================

@router.get("/descargar/{filename}")
def descargar_archivo(filename: str):
    safe_name = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, safe_name)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    return FileResponse(path)


# ===========================================================
# ELIMINAR EVIDENCIA
# DELETE /evidencias/{id}
# ===========================================================

@router.delete("/{id}")
def eliminar_evidencia(
    id: UUID,
    db: Session = Depends(get_db),
):
    evidencia = db.query(Evidencia).filter(Evidencia.id == id).first()

    if not evidencia:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")

    filename = os.path.basename(evidencia.archivo_url or "")
    path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(path):
        os.remove(path)

    db.delete(evidencia)
    db.commit()

    return {"message": "Evidencia eliminada correctamente"}