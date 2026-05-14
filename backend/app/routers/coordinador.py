"""
===========================================================
FASE 32.3 — MÓDULO COORDINADOR PRO MULTIEMPRESA
Archivo: backend/app/routers/coordinador.py

Reglas:
- ADMIN puede ver todo.
- COORDINADOR solo puede ver la empresa asignada en usuario.empresa_id.
- Los técnicos se filtran por la empresa del usuario técnico.
- Los equipos, sedes, mantenimientos e informes se filtran por empresa.
===========================================================
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.mantenimiento import Mantenimiento
from app.models.equipo import Equipo
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.routers.auth import obtener_usuario_actual


router = APIRouter(
    prefix="/coordinador",
    tags=["Coordinador PRO"],
)


# ===========================================================
# SCHEMAS INTERNOS
# ===========================================================

class MantenimientoCreate(BaseModel):
    equipo_id: UUID
    tipo: str
    estado: Optional[str] = "PROGRAMADO"
    tecnico_id: Optional[UUID] = None
    empresa_id: Optional[UUID] = None
    sede_id: Optional[UUID] = None
    fecha_programada: Optional[datetime] = None
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None
    costo: Optional[float] = None


class MantenimientoUpdate(BaseModel):
    equipo_id: Optional[UUID] = None
    tipo: Optional[str] = None
    estado: Optional[str] = None
    tecnico_id: Optional[UUID] = None
    empresa_id: Optional[UUID] = None
    sede_id: Optional[UUID] = None
    fecha_programada: Optional[datetime] = None
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None
    costo: Optional[float] = None


# ===========================================================
# HELPERS
# ===========================================================

def _rol(usuario: Usuario):
    return str(getattr(usuario, "rol", "") or "").upper()


def _es_admin(usuario: Usuario):
    return _rol(usuario) == "ADMIN"


def _es_coordinador(usuario: Usuario):
    return _rol(usuario) == "COORDINADOR"


def _empresa_usuario(usuario: Usuario):
    return getattr(usuario, "empresa_id", None)


def _validar_coordinador_con_empresa(usuario: Usuario):
    """
    El coordinador debe tener empresa_id.
    """

    if _es_coordinador(usuario) and not _empresa_usuario(usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario COORDINADOR no tiene empresa asignada",
        )


def _fecha_iso(valor):
    if not valor:
        return None

    try:
        return valor.isoformat()
    except Exception:
        return str(valor)


def _set_if_exists(obj, campo, valor):
    if hasattr(obj, campo):
        setattr(obj, campo, valor)


def _nombre_objeto(obj):
    if not obj:
        return None

    usuario = getattr(obj, "usuario", None)

    if usuario:
        for campo in [
            "nombre_completo",
            "nombre",
            "nombres",
            "username",
            "email",
            "correo",
        ]:
            valor = getattr(usuario, campo, None)
            if valor:
                return str(valor)

    for campo in [
        "nombre_completo",
        "nombre",
        "nombres",
        "name",
        "username",
        "email",
        "correo",
        "codigo",
        "codigo_inventario",
        "serie",
        "documento",
        "especialidad",
        "cargo",
    ]:
        valor = getattr(obj, campo, None)
        if valor:
            return str(valor)

    return str(getattr(obj, "id", "Sin nombre"))


def _orden_mantenimiento():
    if hasattr(Mantenimiento, "created_at"):
        return Mantenimiento.created_at.desc()

    if hasattr(Mantenimiento, "creado_en"):
        return Mantenimiento.creado_en.desc()

    if hasattr(Mantenimiento, "fecha_programada"):
        return Mantenimiento.fecha_programada.desc()

    return Mantenimiento.id.desc()


def _serializar_mantenimiento(m):
    tecnico = getattr(m, "tecnico", None)
    equipo = getattr(m, "equipo", None)
    empresa = getattr(m, "empresa", None)
    sede = getattr(m, "sede", None)

    return {
        "id": str(m.id),
        "tipo": getattr(m, "tipo", None),
        "estado": getattr(m, "estado", None),

        "equipo_id": str(m.equipo_id) if getattr(m, "equipo_id", None) else None,
        "equipo_nombre": _nombre_objeto(equipo) or "Sin equipo",

        "tecnico_id": str(m.tecnico_id) if getattr(m, "tecnico_id", None) else None,
        "tecnico_nombre": _nombre_objeto(tecnico) or "Sin técnico",

        "empresa_id": str(m.empresa_id) if getattr(m, "empresa_id", None) else None,
        "empresa_nombre": _nombre_objeto(empresa) or "Sin empresa",

        "sede_id": str(m.sede_id) if getattr(m, "sede_id", None) else None,
        "sede_nombre": _nombre_objeto(sede) or "Sin sede",

        "fecha_programada": _fecha_iso(getattr(m, "fecha_programada", None)),
        "fecha_inicio": _fecha_iso(getattr(m, "fecha_inicio", None)),
        "fecha_fin": _fecha_iso(getattr(m, "fecha_fin", None)),
        "fecha_asignacion": _fecha_iso(getattr(m, "fecha_asignacion", None)),
        "fecha_finalizacion": _fecha_iso(getattr(m, "fecha_finalizacion", None)),

        "descripcion": getattr(m, "descripcion", None),
        "observaciones": getattr(m, "observaciones", None),
        "observacion_estado": getattr(m, "observacion_estado", None),
        "motivo_anulacion": getattr(m, "motivo_anulacion", None),

        "costo": float(m.costo) if getattr(m, "costo", None) else 0,

        "created_at": _fecha_iso(getattr(m, "created_at", None)),
        "updated_at": _fecha_iso(getattr(m, "updated_at", None)),
        "creado_en": _fecha_iso(getattr(m, "creado_en", None)),
        "actualizado_en": _fecha_iso(getattr(m, "actualizado_en", None)),
    }


def _serializar_catalogo(obj):
    nombre = _nombre_objeto(obj)
    usuario = getattr(obj, "usuario", None)

    return {
        "id": str(getattr(obj, "id", "")),
        "nombre": nombre,
        "nombre_completo": nombre,
        "usuario_nombre": nombre,
        "email": getattr(usuario, "email", None) if usuario else getattr(obj, "email", None),
        "username": getattr(usuario, "username", None) if usuario else getattr(obj, "username", None),
        "codigo": getattr(obj, "codigo", None),
        "codigo_inventario": getattr(obj, "codigo_inventario", None),
        "serie": getattr(obj, "serie", None),
        "empresa_id": str(getattr(obj, "empresa_id", "")) if getattr(obj, "empresa_id", None) else None,
    }


def _query_mantenimientos_base(db: Session):
    query = db.query(Mantenimiento)

    relaciones = []

    for rel in ["equipo", "tecnico", "empresa", "sede"]:
        if hasattr(Mantenimiento, rel):
            relaciones.append(joinedload(getattr(Mantenimiento, rel)))

    if relaciones:
        query = query.options(*relaciones)

    return query


def _aplicar_filtro_empresa_mantenimientos(query, usuario: Usuario):
    """
    Filtra mantenimientos por empresa cuando el usuario es COORDINADOR.

    Se usa doble validación:
    - Mantenimiento.empresa_id
    - Equipo.empresa_id

    Así cubrimos mantenimientos antiguos que no tengan empresa_id,
    pero cuyo equipo sí pertenece a una empresa.
    """

    if _es_admin(usuario):
        return query

    _validar_coordinador_con_empresa(usuario)

    empresa_id = _empresa_usuario(usuario)

    if hasattr(Mantenimiento, "equipo_id") and hasattr(Equipo, "empresa_id"):
        query = query.outerjoin(Equipo, Mantenimiento.equipo_id == Equipo.id)

        if hasattr(Mantenimiento, "empresa_id"):
            return query.filter(
                or_(
                    Mantenimiento.empresa_id == empresa_id,
                    Equipo.empresa_id == empresa_id,
                )
            )

        return query.filter(Equipo.empresa_id == empresa_id)

    if hasattr(Mantenimiento, "empresa_id"):
        return query.filter(Mantenimiento.empresa_id == empresa_id)

    return query


def _query_equipos_por_usuario(db: Session, usuario: Usuario):
    query = db.query(Equipo)

    if _es_admin(usuario):
        return query

    _validar_coordinador_con_empresa(usuario)

    if hasattr(Equipo, "empresa_id"):
        query = query.filter(Equipo.empresa_id == _empresa_usuario(usuario))

    return query


def _query_sedes_por_usuario(db: Session, usuario: Usuario):
    query = db.query(Sede)

    if _es_admin(usuario):
        return query

    _validar_coordinador_con_empresa(usuario)

    if hasattr(Sede, "empresa_id"):
        query = query.filter(Sede.empresa_id == _empresa_usuario(usuario))

    return query


def _query_empresas_por_usuario(db: Session, usuario: Usuario):
    query = db.query(Empresa)

    if _es_admin(usuario):
        return query

    _validar_coordinador_con_empresa(usuario)

    return query.filter(Empresa.id == _empresa_usuario(usuario))


def _query_tecnicos_por_usuario(db: Session, usuario: Usuario):
    """
    Técnicos filtrados por la empresa del usuario asociado al técnico.

    Tabla tecnicos:
        tecnico.usuario_id -> usuarios.id

    Tabla usuarios:
        usuarios.empresa_id = empresa del técnico.
    """

    query = db.query(Tecnico).join(Usuario, Tecnico.usuario_id == Usuario.id)

    if hasattr(Tecnico, "usuario"):
        query = query.options(joinedload(Tecnico.usuario))

    if _es_admin(usuario):
        return query

    _validar_coordinador_con_empresa(usuario)

    return query.filter(Usuario.empresa_id == _empresa_usuario(usuario))


def _validar_equipo_pertenece_empresa(db: Session, equipo_id, usuario: Usuario):
    if _es_admin(usuario):
        return

    _validar_coordinador_con_empresa(usuario)

    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()

    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    if getattr(equipo, "empresa_id", None) != _empresa_usuario(usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El equipo no pertenece a la empresa del coordinador",
        )


def _validar_tecnico_pertenece_empresa(db: Session, tecnico_id, usuario: Usuario):
    if not tecnico_id or _es_admin(usuario):
        return

    _validar_coordinador_con_empresa(usuario)

    tecnico = (
        db.query(Tecnico)
        .join(Usuario, Tecnico.usuario_id == Usuario.id)
        .filter(
            Tecnico.id == tecnico_id,
            Usuario.empresa_id == _empresa_usuario(usuario),
        )
        .first()
    )

    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El técnico no pertenece a la empresa del coordinador",
        )


def _resumen_mantenimientos(mantenimientos):
    por_estado = {}
    por_tipo = {}

    for m in mantenimientos:
        estado = getattr(m, "estado", None) or "SIN_ESTADO"
        tipo = getattr(m, "tipo", None) or "SIN_TIPO"

        por_estado[estado] = por_estado.get(estado, 0) + 1
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    return por_estado, por_tipo


# ===========================================================
# DASHBOARD
# ===========================================================

@router.get("/dashboard")
def dashboard_coordinador(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    query = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db),
        usuario_actual,
    )

    mantenimientos = query.all()

    total_mantenimientos = len(mantenimientos)
    programados = len([m for m in mantenimientos if m.estado == "PROGRAMADO"])
    asignados = len([m for m in mantenimientos if m.estado == "ASIGNADO"])
    en_proceso = len([m for m in mantenimientos if m.estado == "EN_PROCESO"])
    finalizados = len([m for m in mantenimientos if m.estado == "FINALIZADO"])
    anulados = len([m for m in mantenimientos if m.estado == "ANULADO"])

    total_equipos = _query_equipos_por_usuario(db, usuario_actual).count()
    total_tecnicos = _query_tecnicos_por_usuario(db, usuario_actual).count()

    recientes = (
        _aplicar_filtro_empresa_mantenimientos(
            _query_mantenimientos_base(db),
            usuario_actual,
        )
        .order_by(_orden_mantenimiento())
        .limit(8)
        .all()
    )

    return {
        "total_mantenimientos": total_mantenimientos,
        "programados": programados,
        "asignados": asignados,
        "en_proceso": en_proceso,
        "finalizados": finalizados,
        "anulados": anulados,
        "total_equipos": total_equipos,
        "total_tecnicos": total_tecnicos,
        "mantenimientos_recientes": [
            _serializar_mantenimiento(m) for m in recientes
        ],
        "metricas": {
            "total_mantenimientos": total_mantenimientos,
            "programados": programados,
            "asignados": asignados,
            "en_proceso": en_proceso,
            "finalizados": finalizados,
            "anulados": anulados,
            "total_equipos": total_equipos,
            "total_tecnicos": total_tecnicos,
        },
        "recientes": [_serializar_mantenimiento(m) for m in recientes],
    }


# ===========================================================
# LISTAR MANTENIMIENTOS
# ===========================================================

@router.get("/mantenimientos")
def listar_mantenimientos_coordinador(
    estado: Optional[str] = Query(None),
    empresa_id: Optional[str] = Query(None),
    sede_id: Optional[str] = Query(None),
    tecnico_id: Optional[str] = Query(None),
    equipo_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    query = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db),
        usuario_actual,
    )

    if estado:
        query = query.filter(Mantenimiento.estado == estado)

    if empresa_id and _es_admin(usuario_actual) and hasattr(Mantenimiento, "empresa_id"):
        query = query.filter(Mantenimiento.empresa_id == empresa_id)

    if sede_id and hasattr(Mantenimiento, "sede_id"):
        query = query.filter(Mantenimiento.sede_id == sede_id)

    if tecnico_id and hasattr(Mantenimiento, "tecnico_id"):
        query = query.filter(Mantenimiento.tecnico_id == tecnico_id)

    if equipo_id and hasattr(Mantenimiento, "equipo_id"):
        query = query.filter(Mantenimiento.equipo_id == equipo_id)

    mantenimientos = query.order_by(_orden_mantenimiento()).all()

    return [_serializar_mantenimiento(m) for m in mantenimientos]


# ===========================================================
# CREAR MANTENIMIENTO
# ===========================================================

@router.post("/mantenimientos")
def crear_mantenimiento_coordinador(
    data: MantenimientoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_equipo_pertenece_empresa(db, data.equipo_id, usuario_actual)
    _validar_tecnico_pertenece_empresa(db, data.tecnico_id, usuario_actual)

    equipo = db.query(Equipo).filter(Equipo.id == data.equipo_id).first()

    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    empresa_final = data.empresa_id

    if not _es_admin(usuario_actual):
        empresa_final = _empresa_usuario(usuario_actual)
    elif not empresa_final:
        empresa_final = getattr(equipo, "empresa_id", None)

    sede_final = data.sede_id or getattr(equipo, "sede_id", None)

    nuevo = Mantenimiento(
        equipo_id=data.equipo_id,
        tipo=data.tipo,
        estado=data.estado or "PROGRAMADO",
        tecnico_id=data.tecnico_id,
        fecha_programada=data.fecha_programada,
        descripcion=data.descripcion,
        observaciones=data.observaciones,
        costo=data.costo,
    )

    _set_if_exists(nuevo, "empresa_id", empresa_final)
    _set_if_exists(nuevo, "sede_id", sede_final)

    if data.tecnico_id:
        _set_if_exists(nuevo, "fecha_asignacion", datetime.utcnow())

        if not data.estado or data.estado == "PROGRAMADO":
            nuevo.estado = "ASIGNADO"

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {
        "message": "Mantenimiento creado correctamente",
        "mantenimiento": _serializar_mantenimiento(nuevo),
    }


# ===========================================================
# EDITAR MANTENIMIENTO
# ===========================================================

@router.put("/mantenimientos/{mantenimiento_id}")
def editar_mantenimiento_coordinador(
    mantenimiento_id: UUID,
    data: MantenimientoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    mantenimiento = (
        _aplicar_filtro_empresa_mantenimientos(
            _query_mantenimientos_base(db),
            usuario_actual,
        )
        .filter(Mantenimiento.id == mantenimiento_id)
        .first()
    )

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    campos = data.model_dump(exclude_unset=True)

    if "equipo_id" in campos and campos["equipo_id"]:
        _validar_equipo_pertenece_empresa(db, campos["equipo_id"], usuario_actual)

    if "tecnico_id" in campos and campos["tecnico_id"]:
        _validar_tecnico_pertenece_empresa(db, campos["tecnico_id"], usuario_actual)

    for campo, valor in campos.items():
        if campo == "empresa_id" and not _es_admin(usuario_actual):
            continue

        if hasattr(mantenimiento, campo):
            setattr(mantenimiento, campo, valor)

    if not _es_admin(usuario_actual):
        _set_if_exists(mantenimiento, "empresa_id", _empresa_usuario(usuario_actual))

    if campos.get("tecnico_id"):
        _set_if_exists(mantenimiento, "fecha_asignacion", datetime.utcnow())

    _set_if_exists(mantenimiento, "actualizado_en", datetime.utcnow())
    _set_if_exists(mantenimiento, "updated_at", datetime.utcnow())

    db.commit()
    db.refresh(mantenimiento)

    return {
        "message": "Mantenimiento actualizado correctamente",
        "mantenimiento": _serializar_mantenimiento(mantenimiento),
    }


# ===========================================================
# ASIGNAR TÉCNICO
# ===========================================================

@router.put("/mantenimientos/{mantenimiento_id}/asignar")
def asignar_tecnico(
    mantenimiento_id: UUID,
    tecnico_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    mantenimiento = (
        _aplicar_filtro_empresa_mantenimientos(
            _query_mantenimientos_base(db),
            usuario_actual,
        )
        .filter(Mantenimiento.id == mantenimiento_id)
        .first()
    )

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    _validar_tecnico_pertenece_empresa(db, tecnico_id, usuario_actual)

    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()

    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")

    mantenimiento.tecnico_id = tecnico_id
    mantenimiento.estado = "ASIGNADO"

    _set_if_exists(mantenimiento, "fecha_asignacion", datetime.utcnow())
    _set_if_exists(mantenimiento, "actualizado_en", datetime.utcnow())
    _set_if_exists(mantenimiento, "updated_at", datetime.utcnow())

    db.commit()
    db.refresh(mantenimiento)

    return {
        "message": "Técnico asignado correctamente",
        "mantenimiento": _serializar_mantenimiento(mantenimiento),
    }


# ===========================================================
# CAMBIAR ESTADO
# ===========================================================

@router.put("/mantenimientos/{mantenimiento_id}/estado")
def cambiar_estado_mantenimiento(
    mantenimiento_id: UUID,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    estados_permitidos = [
        "PROGRAMADO",
        "ASIGNADO",
        "EN_PROCESO",
        "PAUSADO",
        "FINALIZADO",
        "ANULADO",
    ]

    if nuevo_estado not in estados_permitidos:
        raise HTTPException(status_code=400, detail="Estado no permitido")

    mantenimiento = (
        _aplicar_filtro_empresa_mantenimientos(
            _query_mantenimientos_base(db),
            usuario_actual,
        )
        .filter(Mantenimiento.id == mantenimiento_id)
        .first()
    )

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    mantenimiento.estado = nuevo_estado

    if nuevo_estado == "EN_PROCESO":
        _set_if_exists(mantenimiento, "fecha_inicio", datetime.utcnow())

    if nuevo_estado == "FINALIZADO":
        _set_if_exists(mantenimiento, "fecha_finalizacion", datetime.utcnow())
        _set_if_exists(mantenimiento, "fecha_fin", datetime.utcnow())

    if nuevo_estado == "PAUSADO":
        _set_if_exists(mantenimiento, "fecha_pausa", datetime.utcnow())

    _set_if_exists(mantenimiento, "actualizado_en", datetime.utcnow())
    _set_if_exists(mantenimiento, "updated_at", datetime.utcnow())

    db.commit()
    db.refresh(mantenimiento)

    return {
        "message": "Estado actualizado correctamente",
        "mantenimiento": _serializar_mantenimiento(mantenimiento),
    }


# ===========================================================
# REPROGRAMAR
# ===========================================================

@router.put("/mantenimientos/{mantenimiento_id}/reprogramar")
def reprogramar_mantenimiento(
    mantenimiento_id: UUID,
    fecha_programada: datetime,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    mantenimiento = (
        _aplicar_filtro_empresa_mantenimientos(
            _query_mantenimientos_base(db),
            usuario_actual,
        )
        .filter(Mantenimiento.id == mantenimiento_id)
        .first()
    )

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    mantenimiento.fecha_programada = fecha_programada
    mantenimiento.estado = "PROGRAMADO"

    _set_if_exists(mantenimiento, "actualizado_en", datetime.utcnow())
    _set_if_exists(mantenimiento, "updated_at", datetime.utcnow())

    db.commit()
    db.refresh(mantenimiento)

    return {
        "message": "Mantenimiento reprogramado correctamente",
        "mantenimiento": _serializar_mantenimiento(mantenimiento),
    }


# ===========================================================
# ANULAR
# ===========================================================

@router.delete("/mantenimientos/{mantenimiento_id}")
def eliminar_mantenimiento_coordinador(
    mantenimiento_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    mantenimiento = (
        _aplicar_filtro_empresa_mantenimientos(
            _query_mantenimientos_base(db),
            usuario_actual,
        )
        .filter(Mantenimiento.id == mantenimiento_id)
        .first()
    )

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    mantenimiento.estado = "ANULADO"

    _set_if_exists(
        mantenimiento,
        "motivo_anulacion",
        "Anulado desde módulo Coordinador",
    )
    _set_if_exists(mantenimiento, "actualizado_en", datetime.utcnow())
    _set_if_exists(mantenimiento, "updated_at", datetime.utcnow())

    db.commit()
    db.refresh(mantenimiento)

    return {
        "message": "Mantenimiento anulado correctamente",
        "mantenimiento": _serializar_mantenimiento(mantenimiento),
    }


# ===========================================================
# CRONOGRAMA
# ===========================================================

@router.get("/cronograma")
def cronograma_coordinador(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    query = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db),
        usuario_actual,
    )

    if hasattr(Mantenimiento, "fecha_programada"):
        mantenimientos = query.order_by(Mantenimiento.fecha_programada.asc()).all()
    else:
        mantenimientos = query.order_by(_orden_mantenimiento()).all()

    return [_serializar_mantenimiento(m) for m in mantenimientos]


# ===========================================================
# INFORMES
# ===========================================================

@router.get("/informes")
def obtener_informes_coordinador(
    equipo_id: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    query = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db),
        usuario_actual,
    )

    if equipo_id and hasattr(Mantenimiento, "equipo_id"):
        query = query.filter(Mantenimiento.equipo_id == equipo_id)

    if estado:
        query = query.filter(Mantenimiento.estado == estado)

    if tipo:
        query = query.filter(Mantenimiento.tipo == tipo)

    mantenimientos = query.order_by(_orden_mantenimiento()).all()

    por_estado, por_tipo = _resumen_mantenimientos(mantenimientos)
    registros = [_serializar_mantenimiento(m) for m in mantenimientos]

    equipo_nombre = None

    if equipo_id:
        equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
        equipo_nombre = _nombre_objeto(equipo) if equipo else None

    return {
        "total": len(registros),
        "equipo_id": equipo_id,
        "equipo_nombre": equipo_nombre,
        "por_estado": por_estado,
        "por_tipo": por_tipo,
        "mantenimientos": registros,
    }


@router.get("/informes/resumen")
def resumen_informes(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    query = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db),
        usuario_actual,
    )

    mantenimientos = query.all()
    por_estado, por_tipo = _resumen_mantenimientos(mantenimientos)

    return {
        "por_estado": [
            {"estado": estado, "total": total}
            for estado, total in por_estado.items()
        ],
        "por_tipo": [
            {"tipo": tipo, "total": total}
            for tipo, total in por_tipo.items()
        ],
    }


# ===========================================================
# CATÁLOGOS
# ===========================================================

@router.get("/catalogos")
def catalogos_coordinador(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    empresas = _query_empresas_por_usuario(db, usuario_actual).all()
    sedes = _query_sedes_por_usuario(db, usuario_actual).all()
    equipos = _query_equipos_por_usuario(db, usuario_actual).all()
    tecnicos = _query_tecnicos_por_usuario(db, usuario_actual).all()

    return {
        "empresas": [_serializar_catalogo(e) for e in empresas],
        "sedes": [_serializar_catalogo(s) for s in sedes],
        "equipos": [_serializar_catalogo(e) for e in equipos],
        "tecnicos": [_serializar_catalogo(t) for t in tecnicos],
    }