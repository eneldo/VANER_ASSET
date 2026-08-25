# ===========================================================
# ROUTER: COORDINADOR PRO
# Archivo: backend/app/routers/coordinador.py
# Fase: Portal Coordinador PRO
#
# Objetivo:
# - Dar al rol COORDINADOR un portal operativo sin afectar módulos ADMIN.
# - Filtrar siempre por empresa_id del usuario coordinador.
# - ADMIN puede usar estas rutas y ver todo.
# ===========================================================

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db, establecer_contexto_sistema
from app.routers.auth import obtener_usuario_actual

from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.categoria import Categoria
from app.models.equipo import Equipo
from app.models.equipo_hoja_vida import EquipoHojaVida
from app.models.tecnico import Tecnico
from app.models.mantenimiento import Mantenimiento
from app.models.hist_mantenimiento import HistMantenimiento
from app.models.evidencia import Evidencia
from app.routers.evidencias import crear_url_firmada
from app.routers.equipos import (
    crear_excel_inventario,
    validar_estado_y_criticidad,
    validar_numero_inventario,
)
from app.services.mantenimiento_estado_service import aplicar_reapertura
from app.services.coordinador_empresas import ids_empresas_autorizadas


router = APIRouter(prefix="/coordinador", tags=["Coordinador PRO"])


# ===========================================================
# SCHEMAS INTERNOS
# ===========================================================

class EquipoCreate(BaseModel):
    nombre: str
    empresa_id: Optional[UUID] = None
    sede_id: UUID
    categoria_id: UUID
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    ubicacion: Optional[str] = None
    invima: Optional[str] = None
    codigo_id: Optional[str] = None
    inventario: Optional[str] = None
    estado: Optional[str] = "OPERATIVO"
    criticidad: Optional[str] = "MEDIA"
    activo: Optional[bool] = True


class EquipoUpdate(BaseModel):
    nombre: Optional[str] = None
    empresa_id: Optional[UUID] = None
    sede_id: Optional[UUID] = None
    categoria_id: Optional[UUID] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    ubicacion: Optional[str] = None
    invima: Optional[str] = None
    codigo_id: Optional[str] = None
    inventario: Optional[str] = None
    estado: Optional[str] = None
    criticidad: Optional[str] = None
    activo: Optional[bool] = None


class MantenimientoCreate(BaseModel):
    equipo_id: UUID
    tipo: str
    estado: Optional[str] = "PROGRAMADO"
    tecnico_id: Optional[UUID] = None
    empresa_id: Optional[UUID] = None
    sede_id: Optional[UUID] = None
    fecha_programada: Optional[datetime] = None
    fecha_inicio_programada: Optional[datetime] = None
    fecha_fin_programada: Optional[datetime] = None
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None
    estado_inicial: Optional[str] = None
    estado_inicial_equipo: Optional[str] = None
    acciones_realizadas: Optional[str] = None
    resultado_final: Optional[str] = None
    latitud: Optional[str] = None
    longitud: Optional[str] = None
    costo: Optional[float] = None


class MantenimientoUpdate(BaseModel):
    equipo_id: Optional[UUID] = None
    tipo: Optional[str] = None
    estado: Optional[str] = None
    tecnico_id: Optional[UUID] = None
    empresa_id: Optional[UUID] = None
    sede_id: Optional[UUID] = None
    fecha_programada: Optional[datetime] = None
    fecha_inicio_programada: Optional[datetime] = None
    fecha_fin_programada: Optional[datetime] = None
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None
    estado_inicial: Optional[str] = None
    estado_inicial_equipo: Optional[str] = None
    acciones_realizadas: Optional[str] = None
    resultado_final: Optional[str] = None
    latitud: Optional[str] = None
    longitud: Optional[str] = None
    costo: Optional[float] = None


class HojaVidaUpdate(BaseModel):
    adquisicion: Optional[str] = None
    costo: Optional[float] = None
    fecha_compra: Optional[str] = None
    fecha_instalacion: Optional[str] = None
    proveedor: Optional[str] = None
    pais_fabricacion: Optional[str] = None
    fecha_fabricacion: Optional[str] = None
    vida_util: Optional[str] = None
    requiere_calibracion: Optional[bool] = None
    rango_voltaje: Optional[str] = None
    rango_presion: Optional[str] = None
    gas_refrigerante: Optional[str] = None
    capacidad: Optional[str] = None
    rango_corriente: Optional[str] = None
    rango_velocidad: Optional[str] = None
    rango_potencia: Optional[str] = None
    rango_temperatura: Optional[str] = None
    frecuencia: Optional[str] = None
    rango_humedad: Optional[str] = None
    otros: Optional[str] = None
    manual_operacion: Optional[bool] = None
    manual_mantenimiento: Optional[bool] = None
    manual_partes: Optional[bool] = None
    manual_despiece: Optional[bool] = None
    plano_electronico: Optional[bool] = None
    plano_electrico: Optional[bool] = None
    plano_neumatico: Optional[bool] = None
    plano_mecanico: Optional[bool] = None
    clase_diagnostico: Optional[bool] = None
    clase_prevencion: Optional[bool] = None
    clase_rehabilitacion: Optional[bool] = None
    clase_analisis: Optional[bool] = None
    riesgo_bajo: Optional[bool] = None
    riesgo_moderado: Optional[bool] = None
    riesgo_alto: Optional[bool] = None
    riesgo_elevado: Optional[bool] = None


# ===========================================================
# HELPERS
# ===========================================================

def _rol(usuario: Usuario) -> str:
    return str(getattr(usuario, "rol", "") or "").upper()


def _es_admin(usuario: Usuario) -> bool:
    return _rol(usuario) == "ADMIN"


def _es_coordinador(usuario: Usuario) -> bool:
    return _rol(usuario) == "COORDINADOR"


def _validar_rol(usuario: Usuario):
    if not (_es_admin(usuario) or _es_coordinador(usuario)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso permitido solo para ADMIN o COORDINADOR",
        )


def _empresa_usuario(usuario: Usuario):
    return getattr(usuario, "empresa_id", None)


def _validar_coordinador_con_empresa(usuario: Usuario):
    _validar_rol(usuario)
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


def _nombre_objeto(obj):
    if not obj:
        return None

    usuario = getattr(obj, "usuario", None)
    if usuario:
        for campo in ["nombre_completo", "nombre", "username", "email"]:
            valor = getattr(usuario, campo, None)
            if valor:
                return str(valor)

    for campo in [
        "nombre", "nombre_completo", "codigo_id", "inventario",
        "codigo_inventario", "codigo", "serie", "documento",
        "especialidad", "cargo", "username", "email"
    ]:
        valor = getattr(obj, campo, None)
        if valor:
            return str(valor)

    return str(getattr(obj, "id", "Sin nombre"))


def _aplicar_empresa(query, modelo, usuario: Usuario):
    """
    Filtro genérico por empresa_id.
    ADMIN ve todo. COORDINADOR solo su empresa.
    """

    if _es_admin(usuario):
        return query

    _validar_coordinador_con_empresa(usuario)

    if hasattr(modelo, "empresa_id"):
        return query.filter(modelo.empresa_id == _empresa_usuario(usuario))

    return query


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
    return _aplicar_empresa(db.query(Equipo), Equipo, usuario)


def _query_sedes_por_usuario(db: Session, usuario: Usuario):
    return _aplicar_empresa(db.query(Sede), Sede, usuario)


def _query_empresas_por_usuario(db: Session, usuario: Usuario):
    query = db.query(Empresa)
    if _es_admin(usuario):
        return query
    _validar_coordinador_con_empresa(usuario)
    return query.filter(Empresa.id == _empresa_usuario(usuario))


def _query_categorias(db: Session):
    return db.query(Categoria).filter(Categoria.activo.is_(True))


def _validar_categoria_canonica(db: Session, categoria_id):
    if not categoria_id:
        raise HTTPException(status_code=422, detail="La categoría del equipo es obligatoria")
    categoria = db.query(Categoria).filter(
        Categoria.id == categoria_id,
        Categoria.activo.is_(True),
    ).first()
    if not categoria:
        raise HTTPException(status_code=422, detail="Categoría de activo no permitida")
    return categoria


def _validar_codigo_equipo(db: Session, codigo_id, excluir_equipo_id=None):
    codigo = str(codigo_id or "").strip()
    if not codigo:
        return None

    query = db.query(Equipo).filter(Equipo.codigo_id == codigo)
    if excluir_equipo_id:
        query = query.filter(Equipo.id != excluir_equipo_id)
    if query.first():
        raise HTTPException(status_code=400, detail="Ya existe un equipo con ese Codigo ID")

    return codigo


def _query_tecnicos_por_usuario(db: Session, usuario: Usuario):
    query = db.query(Tecnico)
    if hasattr(Tecnico, "usuario"):
        query = query.options(joinedload(Tecnico.usuario))

    if _es_admin(usuario):
        return query

    _validar_coordinador_con_empresa(usuario)

    if hasattr(Tecnico, "usuario_id"):
        return (
            query.join(Usuario, Tecnico.usuario_id == Usuario.id)
            .filter(Usuario.empresa_id == _empresa_usuario(usuario))
        )

    return query


def _validar_equipo_pertenece_empresa(db: Session, equipo_id, usuario: Usuario) -> Equipo:
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    if not _es_admin(usuario):
        _validar_coordinador_con_empresa(usuario)
        if getattr(equipo, "empresa_id", None) != _empresa_usuario(usuario):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El equipo no pertenece a la empresa del coordinador",
            )

    return equipo


def _validar_sede_pertenece_empresa(db: Session, sede_id, usuario: Usuario):
    if not sede_id or _es_admin(usuario):
        return

    _validar_coordinador_con_empresa(usuario)
    sede = db.query(Sede).filter(Sede.id == sede_id).first()

    if not sede or getattr(sede, "empresa_id", None) != _empresa_usuario(usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La sede no pertenece a la empresa del coordinador",
        )


def _validar_tecnico_pertenece_empresa(db: Session, tecnico_id, usuario: Usuario):
    if not tecnico_id or _es_admin(usuario):
        return

    _validar_coordinador_con_empresa(usuario)

    tecnico = (
        db.query(Tecnico)
        .join(Usuario, Tecnico.usuario_id == Usuario.id)
        .filter(Tecnico.id == tecnico_id, Usuario.empresa_id == _empresa_usuario(usuario))
        .first()
    )

    if not tecnico:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El técnico no pertenece a la empresa del coordinador",
        )


def _orden_mantenimiento():
    if hasattr(Mantenimiento, "created_at"):
        return Mantenimiento.created_at.desc()
    if hasattr(Mantenimiento, "creado_en"):
        return Mantenimiento.creado_en.desc()
    if hasattr(Mantenimiento, "fecha_programada"):
        return Mantenimiento.fecha_programada.desc()
    return Mantenimiento.id.desc()


def _serializar_catalogo(obj):
    usuario = getattr(obj, "usuario", None)
    nombre = _nombre_objeto(obj)

    return {
        "id": str(getattr(obj, "id", "")),
        "nombre": nombre,
        "nombre_completo": nombre,
        "usuario_nombre": nombre,
        "email": getattr(usuario, "email", None) if usuario else getattr(obj, "email", None),
        "username": getattr(usuario, "username", None) if usuario else getattr(obj, "username", None),
        "codigo": getattr(obj, "codigo", None),
        "codigo_id": getattr(obj, "codigo_id", None),
        "codigo_inventario": getattr(obj, "inventario", None) or getattr(obj, "codigo_inventario", None),
        "inventario": getattr(obj, "inventario", None),
        "serie": getattr(obj, "serie", None),
        "empresa_id": str(getattr(obj, "empresa_id", "")) if getattr(obj, "empresa_id", None) else None,
        "sede_id": str(getattr(obj, "sede_id", "")) if getattr(obj, "sede_id", None) else None,
        "categoria_id": str(getattr(obj, "categoria_id", "")) if getattr(obj, "categoria_id", None) else None,
        "marca": getattr(obj, "marca", None),
        "modelo": getattr(obj, "modelo", None),
        "ubicacion": getattr(obj, "ubicacion", None),
        "estado": getattr(obj, "estado", None),
        "criticidad": getattr(obj, "criticidad", None),
        "activo": getattr(obj, "activo", None),
    }


def _serializar_equipo(equipo: Equipo, db: Session = None):
    data = _serializar_catalogo(equipo)

    empresa = db.query(Empresa).filter(Empresa.id == equipo.empresa_id).first() if db and getattr(equipo, "empresa_id", None) else None
    sede = db.query(Sede).filter(Sede.id == equipo.sede_id).first() if db and getattr(equipo, "sede_id", None) else None
    categoria = db.query(Categoria).filter(Categoria.id == equipo.categoria_id).first() if db and getattr(equipo, "categoria_id", None) else None
    hoja = db.query(EquipoHojaVida).filter(EquipoHojaVida.equipo_id == equipo.id).first() if db else None

    data.update({
        "empresa_nombre": empresa.nombre if empresa else None,
        "sede_nombre": sede.nombre if sede else None,
        "categoria_nombre": categoria.nombre if categoria else None,
        "tiene_hoja_vida": bool(hoja),
        "created_at": _fecha_iso(getattr(equipo, "created_at", None)),
        "updated_at": _fecha_iso(getattr(equipo, "updated_at", None)),
    })

    return data


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
        "fecha_inicio_programada": _fecha_iso(getattr(m, "fecha_inicio_programada", None)),
        "fecha_fin_programada": _fecha_iso(getattr(m, "fecha_fin_programada", None)),
        "fecha_inicio": _fecha_iso(getattr(m, "fecha_inicio", None)),
        "fecha_fin": _fecha_iso(getattr(m, "fecha_fin", None)),
        "fecha_asignacion": _fecha_iso(getattr(m, "fecha_asignacion", None)),
        "fecha_finalizacion": _fecha_iso(getattr(m, "fecha_finalizacion", None)),

        "descripcion": getattr(m, "descripcion", None),
        "observaciones": getattr(m, "observaciones", None),
        "estado_inicial": getattr(m, "estado_inicial", None) or getattr(m, "estado_inicial_equipo", None),
        "estado_inicial_equipo": getattr(m, "estado_inicial_equipo", None) or getattr(m, "estado_inicial", None),
        "acciones_realizadas": getattr(m, "acciones_realizadas", None),
        "resultado_final": getattr(m, "resultado_final", None),
        "latitud": getattr(m, "latitud", None),
        "longitud": getattr(m, "longitud", None),
        "observacion_estado": getattr(m, "observacion_estado", None),
        "motivo_anulacion": getattr(m, "motivo_anulacion", None),
        "costo": float(m.costo) if getattr(m, "costo", None) else 0,

        "created_at": _fecha_iso(getattr(m, "created_at", None)),
        "updated_at": _fecha_iso(getattr(m, "updated_at", None)),
        "creado_en": _fecha_iso(getattr(m, "creado_en", None)),
        "actualizado_en": _fecha_iso(getattr(m, "actualizado_en", None)),
    }


def _serializar_hoja(hoja):
    if not hoja:
        return None

    campos = [
        "id", "equipo_id", "adquisicion", "costo", "fecha_compra", "fecha_instalacion",
        "proveedor", "pais_fabricacion", "fecha_fabricacion", "vida_util",
        "requiere_calibracion", "rango_voltaje", "rango_presion", "gas_refrigerante",
        "capacidad", "rango_corriente", "rango_velocidad", "rango_potencia",
        "rango_temperatura", "frecuencia", "rango_humedad", "otros",
        "manual_operacion", "manual_mantenimiento", "manual_partes", "manual_despiece",
        "plano_electronico", "plano_electrico", "plano_neumatico", "plano_mecanico",
        "clase_diagnostico", "clase_prevencion", "clase_rehabilitacion", "clase_analisis",
        "riesgo_bajo", "riesgo_moderado", "riesgo_alto", "riesgo_elevado",
        "created_at", "updated_at",
    ]

    data = {}
    for campo in campos:
        valor = getattr(hoja, campo, None)
        if campo in ["id", "equipo_id"] and valor:
            data[campo] = str(valor)
        elif "fecha" in campo or campo in ["created_at", "updated_at"]:
            data[campo] = _fecha_iso(valor)
        elif campo == "costo" and valor is not None:
            data[campo] = float(valor)
        else:
            data[campo] = valor
    return data


def _serializar_evidencia(e, db: Session):
    equipo = db.query(Equipo).filter(Equipo.id == e.equipo_id).first() if getattr(e, "equipo_id", None) else None
    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == e.mantenimiento_id).first() if getattr(e, "mantenimiento_id", None) else None

    return {
        "id": str(e.id),
        "tipo": getattr(e, "tipo", None),
        "archivo_url": crear_url_firmada(e.id, getattr(e, "archivo_url", None)),
        "nombre_original": getattr(e, "nombre_original", None),
        "descripcion": getattr(e, "descripcion", None),
        "equipo_id": str(e.equipo_id) if getattr(e, "equipo_id", None) else None,
        "equipo_nombre": _nombre_objeto(equipo) if equipo else "Sin equipo",
        "mantenimiento_id": str(e.mantenimiento_id) if getattr(e, "mantenimiento_id", None) else None,
        "mantenimiento_tipo": getattr(mantenimiento, "tipo", None) if mantenimiento else None,
        "created_at": _fecha_iso(getattr(e, "created_at", None)),
    }


# ===========================================================
# DASHBOARD
# ===========================================================

@router.get("/empresas-autorizadas")
def empresas_autorizadas_coordinador(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_rol(usuario_actual)
    if _es_admin(usuario_actual):
        establecer_contexto_sistema(db)
        empresas = db.query(Empresa).order_by(Empresa.nombre).all()
    else:
        ids = ids_empresas_autorizadas(db, usuario_actual)
        establecer_contexto_sistema(db)
        empresas = db.query(Empresa).filter(Empresa.id.in_(ids)).order_by(Empresa.nombre).all()

    return [
        {
            "id": str(empresa.id),
            "nombre": empresa.nombre,
            "es_principal": str(empresa.id) == str(
                getattr(usuario_actual, "empresa_id_principal", usuario_actual.empresa_id)
            ),
        }
        for empresa in empresas
    ]

@router.get("/dashboard")
def dashboard_coordinador(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_rol(usuario_actual)

    mantenimientos = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db),
        usuario_actual,
    ).all()

    equipos = _query_equipos_por_usuario(db, usuario_actual).all()
    tecnicos = _query_tecnicos_por_usuario(db, usuario_actual).all()

    por_estado = {}
    por_tipo = {}

    for m in mantenimientos:
        estado = getattr(m, "estado", None) or "SIN_ESTADO"
        tipo = getattr(m, "tipo", None) or "SIN_TIPO"
        por_estado[estado] = por_estado.get(estado, 0) + 1
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    return {
        "metricas": {
            "total_mantenimientos": len(mantenimientos),
            "programados": por_estado.get("PROGRAMADO", 0),
            "asignados": por_estado.get("ASIGNADO", 0),
            "en_proceso": por_estado.get("EN_PROCESO", 0),
            "pausados": por_estado.get("PAUSADO", 0),
            "finalizados": por_estado.get("FINALIZADO", 0),
            "anulados": por_estado.get("ANULADO", 0),
            "equipos": len(equipos),
            "tecnicos": len(tecnicos),
        },
        "por_estado": por_estado,
        "por_tipo": por_tipo,
        "mantenimientos_recientes": [_serializar_mantenimiento(m) for m in mantenimientos[:10]],
    }


# ===========================================================
# CATÁLOGOS
# ===========================================================

@router.get("/catalogos")
def catalogos_coordinador(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_rol(usuario_actual)

    empresas = _query_empresas_por_usuario(db, usuario_actual).all()
    sedes = _query_sedes_por_usuario(db, usuario_actual).all()
    equipos = _query_equipos_por_usuario(db, usuario_actual).all()
    tecnicos = _query_tecnicos_por_usuario(db, usuario_actual).all()
    categorias = _query_categorias(db).all()

    return {
        "empresas": [_serializar_catalogo(e) for e in empresas],
        "sedes": [_serializar_catalogo(s) for s in sedes],
        "equipos": [_serializar_equipo(e, db) for e in equipos],
        "tecnicos": [_serializar_catalogo(t) for t in tecnicos],
        "categorias": [_serializar_catalogo(c) for c in categorias],
    }


# ===========================================================
# INVENTARIO / EQUIPOS
# ===========================================================

@router.get("/equipos")
def listar_equipos_coordinador(
    response: Response,
    busqueda: Optional[str] = Query(default=None, max_length=150),
    sede_id: Optional[UUID] = Query(default=None),
    categoria_id: Optional[UUID] = Query(default=None),
    estado: Optional[str] = Query(default=None, max_length=50),
    criticidad: Optional[str] = Query(default=None, max_length=50),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_rol(usuario_actual)
    query = _query_equipos_por_usuario(db, usuario_actual)
    if busqueda:
        patron = f"%{busqueda.strip()}%"
        query = query.filter(
            or_(
                Equipo.nombre.ilike(patron),
                Equipo.marca.ilike(patron),
                Equipo.modelo.ilike(patron),
                Equipo.serie.ilike(patron),
                Equipo.ubicacion.ilike(patron),
                Equipo.codigo_id.ilike(patron),
                Equipo.inventario.ilike(patron),
            )
        )
    if sede_id:
        query = query.filter(Equipo.sede_id == sede_id)
    if categoria_id:
        query = query.filter(Equipo.categoria_id == categoria_id)
    if estado:
        query = query.filter(Equipo.estado == estado)
    if criticidad:
        query = query.filter(Equipo.criticidad == criticidad)

    total = query.order_by(None).count()
    equipos = query.order_by(Equipo.created_at.desc()).offset(offset).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Limit"] = str(limit)
    response.headers["X-Offset"] = str(offset)
    return [_serializar_equipo(e, db) for e in equipos]


@router.post("/equipos", status_code=201)
def crear_equipo_coordinador(
    data: EquipoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_rol(usuario_actual)
    _validar_sede_pertenece_empresa(db, data.sede_id, usuario_actual)
    _validar_categoria_canonica(db, data.categoria_id)
    validar_estado_y_criticidad(data.estado, data.criticidad)

    empresa_id = data.empresa_id if _es_admin(usuario_actual) else _empresa_usuario(usuario_actual)
    if not empresa_id:
        raise HTTPException(status_code=400, detail="No fue posible determinar la empresa del equipo")

    payload = data.model_dump(exclude_unset=True)
    payload["empresa_id"] = empresa_id
    payload["codigo_id"] = _validar_codigo_equipo(db, payload.get("codigo_id"))
    payload["inventario"] = validar_numero_inventario(db, payload.get("inventario"))

    nuevo = Equipo(**payload)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return _serializar_equipo(nuevo, db)


@router.put("/equipos/{equipo_id}")
def actualizar_equipo_coordinador(
    equipo_id: UUID,
    data: EquipoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    equipo = _validar_equipo_pertenece_empresa(db, equipo_id, usuario_actual)
    payload = data.model_dump(exclude_unset=True)

    if not _es_admin(usuario_actual):
        payload.pop("empresa_id", None)

    if payload.get("sede_id"):
        _validar_sede_pertenece_empresa(db, payload["sede_id"], usuario_actual)
    if "categoria_id" in payload:
        _validar_categoria_canonica(db, payload["categoria_id"])
    if "estado" in payload or "criticidad" in payload:
        validar_estado_y_criticidad(
            payload.get("estado", equipo.estado),
            payload.get("criticidad", equipo.criticidad),
        )
    if "inventario" in payload:
        payload["inventario"] = validar_numero_inventario(
            db,
            payload["inventario"],
            excluir_equipo_id=equipo_id,
        )
    if "codigo_id" in payload:
        payload["codigo_id"] = _validar_codigo_equipo(
            db,
            payload["codigo_id"],
            excluir_equipo_id=equipo_id,
        )

    for campo, valor in payload.items():
        if hasattr(equipo, campo):
            setattr(equipo, campo, valor)

    db.commit()
    db.refresh(equipo)
    return _serializar_equipo(equipo, db)


@router.get("/equipos/exportar")
def exportar_inventario_coordinador(
    busqueda: Optional[str] = Query(default=None),
    sede_id: Optional[UUID] = Query(default=None),
    categoria_id: Optional[UUID] = Query(default=None),
    estado: Optional[str] = Query(default=None),
    criticidad: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_rol(usuario_actual)

    query = (
        db.query(
            Equipo,
            Empresa.nombre.label("empresa_nombre"),
            Sede.nombre.label("sede_nombre"),
            Categoria.nombre.label("categoria_nombre"),
        )
        .outerjoin(Empresa, Empresa.id == Equipo.empresa_id)
        .outerjoin(Sede, Sede.id == Equipo.sede_id)
        .outerjoin(Categoria, Categoria.id == Equipo.categoria_id)
    )

    if not _es_admin(usuario_actual):
        _validar_coordinador_con_empresa(usuario_actual)
        query = query.filter(Equipo.empresa_id == _empresa_usuario(usuario_actual))

    if sede_id:
        query = query.filter(Equipo.sede_id == sede_id)
    if categoria_id:
        query = query.filter(Equipo.categoria_id == categoria_id)
    if estado:
        query = query.filter(Equipo.estado == estado)
    if criticidad:
        query = query.filter(Equipo.criticidad == criticidad)
    if busqueda:
        patron = f"%{busqueda.strip().lower()}%"
        query = query.filter(or_(
            func.lower(Equipo.nombre).like(patron),
            func.lower(Equipo.marca).like(patron),
            func.lower(Equipo.modelo).like(patron),
            func.lower(Equipo.serie).like(patron),
            func.lower(Equipo.ubicacion).like(patron),
            func.lower(Equipo.codigo_id).like(patron),
            func.lower(Equipo.inventario).like(patron),
        ))

    registros = query.order_by(Empresa.nombre, Sede.nombre, Equipo.nombre).all()
    filas = [
        {
            "codigo_inventario": equipo.codigo_id,
            "nombre": equipo.nombre,
            "empresa": empresa_nombre,
            "sede": sede_nombre,
            "categoria": categoria_nombre,
            "marca": equipo.marca,
            "modelo": equipo.modelo,
            "serie": equipo.serie,
            "ubicacion": equipo.ubicacion,
            "estado": equipo.estado,
            "criticidad": equipo.criticidad,
            "invima": equipo.invima,
            "inventario": equipo.inventario,
            "activo": "SI" if equipo.activo else "NO",
            "fecha_creacion": equipo.created_at,
        }
        for equipo, empresa_nombre, sede_nombre, categoria_nombre in registros
    ]

    filename = f"inventario_equipos_coordinador_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        crear_excel_inventario(filas),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ===========================================================
# HOJA DE VIDA
# ===========================================================

@router.get("/equipos/{equipo_id}/hoja-vida")
def obtener_hoja_vida_coordinador(
    equipo_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    equipo = _validar_equipo_pertenece_empresa(db, equipo_id, usuario_actual)

    empresa = db.query(Empresa).filter(Empresa.id == equipo.empresa_id).first()
    sede = db.query(Sede).filter(Sede.id == equipo.sede_id).first()
    categoria = db.query(Categoria).filter(Categoria.id == equipo.categoria_id).first() if equipo.categoria_id else None
    hoja = db.query(EquipoHojaVida).filter(EquipoHojaVida.equipo_id == equipo_id).first()

    return {
        "encabezado": {
            "empresa_nombre": empresa.nombre if empresa else None,
            "empresa_logo_url": empresa.logo_url if empresa else None,
            "sede_nombre": sede.nombre if sede else None,
        },
        "equipo_basico": {
            **_serializar_equipo(equipo, db),
            "categoria": categoria.nombre if categoria else None,
        },
        "hoja_vida_tecnica": _serializar_hoja(hoja),
    }


@router.put("/equipos/{equipo_id}/hoja-vida")
def actualizar_hoja_vida_coordinador(
    equipo_id: UUID,
    data: HojaVidaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_equipo_pertenece_empresa(db, equipo_id, usuario_actual)

    hoja = db.query(EquipoHojaVida).filter(EquipoHojaVida.equipo_id == equipo_id).first()

    if not hoja:
        hoja = EquipoHojaVida(equipo_id=equipo_id)
        db.add(hoja)
        db.flush()

    payload = data.model_dump(exclude_unset=True)

    for campo, valor in payload.items():
        if hasattr(hoja, campo):
            setattr(hoja, campo, valor)

    db.commit()
    db.refresh(hoja)

    return _serializar_hoja(hoja)


# ===========================================================
# MANTENIMIENTOS
# ===========================================================

@router.get("/mantenimientos")
def listar_mantenimientos(
    response: Response,
    estado: Optional[str] = Query(default=None),
    equipo_id: Optional[UUID] = Query(default=None),
    tecnico_id: Optional[UUID] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_rol(usuario_actual)

    query = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db),
        usuario_actual,
    )

    if estado:
        query = query.filter(Mantenimiento.estado == estado)
    if equipo_id:
        query = query.filter(Mantenimiento.equipo_id == equipo_id)
    if tecnico_id:
        query = query.filter(Mantenimiento.tecnico_id == tecnico_id)

    total = query.order_by(None).count()
    mantenimientos = query.order_by(_orden_mantenimiento()).offset(offset).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Limit"] = str(limit)
    response.headers["X-Offset"] = str(offset)
    return [_serializar_mantenimiento(m) for m in mantenimientos]


@router.post("/mantenimientos", status_code=201)
def crear_mantenimiento(
    data: MantenimientoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    equipo = _validar_equipo_pertenece_empresa(db, data.equipo_id, usuario_actual)
    _validar_tecnico_pertenece_empresa(db, data.tecnico_id, usuario_actual)

    payload = data.model_dump(exclude_unset=True)
    payload["empresa_id"] = data.empresa_id if _es_admin(usuario_actual) and data.empresa_id else equipo.empresa_id
    payload["sede_id"] = (
        data.sede_id
        if _es_admin(usuario_actual) and data.sede_id
        else getattr(equipo, "sede_id", None)
    )
    payload["estado"] = payload.get("estado") or "PROGRAMADO"

    nuevo = Mantenimiento(**payload)
    db.add(nuevo)
    db.flush()
    db.add(HistMantenimiento(
        mantenimiento_id=nuevo.id,
        estado_anterior=None,
        estado_nuevo=nuevo.estado,
        tecnico_id=nuevo.tecnico_id,
        observacion="Mantenimiento creado desde el portal coordinador.",
        creado_por=usuario_actual.nombre_completo or _rol(usuario_actual),
    ))
    db.commit()
    db.refresh(nuevo)

    return _serializar_mantenimiento(nuevo)


@router.put("/mantenimientos/{mantenimiento_id}")
def actualizar_mantenimiento(
    mantenimiento_id: UUID,
    data: MantenimientoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    query = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db).filter(Mantenimiento.id == mantenimiento_id),
        usuario_actual,
    )

    mantenimiento = query.first()
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    payload = data.model_dump(exclude_unset=True)

    estado_actual = str(mantenimiento.estado or "").upper()
    estado_solicitado = str(payload.get("estado") or mantenimiento.estado or "").upper()
    if estado_actual == "FINALIZADO" and estado_solicitado != "FINALIZADO":
        raise HTTPException(
            status_code=409,
            detail="Usa la opción Reabrir e indica el motivo de la corrección.",
        )

    if payload.get("equipo_id"):
        equipo = _validar_equipo_pertenece_empresa(db, payload["equipo_id"], usuario_actual)
        payload["empresa_id"] = getattr(equipo, "empresa_id", None)
        payload["sede_id"] = payload.get("sede_id") or getattr(equipo, "sede_id", None)

    if payload.get("tecnico_id"):
        _validar_tecnico_pertenece_empresa(db, payload["tecnico_id"], usuario_actual)

    if not _es_admin(usuario_actual):
        payload.pop("empresa_id", None)
        payload.pop("sede_id", None)

    for campo, valor in payload.items():
        if hasattr(mantenimiento, campo):
            setattr(mantenimiento, campo, valor)

    db.commit()
    db.refresh(mantenimiento)

    return _serializar_mantenimiento(mantenimiento)


@router.put("/mantenimientos/{mantenimiento_id}/asignar")
def asignar_tecnico(
    mantenimiento_id: UUID,
    tecnico_id: UUID = Query(...),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_tecnico_pertenece_empresa(db, tecnico_id, usuario_actual)

    mantenimiento = _aplicar_filtro_empresa_mantenimientos(
        db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id),
        usuario_actual,
    ).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    if str(mantenimiento.estado or "").upper() == "FINALIZADO":
        raise HTTPException(
            status_code=409,
            detail="Reabre el mantenimiento antes de cambiar el técnico asignado.",
        )

    mantenimiento.tecnico_id = tecnico_id
    mantenimiento.estado = "ASIGNADO"
    if hasattr(mantenimiento, "fecha_asignacion"):
        mantenimiento.fecha_asignacion = datetime.utcnow()

    db.commit()
    db.refresh(mantenimiento)

    return _serializar_mantenimiento(mantenimiento)


@router.put("/mantenimientos/{mantenimiento_id}/estado")
def cambiar_estado(
    mantenimiento_id: UUID,
    estado: str = Query(...),
    observacion: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    mantenimiento = _aplicar_filtro_empresa_mantenimientos(
        db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id),
        usuario_actual,
    ).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    estado_actual = str(mantenimiento.estado or "").upper()
    estado_nuevo = str(estado or "").upper()

    if estado_actual == "FINALIZADO":
        if estado_nuevo != "EN_PROCESO":
            raise HTTPException(
                status_code=409,
                detail="Un mantenimiento finalizado solo puede reabrirse a EN_PROCESO.",
            )

        motivo = str(observacion or "").strip()
        if len(motivo) < 10:
            raise HTTPException(
                status_code=422,
                detail="Indica el motivo de la reapertura con al menos 10 caracteres.",
            )

        estado_anterior = aplicar_reapertura(mantenimiento)
        mantenimiento.observacion_estado = f"Reabierto para corrección: {motivo}"
        db.add(HistMantenimiento(
            mantenimiento_id=mantenimiento.id,
            estado_anterior=estado_anterior,
            estado_nuevo="EN_PROCESO",
            tecnico_id=mantenimiento.tecnico_id,
            observacion=motivo,
            creado_por=usuario_actual.nombre_completo or _rol(usuario_actual),
        ))
        db.commit()
        db.refresh(mantenimiento)
        return _serializar_mantenimiento(mantenimiento)

    mantenimiento.estado = estado_nuevo
    if observacion and hasattr(mantenimiento, "observacion_estado"):
        mantenimiento.observacion_estado = observacion

    if estado_nuevo == "EN_PROCESO" and hasattr(mantenimiento, "fecha_inicio"):
        mantenimiento.fecha_inicio = mantenimiento.fecha_inicio or datetime.utcnow()
    if estado_nuevo == "FINALIZADO":
        if hasattr(mantenimiento, "fecha_fin"):
            mantenimiento.fecha_fin = datetime.utcnow()
        if hasattr(mantenimiento, "fecha_finalizacion"):
            mantenimiento.fecha_finalizacion = datetime.utcnow()

    db.commit()
    db.refresh(mantenimiento)

    return _serializar_mantenimiento(mantenimiento)


@router.put("/mantenimientos/{mantenimiento_id}/reprogramar")
def reprogramar(
    mantenimiento_id: UUID,
    fecha_programada: datetime,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    mantenimiento = _aplicar_filtro_empresa_mantenimientos(
        db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id),
        usuario_actual,
    ).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    mantenimiento.fecha_programada = fecha_programada
    db.commit()
    db.refresh(mantenimiento)

    return _serializar_mantenimiento(mantenimiento)


@router.delete("/mantenimientos/{mantenimiento_id}")
def eliminar_mantenimiento(
    mantenimiento_id: UUID,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    mantenimiento = _aplicar_filtro_empresa_mantenimientos(
        db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id),
        usuario_actual,
    ).first()

    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")

    db.delete(mantenimiento)
    db.commit()

    return {"message": "Mantenimiento eliminado correctamente"}


# ===========================================================
# CRONOGRAMA / EVIDENCIAS / INFORMES
# ===========================================================

@router.get("/cronograma")
def cronograma(
    response: Response,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    query = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db),
        usuario_actual,
    )
    total = query.order_by(None).count()
    mantenimientos = query.order_by(Mantenimiento.fecha_programada.asc()).offset(offset).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)

    return [_serializar_mantenimiento(m) for m in mantenimientos]


@router.get("/evidencias")
def evidencias_coordinador(
    response: Response,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    _validar_rol(usuario_actual)

    query = db.query(Evidencia)

    if not _es_admin(usuario_actual):
        _validar_coordinador_con_empresa(usuario_actual)
        query = (
            query.join(Equipo, Evidencia.equipo_id == Equipo.id)
            .filter(Equipo.empresa_id == _empresa_usuario(usuario_actual))
        )

    total = query.order_by(None).count()
    evidencias = query.order_by(Evidencia.created_at.desc()).offset(offset).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)
    return [_serializar_evidencia(e, db) for e in evidencias]


@router.get("/informes")
def informes(
    response: Response,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    query = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db),
        usuario_actual,
    )
    total = query.order_by(None).count()
    mantenimientos = query.order_by(_orden_mantenimiento()).offset(offset).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)

    return [_serializar_mantenimiento(m) for m in mantenimientos]


@router.get("/informes/resumen")
def resumen_informes(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    mantenimientos = _aplicar_filtro_empresa_mantenimientos(
        _query_mantenimientos_base(db),
        usuario_actual,
    ).all()

    por_estado = {}
    por_tipo = {}

    for m in mantenimientos:
        estado = getattr(m, "estado", None) or "SIN_ESTADO"
        tipo = getattr(m, "tipo", None) or "SIN_TIPO"
        por_estado[estado] = por_estado.get(estado, 0) + 1
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    return {
        "total": len(mantenimientos),
        "por_estado": por_estado,
        "por_tipo": por_tipo,
    }
