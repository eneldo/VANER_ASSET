# =========================================================
# ROUTER DASHBOARD TÉCNICO PRO - SGA PRO
# Fase 25 - Portal Técnico operativo
#
# Objetivo:
# - El técnico solo ve sus mantenimientos asignados.
# - Puede cambiar estado: EN_PROCESO, PAUSADO, FINALIZADO.
# - Puede subir evidencias.
# - Evita errores por columnas faltantes usando getattr().
# =========================================================

import os
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.models.tecnico import Tecnico
from app.models.mantenimiento import Mantenimiento
from app.models.equipo import Equipo
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.categoria import Categoria
from app.models.equipo_hoja_vida import EquipoHojaVida
from app.models.evidencia import Evidencia


router = APIRouter(prefix="/dashboard-tecnico", tags=["Dashboard Técnico"])


# =========================================================
# CONFIGURACIÓN DE UPLOADS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "evidencias")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================================================
# HELPERS SEGUROS
# =========================================================

def safe_str(value):
    return str(value) if value is not None else None


def safe_get(obj, attr, default=None):
    return getattr(obj, attr, default) if obj else default


def get_fecha_fin(mantenimiento):
    """
    Tu modelo actual usa fecha_finalizacion.
    Algunos códigos anteriores usaban fecha_fin.
    Este helper soporta ambos nombres sin romper.
    """
    return (
        getattr(mantenimiento, "fecha_fin", None)
        or getattr(mantenimiento, "fecha_finalizacion", None)
    )


def parse_mantenimiento_id(value: str):
    """
    Soporta mantenimientos con ID entero o UUID.
    Así evitamos errores si la tabla está en int o uuid.
    """
    try:
        return int(value)
    except Exception:
        try:
            return UUID(value)
        except Exception:
            raise HTTPException(status_code=422, detail="ID de mantenimiento inválido")


def validar_usuario_tecnico(usuario_id: UUID, db: Session):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.rol != "TECNICO":
        raise HTTPException(status_code=403, detail="El usuario no tiene rol TECNICO")

    tecnico = db.query(Tecnico).filter(Tecnico.usuario_id == usuario.id).first()

    if not tecnico:
        raise HTTPException(
            status_code=404,
            detail="Este usuario técnico no tiene perfil creado en el módulo Técnicos"
        )

    return usuario, tecnico


def validar_mantenimiento_del_tecnico(usuario_id: UUID, mantenimiento_id: str, db: Session):
    usuario, tecnico = validar_usuario_tecnico(usuario_id, db)
    mantenimiento_pk = parse_mantenimiento_id(mantenimiento_id)

    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_pk
    ).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    if str(mantenimiento.tecnico_id) != str(tecnico.id):
        raise HTTPException(
            status_code=403,
            detail="No puedes modificar un mantenimiento que no está asignado a ti"
        )

    return usuario, tecnico, mantenimiento


def serializar_hoja_vida(hoja):
    if not hoja:
        return None

    data = {}
    for col in hoja.__table__.columns:
        value = getattr(hoja, col.name)
        data[col.name] = safe_str(value)

    return data


# =========================================================
# DASHBOARD POR USUARIO TÉCNICO
# =========================================================

@router.get("/usuario/{usuario_id}")
def dashboard_por_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    usuario, tecnico = validar_usuario_tecnico(usuario_id, db)

    mantenimientos = db.query(Mantenimiento).filter(
        Mantenimiento.tecnico_id == tecnico.id
    ).order_by(Mantenimiento.fecha_programada.desc()).all()

    return {
        "usuario": {
            "id": str(usuario.id),
            "nombre_completo": usuario.nombre_completo,
            "username": usuario.username,
            "email": usuario.email,
            "rol": usuario.rol,
        },
        "tecnico": {
            "id": str(tecnico.id),
            "documento": tecnico.documento,
            "telefono": tecnico.telefono,
            "especialidad": tecnico.especialidad,
            "cargo": tecnico.cargo,
        },
        "resumen": {
            "total_asignados": len(mantenimientos),
            "programados": len([m for m in mantenimientos if m.estado == "PROGRAMADO"]),
            "asignados": len([m for m in mantenimientos if m.estado == "ASIGNADO"]),
            "en_proceso": len([m for m in mantenimientos if m.estado == "EN_PROCESO"]),
            "pausados": len([m for m in mantenimientos if m.estado == "PAUSADO"]),
            "finalizados": len([m for m in mantenimientos if m.estado == "FINALIZADO"]),
        },
        "mantenimientos": [
            construir_card_mantenimiento(m, db) for m in mantenimientos
        ],
    }


# =========================================================
# DETALLE DEL MANTENIMIENTO
# =========================================================

@router.get("/mantenimiento/{mantenimiento_id}/detalle")
def detalle_mantenimiento_tecnico(
    mantenimiento_id: str,
    db: Session = Depends(get_db)
):
    mantenimiento_pk = parse_mantenimiento_id(mantenimiento_id)

    mantenimiento = db.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_pk
    ).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    equipo = db.query(Equipo).filter(Equipo.id == mantenimiento.equipo_id).first()

    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo asociado no encontrado")

    empresa = db.query(Empresa).filter(Empresa.id == equipo.empresa_id).first()
    sede = db.query(Sede).filter(Sede.id == equipo.sede_id).first()

    categoria = None
    if getattr(equipo, "categoria_id", None):
        categoria = db.query(Categoria).filter(Categoria.id == equipo.categoria_id).first()

    hoja_vida = db.query(EquipoHojaVida).filter(
        EquipoHojaVida.equipo_id == equipo.id
    ).first()

    evidencias = db.query(Evidencia).filter(
        Evidencia.mantenimiento_id == mantenimiento.id
    ).order_by(Evidencia.created_at.desc()).all()

    fecha_fin = get_fecha_fin(mantenimiento)

    return {
        "encabezado": {
            "empresa_nombre": safe_get(empresa, "nombre"),
            "empresa_logo_url": safe_get(empresa, "logo_url"),
            "sede_nombre": safe_get(sede, "nombre"),
        },
        "mantenimiento": {
            "id": str(mantenimiento.id),
            "tipo": mantenimiento.tipo,
            "estado": mantenimiento.estado,
            "descripcion": safe_get(mantenimiento, "descripcion"),
            "fecha_programada": safe_str(safe_get(mantenimiento, "fecha_programada")),
            "fecha_inicio": safe_str(safe_get(mantenimiento, "fecha_inicio")),
            "fecha_fin": safe_str(fecha_fin),
            "fecha_finalizacion": safe_str(fecha_fin),
            "estado_inicial": safe_get(mantenimiento, "estado_inicial"),
            "acciones_realizadas": safe_get(mantenimiento, "acciones_realizadas"),
            "resultado_final": safe_get(mantenimiento, "resultado_final"),
            "observaciones": safe_get(mantenimiento, "observaciones"),
            "observacion_estado": safe_get(mantenimiento, "observacion_estado"),
        },
        "equipo_basico": {
            "id": str(equipo.id),
            "nombre": equipo.nombre,
            "marca": equipo.marca,
            "modelo": equipo.modelo,
            "serie": equipo.serie,
            "ubicacion": equipo.ubicacion,
            "invima": equipo.invima,
            "codigo_id": equipo.codigo_id,
            "inventario": safe_get(equipo, "inventario"),
            "estado": equipo.estado,
            "criticidad": equipo.criticidad,
            "categoria": categoria.nombre if categoria else None,
        },
        "hoja_vida_tecnica": serializar_hoja_vida(hoja_vida),
        "evidencias": [
            {
                "id": str(e.id),
                "tipo": e.tipo,
                "archivo_url": e.archivo_url,
                "nombre_original": e.nombre_original,
                "descripcion": e.descripcion,
                "created_at": safe_str(e.created_at),
            }
            for e in evidencias
        ],
    }


# =========================================================
# CAMBIAR ESTADO DEL MANTENIMIENTO ASIGNADO
# =========================================================

@router.patch("/mantenimiento/{mantenimiento_id}/estado")
def cambiar_estado_mantenimiento(
    mantenimiento_id: str,
    usuario_id: UUID = Form(...),
    nuevo_estado: str = Form(...),
    observacion: str = Form(""),
    db: Session = Depends(get_db)
):
    _, _, mantenimiento = validar_mantenimiento_del_tecnico(
        usuario_id, mantenimiento_id, db
    )

    estados_validos = ["ASIGNADO", "EN_PROCESO", "PAUSADO", "FINALIZADO"]

    if nuevo_estado not in estados_validos:
        raise HTTPException(status_code=400, detail="Estado no permitido")

    mantenimiento.estado = nuevo_estado

    if nuevo_estado == "EN_PROCESO" and hasattr(mantenimiento, "fecha_inicio"):
        from datetime import datetime
        if not mantenimiento.fecha_inicio:
            mantenimiento.fecha_inicio = datetime.now()

    if nuevo_estado == "PAUSADO" and hasattr(mantenimiento, "fecha_pausa"):
        from datetime import datetime
        mantenimiento.fecha_pausa = datetime.now()

    if nuevo_estado == "FINALIZADO" and hasattr(mantenimiento, "fecha_finalizacion"):
        from datetime import datetime
        mantenimiento.fecha_finalizacion = datetime.now()

    if observacion:
        mantenimiento.observaciones = observacion

    db.commit()

    return {
        "message": "Estado actualizado correctamente",
        "estado": nuevo_estado,
    }


# =========================================================
# SUBIR EVIDENCIA DESDE PORTAL TÉCNICO
# =========================================================

@router.post("/mantenimiento/{mantenimiento_id}/evidencia")
async def subir_evidencia_tecnico(
    mantenimiento_id: str,
    usuario_id: UUID = Form(...),
    tipo: str = Form(...),
    descripcion: str = Form(""),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    _, _, mantenimiento = validar_mantenimiento_del_tecnico(
        usuario_id, mantenimiento_id, db
    )

    tipos_validos = ["ANTES", "DURANTE", "DESPUES", "SOPORTE"]

    if tipo not in tipos_validos:
        raise HTTPException(status_code=400, detail="Tipo de evidencia inválido")

    extension = archivo.filename.split(".")[-1].lower()

    if extension not in ["jpg", "jpeg", "png", "pdf"]:
        raise HTTPException(status_code=400, detail="Solo se permiten JPG, JPEG, PNG o PDF")

    nombre_archivo = f"{uuid.uuid4()}.{extension}"
    ruta = os.path.join(UPLOAD_DIR, nombre_archivo)

    contenido = await archivo.read()

    with open(ruta, "wb") as buffer:
        buffer.write(contenido)

    evidencia = Evidencia(
        mantenimiento_id=mantenimiento.id,
        equipo_id=mantenimiento.equipo_id,
        tipo=tipo,
        archivo_url=f"/uploads/evidencias/{nombre_archivo}",
        nombre_original=archivo.filename,
        descripcion=descripcion,
    )

    db.add(evidencia)
    db.commit()

    return {"message": "Evidencia subida correctamente"}


# =========================================================
# CONSTRUIR CARD PARA FRONTEND
# =========================================================

def construir_card_mantenimiento(mantenimiento: Mantenimiento, db: Session):
    equipo = db.query(Equipo).filter(Equipo.id == mantenimiento.equipo_id).first()

    empresa = None
    sede = None

    if equipo:
        empresa = db.query(Empresa).filter(Empresa.id == equipo.empresa_id).first()
        sede = db.query(Sede).filter(Sede.id == equipo.sede_id).first()

    fecha_fin = get_fecha_fin(mantenimiento)

    return {
        "mantenimiento_id": str(mantenimiento.id),
        "tipo": mantenimiento.tipo,
        "estado": mantenimiento.estado,
        "descripcion": safe_get(mantenimiento, "descripcion"),
        "fecha_programada": safe_str(safe_get(mantenimiento, "fecha_programada")),
        "fecha_inicio": safe_str(safe_get(mantenimiento, "fecha_inicio")),
        "fecha_fin": safe_str(fecha_fin),
        "fecha_finalizacion": safe_str(fecha_fin),
        "observaciones": safe_get(mantenimiento, "observaciones"),
        "observacion_estado": safe_get(mantenimiento, "observacion_estado"),
        "equipo": {
            "id": str(equipo.id) if equipo else None,
            "nombre": safe_get(equipo, "nombre"),
            "codigo_id": safe_get(equipo, "codigo_id"),
            "inventario": safe_get(equipo, "inventario"),
            "marca": safe_get(equipo, "marca"),
            "modelo": safe_get(equipo, "modelo"),
            "serie": safe_get(equipo, "serie"),
            "ubicacion": safe_get(equipo, "ubicacion"),
            "estado": safe_get(equipo, "estado"),
            "criticidad": safe_get(equipo, "criticidad"),
        },
        "empresa": {
            "nombre": safe_get(empresa, "nombre"),
            "logo_url": safe_get(empresa, "logo_url"),
        },
        "sede": {
            "nombre": safe_get(sede, "nombre"),
        },
    }