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

FIX PRODUCCIÓN:
- Usa el mismo servicio de guardado para todos los flujos.
- Guarda en BD la URL pública real: /uploads/evidencias/<archivo>.
- Eliminar borra BD aunque el archivo físico ya no exista.
===========================================================
"""

import os
import hashlib
import hmac
import time
import mimetypes
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import establecer_contexto_sistema, get_db
from app.models.evidencia import Evidencia
from app.models.mantenimiento import Mantenimiento
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.routers.auth import obtener_usuario_actual
from app.config import settings
from app.services.evidencia_service import (
    save_secure_file,
    get_evidence_upload_config,
    get_evidencia_path,
    EVIDENCIAS_DIR,
)

router = APIRouter(prefix="/evidencias", tags=["Evidencias PRO"])


# ===========================================================
# SERIALIZADOR
# ===========================================================

def crear_url_firmada(evidencia_id, filename=None, ttl_segundos=3600):
    expires = int(time.time()) + ttl_segundos
    payload = f"{evidencia_id}:{expires}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode(), payload, hashlib.sha256).hexdigest()
    url = f"/evidencias/{evidencia_id}/archivo?expires={expires}&signature={signature}"
    return f"{url}&filename={os.path.basename(filename)}" if filename else url


def validar_firma_archivo(evidencia_id, expires: int, signature: str):
    if expires < int(time.time()):
        raise HTTPException(status_code=401, detail="El enlace de evidencia expiró")
    payload = f"{evidencia_id}:{expires}".encode()
    esperada = hmac.new(settings.SECRET_KEY.encode(), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(esperada, signature or ""):
        raise HTTPException(status_code=403, detail="Firma de archivo inválida")


def autorizar_mantenimiento(usuario: Usuario, mantenimiento: Mantenimiento, db: Session, escritura=False):
    rol = str(usuario.rol or "").upper()
    if rol == "ADMIN":
        return mantenimiento
    if rol == "COORDINADOR" and str(usuario.empresa_id) == str(mantenimiento.empresa_id):
        return mantenimiento
    if rol in {"EMPRESA", "CLIENTE"}:
        if not escritura and str(usuario.empresa_id) == str(mantenimiento.empresa_id):
            return mantenimiento
        raise HTTPException(status_code=403, detail="Sin permiso sobre esta evidencia")
    if rol == "TECNICO":
        tecnico = db.query(Tecnico).filter(Tecnico.usuario_id == usuario.id).first()
        if tecnico and str(tecnico.id) == str(mantenimiento.tecnico_id):
            if escritura and str(getattr(mantenimiento, "estado", "") or "").upper() == "FINALIZADO":
                raise HTTPException(
                    status_code=409,
                    detail="Debes reabrir el mantenimiento antes de modificar sus evidencias",
                )
            return mantenimiento
    raise HTTPException(status_code=403, detail="Sin acceso a esta evidencia")


def autorizar_evidencia(usuario: Usuario, evidencia: Evidencia, db: Session, escritura=False):
    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == evidencia.mantenimiento_id
    ).first()
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    return autorizar_mantenimiento(usuario, mantenimiento, db, escritura)


def serializar_evidencia(e: Evidencia):
    archivo = e.archivo_url or ""

    if archivo.startswith("/uploads/"):
        archivo_url = archivo
        filename = os.path.basename(archivo)
    else:
        filename = os.path.basename(archivo)
        archivo_url = f"/uploads/evidencias/{filename}" if filename else ""

    return {
        "id": str(e.id),
        "mantenimiento_id": str(e.mantenimiento_id) if e.mantenimiento_id else None,
        "equipo_id": str(e.equipo_id) if e.equipo_id else None,
        "tipo": e.tipo,
        "descripcion": e.descripcion,
        "nombre_original": e.nombre_original,
        "archivo_url": crear_url_firmada(e.id, filename),
        "descarga_url": crear_url_firmada(e.id, filename),
        "filename": filename,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


# ===========================================================
# LISTAR TODAS LAS EVIDENCIAS
# GET /evidencias/
# ===========================================================

@router.get("/")
def listar_evidencias(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    query = db.query(Evidencia).join(Mantenimiento, Evidencia.mantenimiento_id == Mantenimiento.id)
    rol = str(usuario.rol or "").upper()
    if rol in {"COORDINADOR", "EMPRESA", "CLIENTE"}:
        query = query.filter(Mantenimiento.empresa_id == usuario.empresa_id)
    elif rol == "TECNICO":
        tecnico = db.query(Tecnico).filter(Tecnico.usuario_id == usuario.id).first()
        if not tecnico:
            return []
        query = query.filter(Mantenimiento.tecnico_id == tecnico.id)
    elif rol != "ADMIN":
        raise HTTPException(status_code=403, detail="Sin acceso a evidencias")
    evidencias = query.order_by(Evidencia.created_at.desc()).all()
    return [serializar_evidencia(e) for e in evidencias]


# ===========================================================
# LISTAR POR MANTENIMIENTO
# GET /evidencias/mantenimiento/{mantenimiento_id}
# ===========================================================

@router.get("/mantenimiento/{mantenimiento_id}")
def evidencias_por_mantenimiento(
    mantenimiento_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
    autorizar_mantenimiento(usuario, mantenimiento, db, escritura=False)
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
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    evidencias = (
        db.query(Evidencia)
        .filter(Evidencia.equipo_id == equipo_id)
        .order_by(Evidencia.created_at.desc())
        .all()
    )

    autorizadas = []
    for evidencia in evidencias:
        autorizar_evidencia(usuario, evidencia, db, escritura=False)
        autorizadas.append(serializar_evidencia(evidencia))
    return autorizadas


# ===========================================================
# SUBIR EVIDENCIA ADMIN / GENERAL
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
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    mantenimiento = (
        db.query(Mantenimiento)
        .filter(Mantenimiento.id == mantenimiento_id)
        .first()
    )

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
    autorizar_mantenimiento(usuario, mantenimiento, db, escritura=True)

    equipo_final_id = equipo_id or getattr(mantenimiento, "equipo_id", None)

    if not equipo_final_id:
        raise HTTPException(
            status_code=400,
            detail="No se pudo determinar el equipo de la evidencia",
        )

    try:
        saved = await save_secure_file(archivo, get_evidence_upload_config(db))

        nueva = Evidencia(
            mantenimiento_id=mantenimiento_id,
            equipo_id=equipo_final_id,
            tipo=tipo,
            descripcion=descripcion,
            nombre_original=archivo.filename,
            archivo_url=saved["public_url"],
        )

        db.add(nueva)
        db.commit()
        db.refresh(nueva)

        return {
            "message": "Archivo subido correctamente",
            "evidencia": serializar_evidencia(nueva),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error guardando evidencia: {str(e)}")


# ===========================================================
# DESCARGA / VISUALIZACIÓN SEGURA
# GET /evidencias/descargar/{filename}
# ===========================================================

@router.get("/{id}/archivo")
def descargar_archivo(
    id: UUID,
    expires: int,
    signature: str,
    db: Session = Depends(get_db),
):
    validar_firma_archivo(id, expires, signature)
    establecer_contexto_sistema(db)
    evidencia = db.query(Evidencia).filter(Evidencia.id == id).first()
    if not evidencia:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")
    filename = os.path.basename(evidencia.archivo_url or "")
    try:
        path = get_evidencia_path(filename)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")

    if not path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    media_type = mimetypes.guess_type(evidencia.nombre_original or filename)[0] or "application/octet-stream"
    return FileResponse(
        str(path),
        media_type=media_type,
        headers={
            "Cache-Control": "private, no-store",
            "Content-Disposition": f'inline; filename="{filename}"',
            "X-Content-Type-Options": "nosniff",
        },
    )


# ===========================================================
# ELIMINAR EVIDENCIA
# DELETE /evidencias/{id}
# ===========================================================

@router.delete("/{id}")
def eliminar_evidencia(
    id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    evidencia = db.query(Evidencia).filter(Evidencia.id == id).first()

    if not evidencia:
        raise HTTPException(status_code=404, detail="Evidencia no encontrada")

    autorizar_evidencia(usuario, evidencia, db, escritura=True)

    filename = os.path.basename(evidencia.archivo_url or "")

    if filename:
        try:
            path = get_evidencia_path(filename)
            if path.exists():
                path.unlink()
        except Exception:
            # Evita que un archivo faltante bloquee la eliminación de BD.
            pass

    db.delete(evidencia)
    db.commit()

    return {"message": "Evidencia eliminada correctamente"}
