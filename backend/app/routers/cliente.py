# ============================================================
# ROUTER CLIENTE - PORTAL MULTIEMPRESA SGA PRO
# Archivo: backend/app/routers/cliente.py
#
# Objetivo:
#   - Portal cliente SaaS multiempresa.
#   - El cliente solo consulta información de su empresa.
#   - Consulta sedes, equipos, mantenimientos, hoja de vida y evidencias.
# ============================================================

from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.equipo import Equipo
from app.models.mantenimiento import Mantenimiento
from app.models.usuario import Usuario
from app.routers.auth import obtener_usuario_actual
from app.routers.evidencias import serializar_evidencia

# Import seguro de hoja de vida
try:
    from app.models.equipo_hoja_vida import EquipoHojaVida
except Exception:
    EquipoHojaVida = None

# Import seguro de evidencias
try:
    from app.models.evidencia import Evidencia
except Exception:
    Evidencia = None


router = APIRouter(prefix="/cliente", tags=["Portal Cliente"])


# ============================================================
# HELPERS
# ============================================================

def serialize(obj):
    """
    Convierte modelos SQLAlchemy a diccionario simple.
    UUID y fechas se convierten a string para evitar errores en frontend.
    """
    if obj is None:
        return None

    data = {}

    for column in obj.__table__.columns:
        value = getattr(obj, column.name)

        if value is None:
            data[column.name] = None
        else:
            data[column.name] = str(value)

    return data


def validar_acceso_empresa(empresa_id: UUID, usuario: Usuario):
    """Autoriza el tenant desde el JWT, nunca desde datos confiados al cliente."""
    rol = str(getattr(usuario, "rol", "") or "").strip().upper()

    if rol == "ADMIN":
        return

    if rol not in {"CLIENTE", "EMPRESA", "COORDINADOR"}:
        raise HTTPException(status_code=403, detail="Rol sin acceso al portal cliente")

    empresa_usuario = getattr(usuario, "empresa_id", None)
    if not empresa_usuario or str(empresa_usuario) != str(empresa_id):
        # No revelar si el tenant solicitado existe.
        raise HTTPException(status_code=403, detail="Acceso denegado para esta empresa")


def validar_empresa(empresa_id: UUID, db: Session, usuario: Usuario):
    """
    Valida que la empresa exista.
    """
    validar_acceso_empresa(empresa_id, usuario)
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return empresa


def obtener_ids_equipos_empresa(empresa_id: UUID, db: Session):
    """
    Obtiene los IDs de equipos pertenecientes a una empresa.
    """
    equipos = db.query(Equipo.id).filter(Equipo.empresa_id == empresa_id).all()
    return [e[0] for e in equipos]


def clasificar_estado_dashboard(mantenimiento, ahora=None):
    """Normaliza los estados operativos en las cuatro categorías ejecutivas."""
    ahora = ahora or datetime.now()
    estado = str(getattr(mantenimiento, "estado", "") or "").upper()
    if estado == "FINALIZADO":
        return "COMPLETADO"
    if estado == "EN_PROCESO":
        return "EN_PROCESO"
    fecha = getattr(mantenimiento, "fecha_programada", None)
    if fecha and fecha < ahora and estado != "ANULADO":
        return "RETRASADO"
    return "PENDIENTE"


def porcentaje_cumplimiento_preventivo(mantenimientos, inicio_mes, fin_mes):
    plan = [
        m for m in mantenimientos
        if str(getattr(m, "tipo", "") or "").upper() == "PREVENTIVO"
        and getattr(m, "fecha_programada", None)
        and inicio_mes <= m.fecha_programada < fin_mes
        and str(getattr(m, "estado", "") or "").upper() != "ANULADO"
    ]
    if not plan:
        return 100.0
    ejecutadas = sum(1 for m in plan if str(getattr(m, "estado", "") or "").upper() == "FINALIZADO")
    return round((ejecutadas / len(plan)) * 100, 1)


# ============================================================
# DASHBOARD CLIENTE
# ============================================================

@router.get("/{empresa_id}/dashboard")
def dashboard_cliente(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    empresa = validar_empresa(empresa_id, db, usuario)
    equipo_ids = obtener_ids_equipos_empresa(empresa_id, db)

    total_sedes = db.query(Sede).filter(Sede.empresa_id == empresa_id).count()
    total_equipos = db.query(Equipo).filter(Equipo.empresa_id == empresa_id).count()

    mantenimientos = []
    if equipo_ids:
        mantenimientos = db.query(Mantenimiento).filter(
            or_(Mantenimiento.empresa_id == empresa_id, Mantenimiento.equipo_id.in_(equipo_ids))
        ).all()

    ahora = datetime.now()
    inicio_mes = datetime(ahora.year, ahora.month, 1)
    fin_mes = datetime(ahora.year + (1 if ahora.month == 12 else 0), 1 if ahora.month == 12 else ahora.month + 1, 1)
    pendientes = sum(1 for m in mantenimientos if str(m.estado or "").upper() not in {"FINALIZADO", "ANULADO"})
    realizados = sum(1 for m in mantenimientos if str(m.estado or "").upper() == "FINALIZADO")
    ejecutadas_mes = sum(
        1 for m in mantenimientos
        if str(m.estado or "").upper() == "FINALIZADO"
        and (getattr(m, "fecha_finalizacion", None) or getattr(m, "fecha_fin", None))
        and inicio_mes <= (getattr(m, "fecha_finalizacion", None) or getattr(m, "fecha_fin", None)) < fin_mes
    )

    distribucion = {"PENDIENTE": 0, "EN_PROCESO": 0, "COMPLETADO": 0, "RETRASADO": 0}
    for mantenimiento in mantenimientos:
        if str(mantenimiento.estado or "").upper() != "ANULADO":
            distribucion[clasificar_estado_dashboard(mantenimiento, ahora)] += 1

    sedes = db.query(Sede).filter(Sede.empresa_id == empresa_id).order_by(Sede.nombre).all()
    equipos_por_id = {
        equipo.id: equipo for equipo in db.query(Equipo).filter(Equipo.empresa_id == empresa_id).all()
    }
    barras_sedes = []
    for sede in sedes:
        items = [
            m for m in mantenimientos
            if str(getattr(m, "sede_id", "") or getattr(equipos_por_id.get(m.equipo_id), "sede_id", "")) == str(sede.id)
        ]
        barras_sedes.append({
            "sede": sede.nombre,
            "preventivos": sum(1 for m in items if str(m.tipo or "").upper() == "PREVENTIVO"),
            "correctivos": sum(1 for m in items if str(m.tipo or "").upper() == "CORRECTIVO"),
        })

    actividad_hoy = []
    for m in mantenimientos:
        if str(m.estado or "").upper() != "EN_PROCESO":
            continue
        equipo = equipos_por_id.get(m.equipo_id)
        sede = next((s for s in sedes if str(s.id) == str(m.sede_id or getattr(equipo, "sede_id", None))), None)
        actividad_hoy.append({
            "id": str(m.id),
            "equipo": getattr(equipo, "nombre", "Equipo"),
            "sede": getattr(sede, "nombre", "Sede"),
            "direccion": getattr(sede, "direccion", None),
            "tipo": m.tipo,
            "estado": m.estado,
            "fecha_inicio": str(m.fecha_inicio) if m.fecha_inicio else None,
            "latitud": m.latitud,
            "longitud": m.longitud,
        })

    return {
        "empresa": serialize(empresa),
        "empresa_id": str(empresa_id),
        "total_sedes": total_sedes,
        "total_equipos": total_equipos,
        "mantenimientos_pendientes": pendientes,
        "mantenimientos_realizados": realizados,
        "ots_ejecutadas_mes": ejecutadas_mes,
        "cumplimiento_preventivo": porcentaje_cumplimiento_preventivo(mantenimientos, inicio_mes, fin_mes),
        "distribucion_estados": [
            {"estado": estado, "cantidad": cantidad} for estado, cantidad in distribucion.items()
        ],
        "mantenimientos_por_sede": barras_sedes,
        "actividad_hoy": actividad_hoy,
        "actualizado_en": ahora.isoformat(),
    }


# ============================================================
# SEDES DEL CLIENTE
# ============================================================

@router.get("/{empresa_id}/sedes")
def sedes_cliente(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    validar_empresa(empresa_id, db, usuario)

    sedes = db.query(Sede).filter(Sede.empresa_id == empresa_id).all()
    resultado = []

    for sede in sedes:
        equipos = db.query(Equipo).filter(
            Equipo.empresa_id == empresa_id,
            Equipo.sede_id == sede.id
        ).all()

        equipo_ids = [e.id for e in equipos]
        total_mantenimientos = 0

        if equipo_ids:
            total_mantenimientos = db.query(Mantenimiento).filter(
                Mantenimiento.equipo_id.in_(equipo_ids)
            ).count()

        item = serialize(sede)
        item["total_equipos"] = len(equipos)
        item["total_mantenimientos"] = total_mantenimientos
        resultado.append(item)

    return resultado


# ============================================================
# DETALLE SEDE CLIENTE
# ============================================================

@router.get("/{empresa_id}/sedes/{sede_id}")
def detalle_sede_cliente(
    empresa_id: UUID,
    sede_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    validar_empresa(empresa_id, db, usuario)

    sede = db.query(Sede).filter(
        Sede.id == sede_id,
        Sede.empresa_id == empresa_id
    ).first()

    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    equipos = db.query(Equipo).filter(
        Equipo.empresa_id == empresa_id,
        Equipo.sede_id == sede_id
    ).all()

    equipo_ids = [e.id for e in equipos]

    mantenimientos = []
    if equipo_ids:
        mantenimientos = db.query(Mantenimiento).filter(
            Mantenimiento.equipo_id.in_(equipo_ids)
        ).all()

    return {
        "sede": serialize(sede),
        "equipos": [serialize(e) for e in equipos],
        "mantenimientos": [serialize(m) for m in mantenimientos],
    }


# ============================================================
# EQUIPOS DEL CLIENTE
# ============================================================

@router.get("/{empresa_id}/equipos")
def equipos_cliente(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    validar_empresa(empresa_id, db, usuario)

    equipos = db.query(Equipo).filter(
        Equipo.empresa_id == empresa_id
    ).order_by(Equipo.nombre.asc()).all()

    return [serialize(e) for e in equipos]


# ============================================================
# MANTENIMIENTOS DEL CLIENTE
# ============================================================

@router.get("/{empresa_id}/mantenimientos")
def mantenimientos_cliente(
    empresa_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    validar_empresa(empresa_id, db, usuario)

    equipo_ids = obtener_ids_equipos_empresa(empresa_id, db)

    if not equipo_ids:
        return []

    mantenimientos = db.query(Mantenimiento).filter(
        Mantenimiento.equipo_id.in_(equipo_ids)
    ).all()

    return [serialize(m) for m in mantenimientos]


# ============================================================
# HOJA DE VIDA FULL PRO
# ============================================================

@router.get("/{empresa_id}/equipos/{equipo_id}/hoja-vida")
def hoja_vida_equipo_cliente(
    empresa_id: UUID,
    equipo_id: UUID,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """
    Retorna toda la información para construir la hoja de vida PRO:
    - Empresa
    - Sede
    - Equipo
    - Hoja de vida técnica
    - Mantenimientos del equipo
    - Evidencias/documentos
    """

    empresa = validar_empresa(empresa_id, db, usuario)

    equipo = db.query(Equipo).filter(
        Equipo.id == equipo_id,
        Equipo.empresa_id == empresa_id
    ).first()

    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    sede = db.query(Sede).filter(Sede.id == equipo.sede_id).first()

    hoja_vida = None
    if EquipoHojaVida:
        hoja_vida = db.query(EquipoHojaVida).filter(
            EquipoHojaVida.equipo_id == equipo_id
        ).first()

    mantenimientos = db.query(Mantenimiento).filter(
        Mantenimiento.equipo_id == equipo_id
    ).all()

    evidencias = []
    if Evidencia:
        evidencias = db.query(Evidencia).filter(
            Evidencia.equipo_id == equipo_id
        ).all()

    return {
        "empresa": serialize(empresa),
        "sede": serialize(sede),
        "equipo": serialize(equipo),
        "hoja_vida": serialize(hoja_vida) if hoja_vida else None,
        "mantenimientos": [serialize(m) for m in mantenimientos],
        "evidencias": [serializar_evidencia(e) for e in evidencias],
    }
