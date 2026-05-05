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
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.equipo import Equipo
from app.models.mantenimiento import Mantenimiento

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


def validar_empresa(empresa_id: UUID, db: Session):
    """
    Valida que la empresa exista.
    """
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


# ============================================================
# DASHBOARD CLIENTE
# ============================================================

@router.get("/{empresa_id}/dashboard")
def dashboard_cliente(empresa_id: UUID, db: Session = Depends(get_db)):
    empresa = validar_empresa(empresa_id, db)
    equipo_ids = obtener_ids_equipos_empresa(empresa_id, db)

    total_sedes = db.query(Sede).filter(Sede.empresa_id == empresa_id).count()
    total_equipos = db.query(Equipo).filter(Equipo.empresa_id == empresa_id).count()

    pendientes = 0
    realizados = 0

    if equipo_ids:
        pendientes = db.query(Mantenimiento).filter(
            Mantenimiento.equipo_id.in_(equipo_ids),
            Mantenimiento.estado.notin_(["FINALIZADO", "ANULADO"])
        ).count()

        realizados = db.query(Mantenimiento).filter(
            Mantenimiento.equipo_id.in_(equipo_ids),
            Mantenimiento.estado == "FINALIZADO"
        ).count()

    return {
        "empresa": serialize(empresa),
        "empresa_id": str(empresa_id),
        "total_sedes": total_sedes,
        "total_equipos": total_equipos,
        "mantenimientos_pendientes": pendientes,
        "mantenimientos_realizados": realizados,
    }


# ============================================================
# SEDES DEL CLIENTE
# ============================================================

@router.get("/{empresa_id}/sedes")
def sedes_cliente(empresa_id: UUID, db: Session = Depends(get_db)):
    validar_empresa(empresa_id, db)

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
    db: Session = Depends(get_db)
):
    validar_empresa(empresa_id, db)

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
def equipos_cliente(empresa_id: UUID, db: Session = Depends(get_db)):
    validar_empresa(empresa_id, db)

    equipos = db.query(Equipo).filter(
        Equipo.empresa_id == empresa_id
    ).order_by(Equipo.nombre.asc()).all()

    return [serialize(e) for e in equipos]


# ============================================================
# MANTENIMIENTOS DEL CLIENTE
# ============================================================

@router.get("/{empresa_id}/mantenimientos")
def mantenimientos_cliente(empresa_id: UUID, db: Session = Depends(get_db)):
    validar_empresa(empresa_id, db)

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
    db: Session = Depends(get_db)
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

    empresa = validar_empresa(empresa_id, db)

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
        "evidencias": [serialize(e) for e in evidencias],
    }