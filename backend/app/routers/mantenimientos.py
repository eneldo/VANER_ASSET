# ============================================================
# ROUTER: Mantenimientos PRO
# Archivo: backend/app/routers/mantenimientos.py
# CRUD + asignación técnico + estados + soft-delete
# Creación transaccional con técnico opcional
# ============================================================

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import cast, String, func
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
from app.routers.auth import obtener_usuario_actual
from app.core.auth_dependencies import require_roles

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


router = APIRouter(
    prefix="/mantenimientos",
    tags=["Mantenimientos PRO"],
    dependencies=[Depends(require_roles("ADMIN", "COORDINADOR", "TECNICO"))],
)


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

def _now():
    return datetime.now(timezone.utc)


def str_id(value):
    return str(value) if value is not None else None


def _parse_uuid(valor) -> UUID:
    try:
        return UUID(str(valor))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Identificador inválido.")


def buscar_por_id(db: Session, modelo, valor_id):
    uid = _parse_uuid(valor_id)
    return db.query(modelo).filter(modelo.id == uid).first()


def _obtener_usuario_empresa_ids(usuario: Usuario) -> list[UUID]:
    ids = list(getattr(usuario, "empresa_ids", None) or [])
    if not ids and usuario.empresa_id:
        ids = [usuario.empresa_id]
    return ids


def _filtrar_por_empresa(query, usuario: Usuario):
    empresa_ids = _obtener_usuario_empresa_ids(usuario)
    if not empresa_ids:
        raise HTTPException(status_code=403, detail="Sin acceso a empresas.")
    if usuario.rol in ("ADMIN", "COORDINADOR"):
        query = query.filter(Mantenimiento.empresa_id.in_(empresa_ids))
    elif usuario.rol == "TECNICO":
        query = query.filter(Mantenimiento.tecnico_id.isnot(None))
    return query


def normalizar_fecha_programada(fecha):
    if not fecha:
        return None
    try:
        if isinstance(fecha, datetime):
            return fecha
        if isinstance(fecha, str):
            return datetime.fromisoformat(fecha.replace("Z", "+00:00"))
        return fecha
    except Exception:
        return None


def _validar_fechas(payload):
    inicio = getattr(payload, "fecha_inicio_programada", None)
    fin = getattr(payload, "fecha_fin_programada", None)
    if inicio and fin:
        fi = normalizar_fecha_programada(inicio)
        ff = normalizar_fecha_programada(fin)
        if fi and ff and ff <= fi:
            raise HTTPException(
                status_code=400,
                detail="La fecha de finalización debe ser posterior a la fecha de inicio.",
            )


def sincronizar_tenant_desde_equipo(mantenimiento: Mantenimiento, equipo: Equipo):
    empresa_id = getattr(equipo, "empresa_id", None)
    sede_id = getattr(equipo, "sede_id", None)
    if not empresa_id or not sede_id:
        raise HTTPException(
            status_code=409,
            detail="El equipo debe tener empresa y sede.",
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


def _cargar_relaciones(db: Session, mantenimiento: Mantenimiento):
    if not mantenimiento.equipo:
        db.refresh(mantenimiento, ["equipo", "tecnico", "empresa", "sede"])
    equipo = mantenimiento.equipo
    empresa = None
    sede = None
    if equipo:
        if equipo.empresa_id and not mantenimiento.empresa:
            mantenimiento.empresa = db.query(Empresa).get(equipo.empresa_id)
        if equipo.sede_id and not mantenimiento.sede:
            mantenimiento.sede = db.query(Sede).get(equipo.sede_id)
        empresa = mantenimiento.empresa
        sede = mantenimiento.sede
    tecnico = mantenimiento.tecnico
    tecnico_nombre = None
    if tecnico:
        usuario_tecnico = db.query(Usuario).get(tecnico.usuario_id)
        tecnico_nombre = (
            getattr(usuario_tecnico, "nombre_completo", None)
            if usuario_tecnico else None
        ) or getattr(tecnico, "especialidad", None) or f"Técnico {str_id(tecnico.id)}"
    return equipo, empresa, sede, tecnico, tecnico_nombre


def mantenimiento_dict(m: Mantenimiento, db: Session):
    equipo, empresa, sede, _, tecnico_nombre = _cargar_relaciones(db, m)
    return {
        "id": str_id(m.id),
        "equipo_id": str_id(m.equipo_id),
        "empresa_id": str_id(m.empresa_id),
        "sede_id": str_id(m.sede_id),
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
        "activo": m.activo,
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
# LISTAR MANTENIMIENTOS (con paginación y filtros)
# ============================================================

@router.get("/")
def listar_mantenimientos(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    estado: str | None = None,
    tipo: str | None = None,
    prioridad: str | None = None,
    equipo_id: str | None = None,
    tecnico_id: str | None = None,
    buscar: str | None = None,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Mantenimiento)
        .filter(Mantenimiento.activo == True)
    )
    query = _filtrar_por_empresa(query, usuario)

    if estado:
        query = query.filter(Mantenimiento.estado == estado.upper())
    if tipo:
        query = query.filter(Mantenimiento.tipo == tipo.upper())
    if prioridad:
        query = query.filter(Mantenimiento.prioridad == prioridad.upper())
    if equipo_id:
        uid = _parse_uuid(equipo_id)
        query = query.filter(Mantenimiento.equipo_id == uid)
    if tecnico_id:
        uid = _parse_uuid(tecnico_id)
        query = query.filter(Mantenimiento.tecnico_id == uid)
    if buscar:
        _like = f"%{buscar}%"
        query = query.join(Equipo, Mantenimiento.equipo_id == Equipo.id, isouter=True).filter(
            (Equipo.nombre.ilike(_like))
            | (Equipo.codigo_id.ilike(_like))
            | (Equipo.serie.ilike(_like))
            | (Mantenimiento.descripcion.ilike(_like))
        )

    total = query.count()
    items = (
        query.order_by(Mantenimiento.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "items": [mantenimiento_dict(m, db) for m in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


# ============================================================
# OBTENER MANTENIMIENTO
# ============================================================

@router.get("/{mantenimiento_id}")
def obtener_mantenimiento(
    mantenimiento_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    mantenimiento = (
        db.query(Mantenimiento)
        .options(joinedload(Mantenimiento.historial))
        .filter(Mantenimiento.id == _parse_uuid(mantenimiento_id))
        .first()
    )

    if not mantenimiento or not mantenimiento.activo:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

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
# CREAR MANTENIMIENTO (transaccional, técnico opcional)
# ============================================================

@router.post("/")
def crear_mantenimiento(
    payload: MantenimientoCreate,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    _validar_fechas(payload)

    equipo = buscar_por_id(db, Equipo, payload.equipo_id)
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")

    tecnico = None
    if payload.tecnico_id:
        tecnico = buscar_por_id(db, Tecnico, payload.tecnico_id)
        if not tecnico:
            raise HTTPException(status_code=404, detail="Técnico no encontrado.")
        usuario_tecnico = db.query(Usuario).get(tecnico.usuario_id)
        if not usuario_tecnico or not usuario_tecnico.activo:
            raise HTTPException(status_code=400, detail="El técnico no está activo.")

    estado_inicial = "ASIGNADO" if tecnico else "PROGRAMADO"

    nuevo = Mantenimiento(
        equipo_id=equipo.id,
        tipo=payload.tipo,
        descripcion=payload.descripcion,
        prioridad=payload.prioridad or "MEDIA",
        fecha_programada=normalizar_fecha_programada(payload.fecha_programada),
        fecha_inicio_programada=normalizar_fecha_programada(payload.fecha_inicio_programada),
        fecha_fin_programada=normalizar_fecha_programada(payload.fecha_fin_programada),
        observaciones=payload.observaciones,
        estado_inicial_equipo=getattr(equipo, "estado", None),
        repuestos=payload.repuestos,
        latitud=payload.latitud,
        longitud=payload.longitud,
        costo=payload.costo,
        costo_mano_obra=payload.costo_mano_obra,
        costo_repuestos=payload.costo_repuestos,
        costo_total=payload.costo_total,
        solucion=payload.solucion,
        responsable_id=usuario.id,
        tipo_movimiento=payload.tipo_movimiento,
        activo_afectado_id=payload.activo_afectado_id,
        activo_afectado_tipo=payload.activo_afectado_tipo,
        estado=estado_inicial,
        tecnico_id=tecnico.id if tecnico else None,
        fecha_asignacion=_now() if tecnico else None,
    )
    sincronizar_tenant_desde_equipo(nuevo, equipo)

    try:
        db.add(nuevo)
        db.flush()

        registrar_historial(
            db=db,
            mantenimiento_id=nuevo.id,
            estado_anterior=None,
            estado_nuevo=estado_inicial,
            tecnico_id=tecnico.id if tecnico else None,
            observacion=f"Mantenimiento creado en estado {estado_inicial}.",
            creado_por=usuario.nombre_completo or usuario.username,
        )

        db.commit()
        db.refresh(nuevo)
        return mantenimiento_dict(nuevo, db)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se pudo crear el mantenimiento.",
        )


# ============================================================
# ACTUALIZAR MANTENIMIENTO
# ============================================================

@router.put("/{mantenimiento_id}")
def actualizar_mantenimiento(
    mantenimiento_id: str,
    payload: MantenimientoUpdate,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    mantenimiento = buscar_por_id(db, Mantenimiento, mantenimiento_id)
    if not mantenimiento or not mantenimiento.activo:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    if mantenimiento.estado in ("FINALIZADO", "ANULADO"):
        raise HTTPException(
            status_code=400,
            detail="No se puede editar un mantenimiento finalizado o anulado.",
        )

    datos = payload.model_dump(exclude_unset=True)

    if "fecha_programada" in datos:
        datos["fecha_programada"] = normalizar_fecha_programada(datos["fecha_programada"])

    for campo, valor in datos.items():
        setattr(mantenimiento, campo, valor)

    if mantenimiento.equipo_id:
        equipo = db.query(Equipo).get(mantenimiento.equipo_id)
        if equipo:
            sincronizar_tenant_desde_equipo(mantenimiento, equipo)

    mantenimiento.actualizado_en = _now()

    try:
        db.commit()
        db.refresh(mantenimiento)
        return mantenimiento_dict(mantenimiento, db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se pudo actualizar.")


# ============================================================
# ELIMINAR MANTENIMIENTO (soft-delete)
# ============================================================

@router.delete("/{mantenimiento_id}")
def eliminar_mantenimiento(
    mantenimiento_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    mantenimiento = buscar_por_id(db, Mantenimiento, mantenimiento_id)
    if not mantenimiento or not mantenimiento.activo:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    if mantenimiento.estado not in ("PROGRAMADO", "ANULADO"):
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden eliminar mantenimientos programados o anulados.",
        )

    mantenimiento.activo = False
    mantenimiento.actualizado_en = _now()

    registrar_historial(
        db=db,
        mantenimiento_id=mantenimiento.id,
        estado_anterior=mantenimiento.estado,
        estado_nuevo="ELIMINADO",
        observacion="Mantenimiento eliminado (soft-delete).",
        creado_por=usuario.nombre_completo or usuario.username,
    )

    db.commit()
    return {"ok": True, "mensaje": "Mantenimiento eliminado correctamente."}


# ============================================================
# ASIGNAR TÉCNICO
# ============================================================

@router.patch("/{mantenimiento_id}/asignar-tecnico")
def asignar_tecnico(
    mantenimiento_id: str,
    payload: AsignarTecnicoRequest,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    mantenimiento = buscar_por_id(db, Mantenimiento, mantenimiento_id)
    if not mantenimiento or not mantenimiento.activo:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    tecnico = buscar_por_id(db, Tecnico, payload.tecnico_id)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado.")

    usuario_tecnico = db.query(Usuario).get(tecnico.usuario_id)
    if not usuario_tecnico or not usuario_tecnico.activo:
        raise HTTPException(status_code=400, detail="El técnico no está activo.")

    equipo = db.query(Equipo).get(mantenimiento.equipo_id)
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")

    if str(usuario_tecnico.empresa_id) != str(equipo.empresa_id):
        raise HTTPException(
            status_code=400,
            detail="El técnico y el equipo deben pertenecer a la misma empresa.",
        )

    if mantenimiento.estado in ("FINALIZADO", "ANULADO"):
        raise HTTPException(
            status_code=400,
            detail="No se puede asignar técnico a un mantenimiento finalizado o anulado.",
        )

    estado_anterior = mantenimiento.estado
    mantenimiento.tecnico_id = tecnico.id
    mantenimiento.estado = "ASIGNADO"
    mantenimiento.fecha_asignacion = _now()
    mantenimiento.observacion_estado = payload.observacion
    mantenimiento.actualizado_en = _now()

    registrar_historial(
        db=db,
        mantenimiento_id=mantenimiento.id,
        estado_anterior=estado_anterior,
        estado_nuevo="ASIGNADO",
        tecnico_id=tecnico.id,
        observacion=payload.observacion,
        creado_por=usuario.nombre_completo or usuario.username,
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
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    mantenimiento = buscar_por_id(db, Mantenimiento, mantenimiento_id)
    if not mantenimiento or not mantenimiento.activo:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    estado_actual = mantenimiento.estado
    estado_nuevo = payload.estado_nuevo.upper()

    if estado_nuevo not in ESTADOS_PERMITIDOS:
        raise HTTPException(status_code=400, detail="Estado no permitido.")

    if estado_nuevo == estado_actual:
        raise HTTPException(status_code=400, detail="Ya tiene ese estado.")

    if estado_nuevo not in TRANSICIONES_VALIDAS.get(estado_actual, []):
        raise HTTPException(
            status_code=400,
            detail=f"No se permite cambiar de {estado_actual} a {estado_nuevo}.",
        )

    if estado_nuevo in ("EN_PROCESO", "PAUSADO", "FINALIZADO") and not mantenimiento.tecnico_id:
        raise HTTPException(
            status_code=400,
            detail="Debe asignar un técnico antes de cambiar a este estado.",
        )

    if estado_nuevo == "FINALIZADO" and not payload.observacion:
        raise HTTPException(
            status_code=400,
            detail="Para finalizar debe registrar una observación.",
        )

    if estado_nuevo == "ANULADO" and not payload.observacion:
        raise HTTPException(
            status_code=400,
            detail="Para anular debe registrar el motivo.",
        )

    if estado_actual == "FINALIZADO" and estado_nuevo == "EN_PROCESO":
        if not payload.observacion or len(payload.observacion.strip()) < 10:
            raise HTTPException(
                status_code=422,
                detail="Indica el motivo de reapertura con al menos 10 caracteres.",
            )
        aplicar_reapertura(mantenimiento)

    ahora = _now()

    if estado_nuevo == "EN_PROCESO" and not mantenimiento.fecha_inicio:
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
        creado_por=usuario.nombre_completo or usuario.username,
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
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    uid = _parse_uuid(mantenimiento_id)
    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == uid).first()
    if not mantenimiento or not mantenimiento.activo:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    return (
        db.query(HistMantenimiento)
        .filter(HistMantenimiento.mantenimiento_id == uid)
        .order_by(HistMantenimiento.fecha_evento.desc())
        .all()
    )


# ============================================================
# MANTENIMIENTOS POR TÉCNICO
# ============================================================

@router.get("/tecnico/{tecnico_id}/asignados")
def mantenimientos_por_tecnico(
    tecnico_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    uid = _parse_uuid(tecnico_id)
    tecnico = db.query(Tecnico).filter(Tecnico.id == uid).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado.")

    items = (
        db.query(Mantenimiento)
        .filter(Mantenimiento.tecnico_id == uid, Mantenimiento.activo == True)
        .order_by(Mantenimiento.created_at.desc())
        .all()
    )
    return [mantenimiento_dict(m, db) for m in items]


# ============================================================
# DASHBOARD TÉCNICO
# ============================================================

@router.get("/dashboard/tecnico/{tecnico_id}")
def dashboard_tecnico(
    tecnico_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    uid = _parse_uuid(tecnico_id)
    tecnico = db.query(Tecnico).filter(Tecnico.id == uid).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado.")

    base = db.query(Mantenimiento).filter(
        Mantenimiento.tecnico_id == uid,
        Mantenimiento.activo == True,
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


# ============================================================
# DETECCIÓN DE CONFLICTOS
# ============================================================

@router.get("/conflictos/{equipo_id}")
def detectar_conflictos(
    equipo_id: str,
    tecnico_id: str | None = None,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    excluir_id: str | None = None,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    uid_eq = _parse_uuid(equipo_id)
    equipo = db.query(Equipo).filter(Equipo.id == uid_eq).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")

    advertencias = []
    bloqueantes = []

    ordenes_abiertas = (
        db.query(Mantenimiento)
        .filter(
            Mantenimiento.equipo_id == uid_eq,
            Mantenimiento.activo == True,
            Mantenimiento.estado.in_(["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO"]),
        )
    )
    if excluir_id:
        ordenes_abiertas = ordenes_abiertas.filter(
            Mantenimiento.id != _parse_uuid(excluir_id)
        )
    duplicadas = ordenes_abiertas.all()
    if duplicadas:
        bloqueantes.append({
            "tipo": "orden_duplicada",
            "mensaje": f"Este equipo ya tiene {len(duplicadas)} orden(es) abierta(s).",
            "severidad": "bloqueante",
        })

    if equipo.estado in ("BAJA", "FUERA_DE_SERVICIO"):
        bloqueantes.append({
            "tipo": "equipo_no_disponible",
            "mensaje": f"El equipo está en estado {equipo.estado}.",
            "severidad": "bloqueante",
        })

    if equipo.estado == "EN_MANTENIMIENTO":
        advertencias.append({
            "tipo": "equipo_en_mantenimiento",
            "mensaje": "El equipo ya se encuentra en mantenimiento.",
            "severidad": "advertencia",
        })

    if tecnico_id:
        uid_tec = _parse_uuid(tecnico_id)
        ord_tec = (
            db.query(Mantenimiento)
            .filter(
                Mantenimiento.tecnico_id == uid_tec,
                Mantenimiento.activo == True,
                Mantenimiento.estado.in_(["ASIGNADO", "EN_PROCESO"]),
            )
        )
        if excluir_id:
            ord_tec = ord_tec.filter(Mantenimiento.id != _parse_uuid(excluir_id))
        ocupadas = ord_tec.all()
        if ocupadas:
            advertencias.append({
                "tipo": "tecnico_ocupado",
                "mensaje": f"El técnico tiene {len(ocupadas)} orden(es) activa(s).",
                "severidad": "advertencia",
            })

    if fecha_inicio and fecha_fin:
        try:
            fi = datetime.fromisoformat(fecha_inicio.replace("Z", "+00:00"))
            ff = datetime.fromisoformat(fecha_fin.replace("Z", "+00:00"))
            if ff <= fi:
                bloqueantes.append({
                    "tipo": "fechas_invalidas",
                    "mensaje": "La fecha fin debe ser posterior a la fecha inicio.",
                    "severidad": "bloqueante",
                })
        except ValueError:
            pass

    preventivos = (
        db.query(Mantenimiento)
        .filter(
            Mantenimiento.equipo_id == uid_eq,
            Mantenimiento.activo == True,
            Mantenimiento.tipo == "PREVENTIVO",
            Mantenimiento.estado.in_(["PROGRAMADO", "ASIGNADO"]),
        )
        .order_by(Mantenimiento.fecha_inicio_programada.desc())
        .first()
    )
    if preventivos and preventivos.fecha_fin_programada:
        from datetime import timedelta
        vencido = preventivos.fecha_fin_programada + timedelta(days=30)
        if datetime.now(timezone.utc) > vencido.replace(tzinfo=timezone.utc):
            advertencias.append({
                "tipo": "preventivo_vencido",
                "mensaje": "Hay un mantenimiento preventivo vencido para este equipo.",
                "severidad": "advertencia",
            })

    return {
        "equipo_id": equipo_id,
        "advertencias": advertencias,
        "bloqueantes": bloqueantes,
        "puede_crear": len(bloqueantes) == 0,
    }


# ============================================================
# SUGERENCIA DE TÉCNICO
# ============================================================

@router.get("/sugerir-tecnico/{equipo_id}")
def sugerir_tecnico(
    equipo_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    uid_eq = _parse_uuid(equipo_id)
    equipo = db.query(Equipo).filter(Equipo.id == uid_eq).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")

    tecnicos = (
        db.query(Tecnico)
        .filter(Tecnico.activo == True)
        .all()
    )

    candidatos = []
    for tec in tecnicos:
        usuario_tec = db.query(Usuario).get(tec.usuario_id)
        if not usuario_tec or not usuario_tec.activo:
            continue
        if usuario_tec.empresa_id and str(usuario_tec.empresa_id) != str(equipo.empresa_id):
            continue

        ordenes_activas = (
            db.query(Mantenimiento)
            .filter(
                Mantenimiento.tecnico_id == tec.id,
                Mantenimiento.activo == True,
                Mantenimiento.estado.in_(["ASIGNADO", "EN_PROCESO"]),
            )
            .count()
        )

        score = 100 - (ordenes_activas * 10)

        if tec.especialidad and equipo.categoria_id:
            score += 15

        candidatos.append({
            "tecnico_id": str(tec.id),
            "nombre": usuario_tec.nombre_completo or tec.especialidad or f"Técnico {tec.id}",
            "especialidad": tec.especialidad,
            "ordenes_activas": ordenes_activas,
            "score": max(0, score),
        })

    candidatos.sort(key=lambda c: c["score"], reverse=True)

    return {
        "equipo_id": equipo_id,
        "sugerencias": candidatos[:5],
    }


# ============================================================
# SUGERENCIA DE PRIORIDAD
# ============================================================

@router.get("/sugerir-prioridad")
def sugerir_prioridad(
    equipo_id: str,
    tipo: str = "PREVENTIVO",
    equipo_detenido: bool = False,
    afectacion_operativa: str | None = None,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    uid_eq = _parse_uuid(equipo_id)
    equipo = db.query(Equipo).filter(Equipo.id == uid_eq).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")

    score = 50
    motivos = []

    criticidad = getattr(equipo, "criticidad", None)
    if criticidad == "CRITICA":
        score += 30
        motivos.append("Equipo de criticidad crítica")
    elif criticidad == "ALTA":
        score += 15
        motivos.append("Equipo de criticidad alta")

    if equipo_detenido:
        score += 25
        motivos.append("Equipo detenido")

    if tipo == "CORRECTIVO":
        score += 10
        motivos.append("Mantenimiento correctivo")
    elif tipo == "CALIBRACION":
        score += 5
        motivos.append("Calibración programada")

    if afectacion_operativa == "ALTA":
        score += 20
        motivos.append("Alta afectación operativa")
    elif afectacion_operativa == "MEDIA":
        score += 10
        motivos.append("Afectación operativa media")

    if score >= 80:
        prioridad = "CRITICA"
    elif score >= 60:
        prioridad = "ALTA"
    elif score >= 40:
        prioridad = "MEDIA"
    else:
        prioridad = "BAJA"

    return {
        "prioridad_sugerida": prioridad,
        "score": score,
        "motivos": motivos,
    }


# ============================================================
# CREAR RECURRENCIA
# ============================================================

@router.post("/{mantenimiento_id}/recurrencia")
def crear_recurrencia(
    mantenimiento_id: str,
    frecuencia: str,
    cantidad: int = 5,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    from datetime import timedelta
    from dateutil.relativedelta import relativedelta

    uid = _parse_uuid(mantenimiento_id)
    original = db.query(Mantenimiento).filter(Mantenimiento.id == uid).first()
    if not original or not original.activo:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado.")

    if not original.fecha_inicio_programada:
        raise HTTPException(
            status_code=400,
            detail="El mantenimiento original debe tener fecha de inicio programada.",
        )

    frecuencias_validas = {
        "SEMANAL": timedelta(weeks=1),
        "MENSUAL": relativedelta(months=1),
        "BIMESTRAL": relativedelta(months=2),
        "TRIMESTRAL": relativedelta(months=3),
        "SEMESTRAL": relativedelta(months=6),
        "ANUAL": relativedelta(years=1),
    }

    freq_upper = frecuencia.upper()
    if freq_upper not in frecuencias_validas:
        raise HTTPException(
            status_code=400,
            detail=f"Frecuencia no válida. Use: {', '.join(frecuencias_validas.keys())}",
        )

    cantidad = min(max(cantidad, 1), 24)
    delta = frecuencias_validas[freq_upper]
    creados = []
    fecha_base = original.fecha_inicio_programada

    for i in range(cantidad):
        if isinstance(delta, timedelta):
            nueva_fecha = fecha_base + delta * (i + 1)
        else:
            nueva_fecha = fecha_base + delta * (i + 1)

        nuevo = Mantenimiento(
            equipo_id=original.equipo_id,
            tipo=original.tipo,
            descripcion=f"{original.descripcion or ''} (Recurrencia {i + 1}/{cantidad})".strip(),
            prioridad=original.prioridad,
            fecha_inicio_programada=nueva_fecha,
            fecha_fin_programada=original.fecha_fin_programada + (nueva_fecha - original.fecha_inicio_programada) if original.fecha_fin_programada else None,
            observaciones=original.observaciones,
            empresa_id=original.empresa_id,
            sede_id=original.sede_id,
            estado="PROGRAMADO",
            responsable_id=usuario.id,
        )

        db.add(nuevo)
        db.flush()

        registrar_historial(
            db=db,
            mantenimiento_id=nuevo.id,
            estado_anterior=None,
            estado_nuevo="PROGRAMADO",
            observacion=f"Generado por recurrencia {freq_upper} desde #{original.id}",
            creado_por=usuario.nombre_completo or usuario.username,
        )

        creados.append({
            "id": str_id(nuevo.id),
            "fecha_inicio_programada": nueva_fecha.isoformat() if nueva_fecha else None,
        })

    db.commit()

    return {
        "ok": True,
        "frecuencia": freq_upper,
        "cantidad": len(creados),
        "mantenimientos_creados": creados,
    }


# ============================================================
# ACCESOS RÁPIDOS — crear desde contexto
# ============================================================

@router.get("/acceso-rapido/{equipo_id}")
def acceso_rapido(
    equipo_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    uid = _parse_uuid(equipo_id)
    equipo = db.query(Equipo).filter(Equipo.id == uid).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.")

    ultimo_mantenimiento = (
        db.query(Mantenimiento)
        .filter(
            Mantenimiento.equipo_id == uid,
            Mantenimiento.activo == True,
        )
        .order_by(Mantenimiento.created_at.desc())
        .first()
    )

    ordenes_abiertas = (
        db.query(Mantenimiento)
        .filter(
            Mantenimiento.equipo_id == uid,
            Mantenimiento.activo == True,
            Mantenimiento.estado.in_(["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO"]),
        )
        .count()
    )

    return {
        "equipo_id": str_id(equipo.id),
        "equipo_nombre": equipo.nombre,
        "empresa_id": str_id(equipo.empresa_id),
        "sede_id": str_id(equipo.sede_id),
        "ubicacion": getattr(equipo, "ubicacion", None),
        "ultimo_mantenimiento": {
            "id": str_id(ultimo_mantenimiento.id) if ultimo_mantenimiento else None,
            "tipo": ultimo_mantenimiento.tipo if ultimo_mantenimiento else None,
            "fecha": ultimo_mantenimiento.fecha_finalizacion.isoformat() if ultimo_mantenimiento and ultimo_mantenimiento.fecha_finalizacion else None,
            "estado": ultimo_mantenimiento.estado if ultimo_mantenimiento else None,
        } if ultimo_mantenimiento else None,
        "ordenes_abiertas": ordenes_abiertas,
        "sugerencia_tipo": "CORRECTIVO" if ordenes_abiertas > 0 else "PREVENTIVO",
    }
