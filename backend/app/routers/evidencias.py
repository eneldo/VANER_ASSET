# =========================================================
# ROUTER EVIDENCIAS
# Subida, listado y eliminación de evidencias por mantenimiento
# =========================================================

import os
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.evidencia import Evidencia
from app.models.mantenimiento import Mantenimiento
from app.schemas.evidencia import EvidenciaOut


router = APIRouter(prefix="/evidencias", tags=["Evidencias"])


# Tipos permitidos para clasificar evidencia
TIPOS_EVIDENCIA = ["ANTES", "DURANTE", "DESPUES"]


# Extensiones permitidas
EXTENSIONES_PERMITIDAS = [".jpg", ".jpeg", ".png", ".webp", ".pdf"]


def asegurar_carpeta_uploads():
    """
    Crea la carpeta de evidencias si no existe.
    """
    carpeta = os.path.join(settings.UPLOAD_DIR, "evidencias")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


@router.post("/{mantenimiento_id}", response_model=EvidenciaOut)
async def subir_evidencia(
    mantenimiento_id: UUID,
    tipo: str = Form(...),
    descripcion: str | None = Form(None),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Sube una evidencia asociada a un mantenimiento.

    tipo permitido:
    - ANTES
    - DURANTE
    - DESPUES
    """

    # Validar mantenimiento existente
    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_id
    ).first()

    if not mantenimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mantenimiento no encontrado"
        )

    # Normalizar tipo
    tipo = tipo.upper().strip()

    if tipo not in TIPOS_EVIDENCIA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo no permitido. Use uno de: {TIPOS_EVIDENCIA}"
        )

    # Validar extensión
    nombre_original = archivo.filename
    extension = os.path.splitext(nombre_original)[1].lower()

    if extension not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archivo no permitido. Use: {EXTENSIONES_PERMITIDAS}"
        )

    # Crear carpeta
    carpeta_destino = asegurar_carpeta_uploads()

    # Nombre único para evitar sobrescribir archivos
    nombre_archivo = f"{uuid.uuid4()}{extension}"
    ruta_fisica = os.path.join(carpeta_destino, nombre_archivo)

    # Guardar archivo físicamente
    contenido = await archivo.read()

    with open(ruta_fisica, "wb") as f:
        f.write(contenido)

    # Ruta pública que consumirá React
    archivo_url = f"/uploads/evidencias/{nombre_archivo}"

    # Guardar registro en BD
    nueva_evidencia = Evidencia(
        mantenimiento_id=mantenimiento_id,
        tipo=tipo,
        archivo_url=archivo_url,
        nombre_original=nombre_original,
        descripcion=descripcion
    )

    db.add(nueva_evidencia)
    db.commit()
    db.refresh(nueva_evidencia)

    return nueva_evidencia


@router.get("/mantenimiento/{mantenimiento_id}", response_model=list[EvidenciaOut])
def listar_evidencias_por_mantenimiento(
    mantenimiento_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Lista evidencias de un mantenimiento.
    """

    evidencias = db.query(Evidencia).filter(
        Evidencia.mantenimiento_id == mantenimiento_id
    ).order_by(Evidencia.created_at.desc()).all()

    return evidencias


@router.get("/mantenimiento/{mantenimiento_id}/tipo/{tipo}", response_model=list[EvidenciaOut])
def listar_evidencias_por_tipo(
    mantenimiento_id: UUID,
    tipo: str,
    db: Session = Depends(get_db)
):
    """
    Lista evidencias filtradas por tipo:
    ANTES, DURANTE o DESPUES.
    """

    tipo = tipo.upper().strip()

    if tipo not in TIPOS_EVIDENCIA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo no permitido. Use uno de: {TIPOS_EVIDENCIA}"
        )

    evidencias = db.query(Evidencia).filter(
        Evidencia.mantenimiento_id == mantenimiento_id,
        Evidencia.tipo == tipo
    ).order_by(Evidencia.created_at.desc()).all()

    return evidencias


@router.delete("/{evidencia_id}")
def eliminar_evidencia(
    evidencia_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Elimina una evidencia de la base de datos y también elimina
    el archivo físico si existe.
    """

    evidencia = db.query(Evidencia).filter(
        Evidencia.id == evidencia_id
    ).first()

    if not evidencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidencia no encontrada"
        )

    # Eliminar archivo físico
    archivo_relativo = evidencia.archivo_url.replace("/uploads/", "")
    ruta_fisica = os.path.join(settings.UPLOAD_DIR, archivo_relativo)

    if os.path.exists(ruta_fisica):
        os.remove(ruta_fisica)

    # Eliminar registro
    db.delete(evidencia)
    db.commit()

    return {"message": "Evidencia eliminada correctamente"}