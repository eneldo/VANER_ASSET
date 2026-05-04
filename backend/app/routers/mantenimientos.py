# ============================================================
# ROUTER: Mantenimientos PRO
# Archivo: app/routers/mantenimientos.py
# Objetivo:
#   CRUD de mantenimientos.
#   Asignación de técnico.
#   Cambio de estados PRO.
#   Historial automático de trazabilidad.
# ============================================================

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.mantenimiento import Mantenimiento
from app.models.hist_mantenimiento import HistMantenimiento
from app.models.tecnico import Tecnico
from app.models.equipo import Equipo

from app.schemas.mantenimiento import (
    MantenimientoCreate,
    MantenimientoUpdate,
    MantenimientoOut,
    MantenimientoDetalleOut,
    AsignarTecnicoRequest,
    CambiarEstadoRequest,
    HistMantenimientoOut,
)

router = APIRouter(
    prefix="/mantenimientos",
    tags=["Mantenimientos PRO"]
)

# ============================================================
# Estados permitidos del flujo PRO
# ============================================================

ESTADOS_PERMITIDOS = [
    "PROGRAMADO",
    "ASIGNADO",
    "EN_PROCESO",
    "PAUSADO",
    "FINALIZADO",
    "ANULADO",
]

# Transiciones válidas para evitar saltos incorrectos
TRANSICIONES_VALIDAS = {
    "PROGRAMADO": ["ASIGNADO", "ANULADO"],
    "ASIGNADO": ["EN_PROCESO", "ANULADO"],
    "EN_PROCESO": ["PAUSADO", "FINALIZADO", "ANULADO"],
    "PAUSADO": ["EN_PROCESO", "ANULADO"],
    "FINALIZADO": [],
    "ANULADO": [],
}


# ============================================================
# Helper: registrar historial de mantenimiento
# ============================================================

def registrar_historial(
    db: Session,
    mantenimiento_id: int,
    estado_anterior: str | None,
    estado_nuevo: str,
    tecnico_id: int | None = None,
    observacion: str | None = None,
    creado_por: str | None = "Sistema",
):
    """
    Guarda una línea en hist_mantenimiento cada vez que ocurre
    una asignación o cambio de estado.
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


# ============================================================
# GET /mantenimientos
# Lista mantenimientos con filtros opcionales
# ============================================================

# ============================================================
# LISTAR MANTENIMIENTOS (SOLUCIÓN DEFINITIVA UUID)
# ============================================================

@router.get("/", response_model=list[MantenimientoOut])
def listar_mantenimientos(db: Session = Depends(get_db)):
    mantenimientos = (
        db.query(Mantenimiento)
        .order_by(Mantenimiento.id.desc())
        .all()
    )

    resultado = []

    for m in mantenimientos:
        resultado.append({
            "id": str(m.id),
            "equipo_id": str(m.equipo_id),
            "tipo": m.tipo,
            "descripcion": m.descripcion,
            "fecha_programada": m.fecha_programada,
            "estado": m.estado,
            "tecnico_id": str(m.tecnico_id) if m.tecnico_id else None,
            "fecha_asignacion": m.fecha_asignacion,
            "fecha_inicio": m.fecha_inicio,
            "fecha_pausa": m.fecha_pausa,
            "fecha_finalizacion": m.fecha_finalizacion,
            "observaciones": m.observaciones,
            "observacion_estado": m.observacion_estado,
            "motivo_anulacion": m.motivo_anulacion,
            "costo": m.costo,
            "creado_en": m.creado_en,
            "actualizado_en": m.actualizado_en,
        })

    return resultado


# ============================================================
# GET /mantenimientos/{mantenimiento_id}
# Detalle de mantenimiento con historial
# ============================================================

@router.get("/{mantenimiento_id}", response_model=MantenimientoDetalleOut)
def obtener_mantenimiento(
    mantenimiento_id: int,
    db: Session = Depends(get_db),
):
    mantenimiento = (
        db.query(Mantenimiento)
        .options(joinedload(Mantenimiento.historial))
        .filter(Mantenimiento.id == mantenimiento_id)
        .first()
    )

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    return mantenimiento


# ============================================================
# POST /mantenimientos
# Crear mantenimiento en estado PROGRAMADO
# ============================================================

@router.post("/", response_model=MantenimientoOut)
def crear_mantenimiento(
    payload: MantenimientoCreate,
    db: Session = Depends(get_db),
):
    equipo = db.query(Equipo).filter(Equipo.id == payload.equipo_id).first()

    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")

    nuevo = Mantenimiento(
        equipo_id=payload.equipo_id,
        tipo=payload.tipo,
        descripcion=payload.descripcion,
        fecha_programada=payload.fecha_programada,
        observaciones=payload.observaciones,
        costo=payload.costo,
        estado="PROGRAMADO",
    )

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

    return nuevo


# ============================================================
# PUT /mantenimientos/{mantenimiento_id}
# Actualizar datos generales del mantenimiento
# ============================================================

@router.put("/{mantenimiento_id}", response_model=MantenimientoOut)
def actualizar_mantenimiento(
    mantenimiento_id: int,
    payload: MantenimientoUpdate,
    db: Session = Depends(get_db),
):
    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    datos = payload.model_dump(exclude_unset=True)

    if "equipo_id" in datos:
        equipo = db.query(Equipo).filter(Equipo.id == datos["equipo_id"]).first()
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado.")

    for campo, valor in datos.items():
        setattr(mantenimiento, campo, valor)

    mantenimiento.actualizado_en = datetime.now()

    db.commit()
    db.refresh(mantenimiento)

    return mantenimiento


# ============================================================
# DELETE /mantenimientos/{mantenimiento_id}
# Eliminación lógica recomendada: cambiar estado a ANULADO
# ============================================================

@router.delete("/{mantenimiento_id}")
def eliminar_mantenimiento(
    mantenimiento_id: int,
    db: Session = Depends(get_db),
):
    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    estado_anterior = mantenimiento.estado
    mantenimiento.estado = "ANULADO"
    mantenimiento.motivo_anulacion = "Mantenimiento anulado desde eliminación lógica."
    mantenimiento.actualizado_en = datetime.now()

    registrar_historial(
        db=db,
        mantenimiento_id=mantenimiento.id,
        estado_anterior=estado_anterior,
        estado_nuevo="ANULADO",
        tecnico_id=mantenimiento.tecnico_id,
        observacion="Eliminación lógica: mantenimiento marcado como ANULADO.",
        creado_por="Sistema",
    )

    db.commit()

    return {"ok": True, "mensaje": "Mantenimiento anulado correctamente."}


# ============================================================
# PATCH /mantenimientos/{mantenimiento_id}/asignar-tecnico
# Asignar técnico y pasar a estado ASIGNADO
# ============================================================

@router.patch("/{mantenimiento_id}/asignar-tecnico", response_model=MantenimientoOut)
def asignar_tecnico(
    mantenimiento_id: int,
    payload: AsignarTecnicoRequest,
    db: Session = Depends(get_db),
):
    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    tecnico = db.query(Tecnico).filter(Tecnico.id == payload.tecnico_id).first()

    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado.")

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

    return mantenimiento


# ============================================================
# PATCH /mantenimientos/{mantenimiento_id}/cambiar-estado
# Cambiar estado con validaciones PRO
# ============================================================

@router.patch("/{mantenimiento_id}/cambiar-estado", response_model=MantenimientoOut)
def cambiar_estado(
    mantenimiento_id: int,
    payload: CambiarEstadoRequest,
    db: Session = Depends(get_db),
):
    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    estado_actual = mantenimiento.estado
    estado_nuevo = payload.estado_nuevo.upper()

    if estado_nuevo not in ESTADOS_PERMITIDOS:
        raise HTTPException(status_code=400, detail="Estado no permitido.")

    if estado_nuevo == estado_actual:
        raise HTTPException(status_code=400, detail="El mantenimiento ya tiene ese estado.")

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

    ahora = datetime.now()

    if estado_nuevo == "EN_PROCESO":
        if not mantenimiento.fecha_inicio:
            mantenimiento.fecha_inicio = ahora

    elif estado_nuevo == "PAUSADO":
        mantenimiento.fecha_pausa = ahora

    elif estado_nuevo == "FINALIZADO":
        mantenimiento.fecha_finalizacion = ahora

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

    return mantenimiento


# ============================================================
# GET /mantenimientos/{mantenimiento_id}/historial
# Ver historial de un mantenimiento
# ============================================================

@router.get("/{mantenimiento_id}/historial", response_model=list[HistMantenimientoOut])
def obtener_historial(
    mantenimiento_id: int,
    db: Session = Depends(get_db),
):
    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    historial = (
        db.query(HistMantenimiento)
        .filter(HistMantenimiento.mantenimiento_id == mantenimiento_id)
        .order_by(HistMantenimiento.fecha_evento.desc())
        .all()
    )

    return historial


# ============================================================
# GET /mantenimientos/tecnico/{tecnico_id}/asignados
# Dashboard técnico: mantenimientos asignados al técnico
# ============================================================

@router.get("/tecnico/{tecnico_id}/asignados", response_model=list[MantenimientoOut])
def mantenimientos_por_tecnico(
    tecnico_id: int,
    db: Session = Depends(get_db),
):
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()

    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado.")

    mantenimientos = (
        db.query(Mantenimiento)
        .filter(Mantenimiento.tecnico_id == tecnico_id)
        .order_by(Mantenimiento.id.desc())
        .all()
    )

    return mantenimientos


# ============================================================
# GET /mantenimientos/dashboard/tecnico/{tecnico_id}
# Resumen dinámico para tarjetas del dashboard técnico
# ============================================================

@router.get("/dashboard/tecnico/{tecnico_id}")
def dashboard_tecnico(
    tecnico_id: int,
    db: Session = Depends(get_db),
):
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()

    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado.")

    base = db.query(Mantenimiento).filter(Mantenimiento.tecnico_id == tecnico_id)

    return {
        "tecnico_id": tecnico_id,
        "total": base.count(),
        "asignados": base.filter(Mantenimiento.estado == "ASIGNADO").count(),
        "en_proceso": base.filter(Mantenimiento.estado == "EN_PROCESO").count(),
        "pausados": base.filter(Mantenimiento.estado == "PAUSADO").count(),
        "finalizados": base.filter(Mantenimiento.estado == "FINALIZADO").count(),
        "anulados": base.filter(Mantenimiento.estado == "ANULADO").count(),
    }