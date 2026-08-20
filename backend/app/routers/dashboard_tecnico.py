# =========================================================
# ROUTER DASHBOARD TÉCNICO PRO - SGAHolding
# Archivo: backend/app/routers/dashboard_tecnico.py
#
# Funciones:
# - Dashboard del técnico.
# - Detalle del mantenimiento.
# - Cambio de estado.
# - Guardar avance técnico.
# - Subir evidencias.
# - Histórico de mantenimientos finalizados del técnico.
# =========================================================

import os
import uuid
import json
from decimal import Decimal, InvalidOperation
from uuid import UUID
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
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
from app.models.ot_repuesto import OtRepuesto
from app.models.ot_incidencia import OtIncidencia
from app.services.evidencia_service import get_evidence_upload_config, save_secure_file
from app.services.mantenimiento_estado_service import validar_mantenimiento_editable
from app.routers.auth import obtener_usuario_actual
from app.routers.evidencias import crear_url_firmada


router = APIRouter(prefix="/dashboard-tecnico", tags=["Dashboard Técnico"])


# =========================================================
# CONFIGURACIÓN DE UPLOADS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "evidencias")
os.makedirs(UPLOAD_DIR, exist_ok=True)

TIPOS_EVIDENCIA_ETAPA = frozenset({"ANTES", "DURANTE", "DESPUES"})
MAX_EVIDENCIAS_POR_ETAPA = 4


# =========================================================
# HELPERS
# =========================================================

def safe_str(value):
    return str(value) if value is not None else None


def safe_get(obj, attr, default=None):
    return getattr(obj, attr, default) if obj else default

def serializar_evidencia_tecnico(e: Evidencia):
    archivo = getattr(e, "archivo_url", None) or ""
    filename = os.path.basename(archivo)

    if archivo.startswith("/uploads/"):
        archivo_url = archivo
    else:
        archivo_url = f"/uploads/evidencias/{filename}" if filename else ""

    return {
        "id": str(e.id),
        "mantenimiento_id": str(e.mantenimiento_id) if e.mantenimiento_id else None,
        "equipo_id": str(e.equipo_id) if e.equipo_id else None,
        "tipo": e.tipo,
        "descripcion": e.descripcion,
        "nombre_original": e.nombre_original,
        "archivo_url": crear_url_firmada(e.id, filename),
        "filename": filename,
        "created_at": safe_str(e.created_at),
    }



def get_fecha_fin(mantenimiento):
    return (
        getattr(mantenimiento, "fecha_fin", None)
        or getattr(mantenimiento, "fecha_finalizacion", None)
    )


def parse_mantenimiento_id(value: str):
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


def validar_identidad_tecnico(usuario_id: UUID, usuario_actual: Usuario):
    """Impide suplantar otro técnico enviando su UUID en la ruta o formulario."""
    if str(getattr(usuario_actual, "rol", "")).upper() != "TECNICO":
        raise HTTPException(status_code=403, detail="Endpoint exclusivo para técnicos")
    if str(usuario_actual.id) != str(usuario_id):
        raise HTTPException(status_code=403, detail="No puedes operar como otro técnico")


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


def aplicar_estado_operativo(mantenimiento, nuevo_estado: str):
    estados_validos = ["ASIGNADO", "PROGRAMADO", "EN_PROCESO", "PAUSADO", "FINALIZADO"]

    if nuevo_estado not in estados_validos:
        raise HTTPException(status_code=400, detail="Estado no permitido")

    mantenimiento.estado = nuevo_estado

    if nuevo_estado == "EN_PROCESO":
        if hasattr(mantenimiento, "fecha_inicio") and not mantenimiento.fecha_inicio:
            mantenimiento.fecha_inicio = datetime.now()

    if nuevo_estado == "PAUSADO":
        if hasattr(mantenimiento, "fecha_pausa"):
            mantenimiento.fecha_pausa = datetime.now()

    if nuevo_estado == "FINALIZADO":
        if hasattr(mantenimiento, "fecha_finalizacion"):
            mantenimiento.fecha_finalizacion = datetime.now()
        if hasattr(mantenimiento, "fecha_fin"):
            mantenimiento.fecha_fin = datetime.now()


def requisitos_finalizacion(evidencias, mantenimiento=None):
    """Retorna los requisitos faltantes para cerrar una OT."""
    tipos = {str(getattr(e, "tipo", "") or "").upper() for e in evidencias}
    faltantes = []
    for tipo, etiqueta in (("ANTES", "foto inicial"), ("DURANTE", "foto del proceso"), ("DESPUES", "foto final")):
        if tipo not in tipos:
            faltantes.append(etiqueta)

    return faltantes


def validar_limite_evidencias_por_etapa(tipo, cantidad_existente):
    tipo_normalizado = str(tipo or "").strip().upper()
    if (
        tipo_normalizado in TIPOS_EVIDENCIA_ETAPA
        and cantidad_existente >= MAX_EVIDENCIAS_POR_ETAPA
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Solo puedes cargar hasta {MAX_EVIDENCIAS_POR_ETAPA} evidencias "
                f"de tipo {tipo_normalizado}."
            ),
        )


def validar_finalizacion(db: Session, mantenimiento: Mantenimiento):
    evidencias = db.query(Evidencia).filter(Evidencia.mantenimiento_id == mantenimiento.id).all()
    faltantes = requisitos_finalizacion(evidencias, mantenimiento)
    if faltantes:
        raise HTTPException(
            status_code=409,
            detail={
                "codigo": "OT_INCOMPLETA",
                "mensaje": "No se puede finalizar la orden de trabajo.",
                "faltantes": faltantes,
            },
        )


def normalizar_repuestos(raw):
    try:
        items = json.loads(raw or "[]") if isinstance(raw, str) else (raw or [])
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Formato de repuestos inválido")
    if not isinstance(items, list) or len(items) > 50:
        raise HTTPException(status_code=422, detail="Se permiten máximo 50 repuestos por OT")
    resultado = []
    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(status_code=422, detail="Cada repuesto debe ser un objeto")
        descripcion = str(item.get("descripcion", "")).strip()
        try:
            cantidad = Decimal(str(item.get("cantidad", "0")))
            costo = item.get("costo_unitario")
            costo = Decimal(str(costo)) if costo not in (None, "") else None
        except (InvalidOperation, TypeError):
            raise HTTPException(status_code=422, detail="Cantidad o costo de repuesto inválido")
        if not descripcion or cantidad <= 0 or (costo is not None and costo < 0):
            raise HTTPException(status_code=422, detail="Cada repuesto requiere descripción y cantidad positiva")
        resultado.append({
            "descripcion": descripcion[:250], "referencia": str(item.get("referencia", "")).strip()[:120] or None,
            "cantidad": cantidad, "unidad": str(item.get("unidad", "UNIDAD")).strip().upper()[:30] or "UNIDAD",
            "costo_unitario": costo,
        })
    return resultado


def normalizar_incidencias(raw):
    try:
        items = json.loads(raw or "[]") if isinstance(raw, str) else (raw or [])
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="Formato de incidencias inválido")
    if not isinstance(items, list) or len(items) > 50:
        raise HTTPException(status_code=422, detail="Se permiten máximo 50 incidencias por OT")
    resultado = []
    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(status_code=422, detail="Cada incidencia debe ser un objeto")
        descripcion = str(item.get("descripcion", "")).strip()
        severidad = str(item.get("severidad", "MEDIA")).strip().upper()
        if not descripcion or severidad not in {"BAJA", "MEDIA", "ALTA", "CRITICA"}:
            raise HTTPException(status_code=422, detail="Incidencia sin descripción o severidad inválida")
        resultado.append({
            "tipo": str(item.get("tipo", "TECNICA")).strip().upper()[:40] or "TECNICA",
            "severidad": severidad, "descripcion": descripcion[:4000], "resuelta": bool(item.get("resuelta", False)),
        })
    return resultado


def guardar_detalles_operativos(db, mantenimiento, repuestos, incidencias):
    empresa_id = mantenimiento.empresa_id
    if not empresa_id:
        equipo = db.query(Equipo).filter(Equipo.id == mantenimiento.equipo_id).first()
        empresa_id = getattr(equipo, "empresa_id", None)
    if not empresa_id:
        raise HTTPException(status_code=409, detail="La OT no tiene tenant asociado")
    db.query(OtRepuesto).filter(OtRepuesto.mantenimiento_id == mantenimiento.id).delete(synchronize_session=False)
    db.query(OtIncidencia).filter(OtIncidencia.mantenimiento_id == mantenimiento.id).delete(synchronize_session=False)
    for item in repuestos:
        db.add(OtRepuesto(empresa_id=empresa_id, mantenimiento_id=mantenimiento.id, **item))
    for item in incidencias:
        db.add(OtIncidencia(empresa_id=empresa_id, mantenimiento_id=mantenimiento.id, **item))


# =========================================================
# DASHBOARD POR USUARIO TÉCNICO
# =========================================================

@router.get("/usuario/{usuario_id}")
def dashboard_por_usuario(
    usuario_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    validar_identidad_tecnico(usuario_id, usuario_actual)
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
# HISTÓRICO DEL TÉCNICO
# =========================================================

@router.get("/usuario/{usuario_id}/historico")
def historico_tecnico(
    usuario_id: UUID,
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    empresa: str | None = Query(default=None),
    sede: str | None = Query(default=None),
    equipo: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """
    Devuelve mantenimientos FINALIZADOS del técnico.
    Permite filtros por fechas, empresa, sede y equipo.
    """

    validar_identidad_tecnico(usuario_id, usuario_actual)
    usuario, tecnico = validar_usuario_tecnico(usuario_id, db)

    query = db.query(Mantenimiento).filter(
        Mantenimiento.tecnico_id == tecnico.id,
        Mantenimiento.estado == "FINALIZADO"
    )

    if desde:
        query = query.filter(Mantenimiento.fecha_finalizacion >= desde)

    if hasta:
        query = query.filter(Mantenimiento.fecha_finalizacion <= hasta)

    mantenimientos = query.order_by(
        Mantenimiento.fecha_finalizacion.desc()
    ).all()

    resultado = []

    for m in mantenimientos:
        item = construir_card_mantenimiento(m, db)

        empresa_nombre = (item.get("empresa") or {}).get("nombre") or ""
        sede_nombre = (item.get("sede") or {}).get("nombre") or ""
        equipo_nombre = ((item.get("equipo") or {}).get("nombre") or "")

        if empresa and empresa.lower() not in empresa_nombre.lower():
            continue

        if sede and sede.lower() not in sede_nombre.lower():
            continue

        if equipo and equipo.lower() not in equipo_nombre.lower():
            continue

        resultado.append(item)

    return {
        "usuario": {
            "id": str(usuario.id),
            "nombre_completo": usuario.nombre_completo,
            "rol": usuario.rol,
        },
        "tecnico": {
            "id": str(tecnico.id),
            "documento": tecnico.documento,
            "cargo": tecnico.cargo,
            "especialidad": tecnico.especialidad,
        },
        "total": len(resultado),
        "historico": resultado,
    }


# =========================================================
# DETALLE DEL MANTENIMIENTO
# =========================================================

@router.get("/mantenimiento/{mantenimiento_id}/detalle")
def detalle_mantenimiento_tecnico(
    mantenimiento_id: str,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _, tecnico, mantenimiento = validar_mantenimiento_del_tecnico(
        usuario_actual.id, mantenimiento_id, db
    )

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
    repuestos = db.query(OtRepuesto).filter(OtRepuesto.mantenimiento_id == mantenimiento.id).all()
    incidencias = db.query(OtIncidencia).filter(OtIncidencia.mantenimiento_id == mantenimiento.id).all()

    fecha_fin = get_fecha_fin(mantenimiento)

    return {
        "encabezado": {
            "empresa_nombre": safe_get(empresa, "nombre"),
            "empresa_logo_url": safe_get(empresa, "logo_url"),
            "sede_nombre": safe_get(sede, "nombre"),
        },
        'tecnico': {
            'id': str(tecnico.id),
            'nombre_completo': safe_get(safe_get(tecnico, 'usuario'), 'nombre_completo'),
            'especialidad': safe_get(tecnico, 'especialidad'),
            'cargo': safe_get(tecnico, 'cargo'),
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
            "estado_inicial_equipo": safe_get(mantenimiento, "estado_inicial_equipo"),
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
            serializar_evidencia_tecnico(e)
            for e in evidencias
        ],
        "repuestos": [{
            "id": str(item.id), "descripcion": item.descripcion, "referencia": item.referencia,
            "cantidad": float(item.cantidad), "unidad": item.unidad,
            "costo_unitario": float(item.costo_unitario) if item.costo_unitario is not None else None,
        } for item in repuestos],
        "incidencias": [{
            "id": str(item.id), "tipo": item.tipo, "severidad": item.severidad,
            "descripcion": item.descripcion, "resuelta": item.resuelta,
        } for item in incidencias],
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
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    validar_identidad_tecnico(usuario_id, usuario_actual)
    _, _, mantenimiento = validar_mantenimiento_del_tecnico(
        usuario_id, mantenimiento_id, db
    )

    if nuevo_estado == "FINALIZADO":
        validar_finalizacion(db, mantenimiento)
    aplicar_estado_operativo(mantenimiento, nuevo_estado)

    if observacion:
        mantenimiento.observaciones = observacion

    db.commit()

    return {
        "message": "Estado actualizado correctamente",
        "estado": nuevo_estado,
    }


# =========================================================
# GUARDAR AVANCE TÉCNICO
# =========================================================

@router.patch("/mantenimiento/{mantenimiento_id}/avance")
def guardar_avance_tecnico(
    mantenimiento_id: str,
    usuario_id: UUID = Form(...),
    estado_inicial: str = Form(""),
    acciones_realizadas: str = Form(""),
    resultado_final: str = Form(""),
    observaciones: str = Form(""),
    repuestos_json: str = Form("[]"),
    incidencias_json: str = Form("[]"),
    nuevo_estado: str = Form(""),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    validar_identidad_tecnico(usuario_id, usuario_actual)
    _, _, mantenimiento = validar_mantenimiento_del_tecnico(
        usuario_id, mantenimiento_id, db
    )
    validar_mantenimiento_editable(mantenimiento)
    repuestos = normalizar_repuestos(repuestos_json)
    incidencias = normalizar_incidencias(incidencias_json)

    if hasattr(mantenimiento, "estado_inicial"):
        mantenimiento.estado_inicial = estado_inicial

    if hasattr(mantenimiento, "estado_inicial_equipo"):
        mantenimiento.estado_inicial_equipo = estado_inicial

    if hasattr(mantenimiento, "acciones_realizadas"):
        mantenimiento.acciones_realizadas = acciones_realizadas

    if hasattr(mantenimiento, "resultado_final"):
        mantenimiento.resultado_final = resultado_final

    if hasattr(mantenimiento, "observaciones"):
        mantenimiento.observaciones = observaciones

    guardar_detalles_operativos(db, mantenimiento, repuestos, incidencias)

    if nuevo_estado:
        if nuevo_estado == "FINALIZADO":
            validar_finalizacion(db, mantenimiento)
        aplicar_estado_operativo(mantenimiento, nuevo_estado)

    db.commit()
    db.refresh(mantenimiento)

    return {
        "message": "Avance técnico guardado correctamente",
        "mantenimiento": {
            "id": str(mantenimiento.id),
            "estado": mantenimiento.estado,
            "estado_inicial": safe_get(mantenimiento, "estado_inicial"),
            "acciones_realizadas": safe_get(mantenimiento, "acciones_realizadas"),
            "resultado_final": safe_get(mantenimiento, "resultado_final"),
            "observaciones": safe_get(mantenimiento, "observaciones"),
            "repuestos": len(repuestos),
            "incidencias": len(incidencias),
            "fecha_inicio": safe_str(safe_get(mantenimiento, "fecha_inicio")),
            "fecha_pausa": safe_str(safe_get(mantenimiento, "fecha_pausa")),
            "fecha_finalizacion": safe_str(safe_get(mantenimiento, "fecha_finalizacion")),
        }
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
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    validar_identidad_tecnico(usuario_id, usuario_actual)
    _, _, mantenimiento = validar_mantenimiento_del_tecnico(
        usuario_id, mantenimiento_id, db
    )
    validar_mantenimiento_editable(mantenimiento)

    tipo = tipo.strip().upper()
    tipos_validos = ["ANTES", "DURANTE", "DESPUES", "SOPORTE"]

    if tipo not in tipos_validos:
        raise HTTPException(status_code=400, detail="Tipo de evidencia inválido")

    if tipo in {"ANTES", "DURANTE", "DESPUES"} and not descripcion.strip():
        raise HTTPException(status_code=422, detail="El comentario de la evidencia es obligatorio")

    tipos_existentes = [
        str(row[0]).upper()
        for row in db.query(Evidencia.tipo).filter(
            Evidencia.mantenimiento_id == mantenimiento.id
        ).all()
    ]
    existentes = set(tipos_existentes)
    validar_limite_evidencias_por_etapa(tipo, tipos_existentes.count(tipo))
    if tipo == "DURANTE" and "ANTES" not in existentes:
        raise HTTPException(status_code=409, detail="Primero debes cargar la foto del estado inicial")
    if tipo == "DESPUES" and not {"ANTES", "DURANTE"}.issubset(existentes):
        raise HTTPException(
            status_code=409,
            detail="Debes completar las fotos inicial y de proceso antes de la foto final",
        )

    try:
        saved = await save_secure_file(archivo, get_evidence_upload_config(db))

        evidencia = Evidencia(
            mantenimiento_id=mantenimiento.id,
            equipo_id=mantenimiento.equipo_id,
            tipo=tipo,
            archivo_url=saved["public_url"],
            nombre_original=archivo.filename,
            descripcion=descripcion,
        )

        db.add(evidencia)
        db.commit()
        db.refresh(evidencia)

        return {
            "message": "Evidencia subida correctamente",
            "evidencia": serializar_evidencia_tecnico(evidencia),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo subir la evidencia: {str(e)}")


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
        "estado_inicial": safe_get(mantenimiento, "estado_inicial"),
        "acciones_realizadas": safe_get(mantenimiento, "acciones_realizadas"),
        "resultado_final": safe_get(mantenimiento, "resultado_final"),
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
