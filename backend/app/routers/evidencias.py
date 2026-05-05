# =========================================================
# ROUTER EVIDENCIAS PRO
# Compatible con UUID + modelo actual del usuario
# =========================================================

import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.evidencia import Evidencia

router = APIRouter(prefix="/evidencias", tags=["Evidencias"])

# Carpeta de almacenamiento
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "evidencias")

os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================================================
# SUBIR EVIDENCIA
# =========================================================
@router.post("/subir")
async def subir_evidencia(
    mantenimiento_id: str = Form(...),
    equipo_id: str = Form(...),
    tipo: str = Form(...),
    descripcion: str = Form(""),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Subir evidencia (imagen o PDF)
    """

    tipos_validos = ["ANTES", "DURANTE", "DESPUES", "SOPORTE"]

    if tipo not in tipos_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo inválido. Usa: {tipos_validos}"
        )

    # Validar extensión
    extension = archivo.filename.split(".")[-1].lower()

    if extension not in ["jpg", "jpeg", "png", "pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Formato no permitido. Solo JPG, PNG o PDF"
        )

    nombre_archivo = f"{uuid.uuid4()}.{extension}"
    ruta_archivo = os.path.join(UPLOAD_DIR, nombre_archivo)

    try:
        with open(ruta_archivo, "wb") as buffer:
            buffer.write(await archivo.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    nueva = Evidencia(
        mantenimiento_id=mantenimiento_id,
        equipo_id=equipo_id,
        tipo=tipo,
        archivo_url=f"/uploads/evidencias/{nombre_archivo}",
        nombre_original=archivo.filename,
        descripcion=descripcion
    )

    db.add(nueva)
    db.commit()

    return {
        "msg": "Evidencia subida correctamente",
        "archivo": nueva.archivo_url
    }


# =========================================================
# LISTAR POR MANTENIMIENTO
# =========================================================
@router.get("/mantenimiento/{mantenimiento_id}")
def evidencias_por_mantenimiento(
    mantenimiento_id: str,
    db: Session = Depends(get_db)
):
    evidencias = db.query(Evidencia).filter(
        Evidencia.mantenimiento_id == mantenimiento_id
    ).order_by(Evidencia.created_at.desc()).all()

    return evidencias


# =========================================================
# LISTAR POR EQUIPO (GALERÍA)
# =========================================================
@router.get("/equipo/{equipo_id}")
def evidencias_por_equipo(
    equipo_id: str,
    db: Session = Depends(get_db)
):
    evidencias = db.query(Evidencia).filter(
        Evidencia.equipo_id == equipo_id
    ).order_by(Evidencia.created_at.desc()).all()

    return evidencias


# =========================================================
# ELIMINAR EVIDENCIA
# =========================================================
@router.delete("/{evidencia_id}")
def eliminar_evidencia(
    evidencia_id: str,
    db: Session = Depends(get_db)
):
    evidencia = db.query(Evidencia).filter(
        Evidencia.id == evidencia_id
    ).first()

    if not evidencia:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")

    # Eliminar archivo físico
    try:
        ruta = evidencia.archivo_url.replace("/uploads/", "")
        ruta_completa = os.path.join(BASE_DIR, "uploads", ruta.split("/", 1)[1])

        if os.path.exists(ruta_completa):
            os.remove(ruta_completa)
    except Exception:
        pass

    db.delete(evidencia)
    db.commit()

    return {"msg": "Evidencia eliminada correctamente"}
# =========================================================
# LISTAR TODAS LAS EVIDENCIAS (ADMIN)
# =========================================================
@router.get("/")
def listar_todas(db: Session = Depends(get_db)):
    return db.query(Evidencia).order_by(Evidencia.created_at.desc()).all()