# ============================================================
# ROUTER: Mantenimientos PRO
# Archivo: backend/app/routers/mantenimientos.py
# CRUD + asignación técnico + estados + eliminación real
# Permite crear mantenimiento CON o SIN fecha programada
# ============================================================

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import cast, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.mantenimiento import Mantenimiento
from app.models.hist_mantenimiento import HistMantenimiento
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.models.equipo import Equipo
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.services.mantenimiento_estado_service import aplicar_reapertura

try:
    from app.models.evidencia import Evidencia
except Exception:
    Evidencia = None

from app.schemas.mantenimiento import (
    MantenimientoCreate,
    MantenimientoUpdate,
    AsignarTecnicoRequest,
    CambiarEstadoRequest,
    HistMantenimientoOut,
)


router = APIRouter(prefix="/mantenimientos", tags=["Mantenimientos PRO"])


# ============================================================
# ESTADOS PERMITIDOS
# ============================================================

ESTADOS_PERMITIDOS = [
    "PROGRAMADO",
    "ASIGNADO",
    "EN_PROCESO",
    "PAUSADO",
    "FINALIZADO",
    "ANULADO",
]

TRANSICIONES_VALIDAS = {
    "PROGRAMADO": ["ASIGNADO", "ANULADO"],
    "ASIGNADO": ["EN_PROCESO", "ANULADO"],
    "EN_PROCESO": ["PAUSADO", "FINALIZADO", "ANULADO"],
    "PAUSADO": ["EN_PROCESO", "ANULADO"],
    "FINALIZADO": ["EN_PROCESO"],
    "ANULADO": [],
}


# ============================================================
# HELPERS
# ============================================================

def str_id(value):
    """
    Convierte UUID/int a string.
    """
    return str(value) if value is not None else None


def buscar_por_id_string(db: Session, modelo, valor_id):
    """
    Busca por ID usando cast a texto.
    Sirve para UUID o enteros.
    """
    return (
        db.query(modelo)
        .filter(cast(modelo.id, String) == str(valor_id))
        .first()
    )


def normalizar_fecha_programada(fecha):
    """
    Permite guardar mantenimiento CON o SIN fecha.

    - Si viene None o vacío: retorna None.
    - Si viene datetime: retorna date().
    - Si viene string ISO: intenta convertirlo.
    """

    if not fecha:
        return None

    try:
        if isinstance(fecha, datetime):
            return fecha

        if isinstance(fecha, str):
            return datetime.fromisoformat(fecha.replace("Z", ""))

        if hasattr(fecha, "year") and hasattr(fecha, "month") and hasattr(fecha, "day"):
            return datetime.combine(fecha, datetime.min.time())

        return fecha

    except Exception:
        return None


def sincronizar_tenant_desde_equipo(mantenimiento: Mantenimiento, equipo: Equipo):
    empresa_id = getattr(equipo, "empresa_id", None)
    sede_id = getattr(equipo, "sede_id", None)

    if not empresa_id or not sede_id:
        raise HTTPException(
            status_code=409,
            detail="El equipo debe tener empresa y sede antes de crear el mantenimiento.",
        )

    mantenimiento.empresa_id = empresa_id
    mantenimiento.sede_id = sede_id
    return mantenimiento


def registrar_historial(
    db: Session,
    mantenimiento_id,
    estado_anterior: str | None,
    estado_nuevo: str,
    tecnico_id=None,
    observacion: str | None = None,
    creado_por: str | None = "Sistema",
):
    """
    Registra trazabilidad del mantenimiento.
    """

    evento = HistMantenimiento(
        mantenimiento_id=mantenimiento_id,
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        tecnico_id=tecnico_id,
        observacion=observacion,
        creado_por=creado_por,
    )

    db.add(evento)
    return evento


def obtener_datos_relacionados(m: Mantenimiento, db: Session):
    """
    Obtiene equipo, empresa, sede, técnico y usuario técnico.
    """

    equipo = None
    empresa = None
    sede = None
    tecnico = None
    usuario_tecnico = None

    if getattr(m, "equipo_id", None):
        equipo = (
            db.query(Equipo)
            .filter(cast(Equipo.id, String) == str(m.equipo_id))
            .first()
        )

    if equipo:
        if getattr(equipo, "empresa_id", None):
            empresa = (
                db.query(Empresa)
                .filter(cast(Empresa.id, String) == str(equipo.empresa_id))
                .first()
            )

        if getattr(equipo, "sede_id", None):
            sede = (
                db.query(Sede)
                .filter(cast(Sede.id, String) == str(equipo.sede_id))
                .first()
            )

    if getattr(m, "tecnico_id", None):
        tecnico = (
            db.query(Tecnico)
            .filter(cast(Tecnico.id, String) == str(m.tecnico_id))
            .first()
        )

        if tecnico and getattr(tecnico, "usuario_id", None):
            usuario_tecnico = (
                db.query(Usuario)
                .filter(cast(Usuario.id, String) == str(tecnico.usuario_id))
                .first()
            )

    return equipo, empresa, sede, tecnico, usuario_tecnico


def mantenimiento_dict(m: Mantenimiento, db: Session):
    """
    Respuesta enriquecida para frontend.
    """

    equipo, empresa, sede, tecnico, usuario_tecnico = obtener_datos_relacionados(
        m, db
    )

    tecnico_nombre = None

    if usuario_tecnico:
        tecnico_nombre = usuario_tecnico.nombre_completo
    elif tecnico:
        tecnico_nombre = (
            getattr(tecnico, "nombre", None)
            or getattr(tecnico, "especialidad", None)
            or f"Técnico {str_id(tecnico.id)}"
        )

    return {
        "id": str_id(m.id),
        "equipo_id": str_id(m.equipo_id),
        "empresa_id": str_id(getattr(equipo, "empresa_id", None)) if equipo else None,
        "sede_id": str_id(getattr(equipo, "sede_id", None)) if equipo else None,
        "tipo": m.tipo,
        "descripcion": m.descripcion,
        "prioridad": m.prioridad,
        "fecha_programada": m.fecha_programada,
        "fecha_inicio_programada": m.fecha_inicio_programada,
        "fecha_fin_programada": m.fecha_fin_programada,
        "estado": m.estado,
        "tecnico_id": str_id(m.tecnico_id),
        "responsable_id": str_id(m.responsable_id),
        "fecha_asignacion": m.fecha_asignacion,
        "fecha_inicio": m.fecha_inicio,
        "fecha_pausa": m.fecha_pausa,
        "fecha_finalizacion": m.fecha_finalizacion,
        "observaciones": m.observaciones,
        "estado_inicial": m.estado_inicial,
        "estado_inicial_equipo": m.estado_inicial_equipo,
        "acciones_realizadas": m.acciones_realizadas,
        "resultado_final": m.resultado_final,
        "falla_incidencia": m.falla_incidencia,
        "diagnostico": m.diagnostico,
        "trabajo_realizado": m.trabajo_realizado,
        "repuestos": m.repuestos,
        "latitud": m.latitud,
        "longitud": m.longitud,
        "observacion_estado": m.observacion_estado,
        "motivo_anulacion": m.motivo_anulacion,
        "costo": m.costo,
        "costo_mano_obra": m.costo_mano_obra,
        "costo_repuestos": m.costo_repuestos,
        "costo_total": m.costo_total,
        "evidencia_fotos": m.evidencia_fotos,
        "evidencia_documentos": m.evidencia_documentos,
        "solucion": m.solucion,
        "cerrado": m.cerrado,
        "fecha_cierre": m.fecha_cierre,
        "tipo_movimiento": m.tipo_movimiento,
        "activo_afectado_id": str_id(m.activo_afectado_id) if m.activo_afectado_id else None,
        "activo_afectado_tipo": m.activo_afectado_tipo,
        "creado_en": m.creado_en,
        "actualizado_en": m.actualizado_en,
        "equipo_nombre": getattr(equipo, "nombre", None) if equipo else None,
        "equipo_codigo": getattr(equipo, "codigo_id", None) if equipo else None,
        "equipo_serie": getattr(equipo, "serie", None) if equipo else None,
        "equipo_ubicacion": getattr(equipo, "ubicacion", None) if equipo else None,
        "empresa_nombre": getattr(empresa, "nombre", None) if empresa else None,
        "sede_nombre": getattr(sede, "nombre", None) if sede else None,
        "tecnico_nombre": tecnico_nombre,
    }


# ============================================================
# LISTAR MANTENIMIENTOS
# ============================================================

@router.get("/")
def listar_mantenimientos(db: Session = Depends(get_db)):
    """
    Lista mantenimientos enriquecidos.
    """

    mantenimientos = (
        db.query(Mantenimiento)
        .order_by(Mantenimiento.id.desc())
        .all()
    )

    return [mantenimiento_dict(m, db) for m in mantenimientos]


# ============================================================
# OBTENER MANTENIMIENTO
# ============================================================

@router.get("/{mantenimiento_id}")
def obtener_mantenimiento(
    mantenimiento_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene mantenimiento por ID con historial.
    """

    mantenimiento = (
        db.query(Mantenimiento)
        .options(joinedload(Mantenimiento.historial))
        .filter(cast(Mantenimiento.id, String) == str(mantenimiento_id))
        .first()
    )

    if not mantenimiento:
        raise HTTPException(
            status_code=404,
            detail="Mantenimiento no encontrado."
        )

    data = mantenimiento_dict(mantenimiento, db)

    data["historial"] = [
        {
            "id": str_id(h.id),
            "mantenimiento_id": str_id(h.mantenimiento_id),
            "estado_anterior": h.estado_anterior,
            "estado_nuevo": h.estado_nuevo,
            "tecnico_id": str_id(h.tecnico_id),
            "observacion": h.observacion,
            "creado_por": h.creado_por,
            "fecha_evento": h.fecha_evento,
        }
        for h in getattr(mantenimiento, "historial", [])
    ]

    return data


# ============================================================
# CREAR MANTENIMIENTO
# ============================================================

@router.post("/")
def crear_mantenimiento(
    payload: MantenimientoCreate,
    db: Session = Depends(get_db)
):
    """
    Crea mantenimiento en estado PROGRAMADO.

    Permite:
    - Crear con fecha programada.
    - Crear sin fecha programada, siempre que la BD permita NULL.
    """

    equipo = (
        db.query(Equipo)
        .filter(cast(Equipo.id, String) == str(payload.equipo_id))
        .first()
    )

    if not equipo:
        raise HTTPException(
            status_code=404,
            detail="Equipo no encontrado."
        )

    fecha_programada = normalizar_fecha_programada(payload.fecha_programada)

    nuevo = Mantenimiento(
        equipo_id=payload.equipo_id,
        tipo=payload.tipo,
        descripcion=(
            payload.descripcion
            or "Mantenimiento registrado desde bitácora profesional."
        ),
        prioridad=payload.prioridad or "MEDIA",
        fecha_programada=fecha_programada,
        fecha_inicio_programada=payload.fecha_inicio_programada,
        fecha_fin_programada=payload.fecha_fin_programada,
        observaciones=payload.observaciones,
        estado_inicial_equipo=payload.estado_inicial_equipo,
        acciones_realizadas=payload.acciones_realizadas,
        resultado_final=payload.resultado_final,
        falla_incidencia=payload.falla_incidencia,
        diagnostico=payload.diagnostico,
        trabajo_realizado=payload.trabajo_realizado,
        repuestos=payload.repuestos,
        latitud=payload.latitud,
        longitud=payload.longitud,
        costo=payload.costo,
        costo_mano_obra=payload.costo_mano_obra,
        costo_repuestos=payload.costo_repuestos,
        costo_total=payload.costo_total,
        evidencia_fotos=payload.evidencia_fotos,
        evidencia_documentos=payload.evidencia_documentos,
        solucion=payload.solucion,
        cerrado=payload.cerrado or False,
        responsable_id=payload.responsable_id,
        tipo_movimiento=payload.tipo_movimiento,
        activo_afectado_id=payload.activo_afectado_id,
        activo_afectado_tipo=payload.activo_afectado_tipo,
        estado="PROGRAMADO",
    )
    sincronizar_tenant_desde_equipo(nuevo, equipo)

    try:
        db.add(nuevo)
        db.flush()

        registrar_historial(
            db=db,
            mantenimiento_id=nuevo.id,
            estado_anterior=None,
            estado_nuevo="PROGRAMADO",
            tecnico_id=None,
            observacion="Mantenimiento creado en estado PROGRAMADO.",
            creado_por="Sistema",
        )

        db.commit()
        db.refresh(nuevo)

        return mantenimiento_dict(nuevo, db)

    except IntegrityError as error:
        db.rollback()

        error_text = str(error).lower()

        if "fecha_programada" in error_text and "not null" in error_text:
            raise HTTPException(
                status_code=400,
                detail=(
                    "La base de datos todavía tiene fecha_programada como NOT NULL. "
                    "Ejecute en PostgreSQL: "
                    "ALTER TABLE mantenimientos ALTER COLUMN fecha_programada DROP NOT NULL;"
                )
            )

        raise HTTPException(
            status_code=400,
            detail="No se pudo guardar el mantenimiento por restricción de base de datos."
        )


# ============================================================
# ACTUALIZAR MANTENIMIENTO
# ============================================================

@router.put("/{mantenimiento_id}")
def actualizar_mantenimiento(
    mantenimiento_id: str,
    payload: MantenimientoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza mantenimiento.
    """

    mantenimiento = buscar_por_id_string(
        db,
        Mantenimiento,
        mantenimiento_id
    )

    if not mantenimiento:
        raise HTTPException(
            status_code=404,
            detail="Mantenimiento no encontrado."
        )

    datos = payload.model_dump(exclude_unset=True)

    equipo = None

    if "equipo_id" in datos:
        equipo = (
            db.query(Equipo)
            .filter(cast(Equipo.id, String) == str(datos["equipo_id"]))
            .first()
        )

        if not equipo:
            raise HTTPException(
                status_code=404,
                detail="Equipo no encontrado."
            )

    if "fecha_programada" in datos:
        datos["fecha_programada"] = normalizar_fecha_programada(
            datos["fecha_programada"]
        )

    for campo, valor in datos.items():
        setattr(mantenimiento, campo, valor)

    if not equipo:
        equipo = (
            db.query(Equipo)
            .filter(cast(Equipo.id, String) == str(mantenimiento.equipo_id))
            .first()
        )

    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo asociado no encontrado.")

    sincronizar_tenant_desde_equipo(mantenimiento, equipo)

    mantenimiento.actualizado_en = datetime.now()

    try:
        db.commit()
        db.refresh(mantenimiento)

        return mantenimiento_dict(mantenimiento, db)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="No se pudo actualizar el mantenimiento."
        )


# ============================================================
# ELIMINAR MANTENIMIENTO
# ============================================================

@router.delete("/{mantenimiento_id}")
def eliminar_mantenimiento(
    mantenimiento_id: str,
    db: Session = Depends(get_db)
):
    """
    Elimina definitivamente el mantenimiento.
    """

    mantenimiento = buscar_por_id_string(
        db,
        Mantenimiento,
        mantenimiento_id
    )

    if not mantenimiento:
        raise HTTPException(
            status_code=404,
            detail="Mantenimiento no encontrado."
        )

    try:
        if Evidencia is not None:
            db.query(Evidencia).filter(
                cast(Evidencia.mantenimiento_id, String) == str(mantenimiento.id)
            ).delete(synchronize_session=False)

        db.query(HistMantenimiento).filter(
            cast(HistMantenimiento.mantenimiento_id, String) == str(mantenimiento.id)
        ).delete(synchronize_session=False)

        db.delete(mantenimiento)
        db.commit()

        return {
            "ok": True,
            "mensaje": "Mantenimiento eliminado correctamente."
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "No se pudo eliminar el mantenimiento porque tiene relaciones activas."
            )
        )


# ============================================================
# ASIGNAR TÉCNICO
# ============================================================

@router.patch("/{mantenimiento_id}/asignar-tecnico")
def asignar_tecnico(
    mantenimiento_id: str,
    payload: AsignarTecnicoRequest,
    db: Session = Depends(get_db)
):
    """
    Asigna técnico a mantenimiento.
    """

    mantenimiento = buscar_por_id_string(
        db,
        Mantenimiento,
        mantenimiento_id
    )

    if not mantenimiento:
        raise HTTPException(
            status_code=404,
            detail="Mantenimiento no encontrado."
        )

    tecnico = (
        db.query(Tecnico)
        .filter(cast(Tecnico.id, String) == str(payload.tecnico_id))
        .first()
    )

    if not tecnico:
        raise HTTPException(
            status_code=404,
            detail="Técnico no encontrado."
        )

    equipo = (
        db.query(Equipo)
        .filter(cast(Equipo.id, String) == str(mantenimiento.equipo_id))
        .first()
    )

    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo asociado no encontrado.")

    usuario_tecnico = (
        db.query(Usuario)
        .filter(cast(Usuario.id, String) == str(tecnico.usuario_id))
        .first()
    )

    if not usuario_tecnico or not usuario_tecnico.activo:
        raise HTTPException(status_code=400, detail="El usuario técnico no está activo.")

    if str(usuario_tecnico.empresa_id) != str(equipo.empresa_id):
        raise HTTPException(
            status_code=400,
            detail="El técnico y el equipo deben pertenecer a la misma empresa.",
        )

    sincronizar_tenant_desde_equipo(mantenimiento, equipo)

    if mantenimiento.estado in ["FINALIZADO", "ANULADO"]:
        raise HTTPException(
            status_code=400,
            detail="No se puede asignar técnico a un mantenimiento finalizado o anulado."
        )

    estado_anterior = mantenimiento.estado

    mantenimiento.tecnico_id = payload.tecnico_id
    mantenimiento.estado = "ASIGNADO"
    mantenimiento.fecha_asignacion = datetime.now()
    mantenimiento.observacion_estado = payload.observacion
    mantenimiento.actualizado_en = datetime.now()

    registrar_historial(
        db=db,
        mantenimiento_id=mantenimiento.id,
        estado_anterior=estado_anterior,
        estado_nuevo="ASIGNADO",
        tecnico_id=payload.tecnico_id,
        observacion=payload.observacion,
        creado_por=payload.creado_por,
    )

    db.commit()
    db.refresh(mantenimiento)

    return mantenimiento_dict(mantenimiento, db)


# ============================================================
# CAMBIAR ESTADO
# ============================================================

@router.patch("/{mantenimiento_id}/cambiar-estado")
def cambiar_estado(
    mantenimiento_id: str,
    payload: CambiarEstadoRequest,
    db: Session = Depends(get_db)
):
    """
    Cambia estado de mantenimiento con trazabilidad.
    """

    mantenimiento = buscar_por_id_string(
        db,
        Mantenimiento,
        mantenimiento_id
    )

    if not mantenimiento:
        raise HTTPException(
            status_code=404,
            detail="Mantenimiento no encontrado."
        )

    estado_actual = mantenimiento.estado
    estado_nuevo = payload.estado_nuevo.upper()

    if estado_nuevo not in ESTADOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="Estado no permitido."
        )

    if estado_nuevo == estado_actual:
        raise HTTPException(
            status_code=400,
            detail="El mantenimiento ya tiene ese estado."
        )

    if estado_nuevo not in TRANSICIONES_VALIDAS.get(estado_actual, []):
        raise HTTPException(
            status_code=400,
            detail=f"No se permite cambiar de {estado_actual} a {estado_nuevo}."
        )

    if estado_nuevo in ["EN_PROCESO", "PAUSADO", "FINALIZADO"] and not mantenimiento.tecnico_id:
        raise HTTPException(
            status_code=400,
            detail="Debe asignar un técnico antes de cambiar a este estado."
        )

    if estado_nuevo == "FINALIZADO" and not payload.observacion:
        raise HTTPException(
            status_code=400,
            detail="Para finalizar debe registrar una observación técnica."
        )

    if estado_nuevo == "ANULADO" and not payload.observacion:
        raise HTTPException(
            status_code=400,
            detail="Para anular debe registrar el motivo de anulación."
        )

    if estado_actual == "FINALIZADO" and estado_nuevo == "EN_PROCESO":
        if not payload.observacion or len(payload.observacion.strip()) < 10:
            raise HTTPException(
                status_code=422,
                detail="Indica el motivo de la reapertura con al menos 10 caracteres.",
            )
        aplicar_reapertura(mantenimiento)

    ahora = datetime.now()

    if estado_actual == "FINALIZADO" and estado_nuevo == "EN_PROCESO":
        pass
    elif estado_nuevo == "EN_PROCESO" and not mantenimiento.fecha_inicio:
        mantenimiento.fecha_inicio = ahora

    elif estado_nuevo == "PAUSADO":
        mantenimiento.fecha_pausa = ahora

    elif estado_nuevo == "FINALIZADO":
        mantenimiento.fecha_finalizacion = ahora
        mantenimiento.cerrado = True
        mantenimiento.fecha_cierre = ahora

    elif estado_nuevo == "ANULADO":
        mantenimiento.motivo_anulacion = payload.observacion

    mantenimiento.estado = estado_nuevo
    mantenimiento.observacion_estado = payload.observacion
    mantenimiento.actualizado_en = ahora

    registrar_historial(
        db=db,
        mantenimiento_id=mantenimiento.id,
        estado_anterior=estado_actual,
        estado_nuevo=estado_nuevo,
        tecnico_id=mantenimiento.tecnico_id,
        observacion=payload.observacion,
        creado_por=payload.creado_por,
    )

    db.commit()
    db.refresh(mantenimiento)

    return mantenimiento_dict(mantenimiento, db)


# ============================================================
# HISTORIAL
# ============================================================

@router.get("/{mantenimiento_id}/historial", response_model=list[HistMantenimientoOut])
def obtener_historial(
    mantenimiento_id: str,
    db: Session = Depends(get_db)
):
    """
    Lista historial de mantenimiento.
    """

    mantenimiento = buscar_por_id_string(
        db,
        Mantenimiento,
        mantenimiento_id
    )

    if not mantenimiento:
        raise HTTPException(
            status_code=404,
            detail="Mantenimiento no encontrado."
        )

    historial = (
        db.query(HistMantenimiento)
        .filter(cast(HistMantenimiento.mantenimiento_id, String) == str(mantenimiento_id))
        .order_by(HistMantenimiento.fecha_evento.desc())
        .all()
    )

    return historial


# ============================================================
# MANTENIMIENTOS POR TÉCNICO
# ============================================================

@router.get("/tecnico/{tecnico_id}/asignados")
def mantenimientos_por_tecnico(
    tecnico_id: str,
    db: Session = Depends(get_db)
):
    """
    Lista mantenimientos asignados a un técnico.
    """

    tecnico = (
        db.query(Tecnico)
        .filter(cast(Tecnico.id, String) == str(tecnico_id))
        .first()
    )

    if not tecnico:
        raise HTTPException(
            status_code=404,
            detail="Técnico no encontrado."
        )

    mantenimientos = (
        db.query(Mantenimiento)
        .filter(cast(Mantenimiento.tecnico_id, String) == str(tecnico_id))
        .order_by(Mantenimiento.id.desc())
        .all()
    )

    return [mantenimiento_dict(m, db) for m in mantenimientos]


# ============================================================
# DASHBOARD TÉCNICO
# ============================================================

@router.get("/dashboard/tecnico/{tecnico_id}")
def dashboard_tecnico(
    tecnico_id: str,
    db: Session = Depends(get_db)
):
    """
    Métricas por técnico.
    """

    tecnico = (
        db.query(Tecnico)
        .filter(cast(Tecnico.id, String) == str(tecnico_id))
        .first()
    )

    if not tecnico:
        raise HTTPException(
            status_code=404,
            detail="Técnico no encontrado."
        )

    base = db.query(Mantenimiento).filter(
        cast(Mantenimiento.tecnico_id, String) == str(tecnico_id)
    )

    return {
        "tecnico_id": tecnico_id,
        "total": base.count(),
        "asignados": base.filter(Mantenimiento.estado == "ASIGNADO").count(),
        "en_proceso": base.filter(Mantenimiento.estado == "EN_PROCESO").count(),
        "pausados": base.filter(Mantenimiento.estado == "PAUSADO").count(),
        "finalizados": base.filter(Mantenimiento.estado == "FINALIZADO").count(),
        "anulados": base.filter(Mantenimiento.estado == "ANULADO").count(),
    }
