# ============================================================
# ROUTER: Cronograma PRO de Mantenimientos
# Archivo: backend/app/routers/cronograma.py
# Fase 28 - SGAHolding
# ============================================================
# Objetivo:
#   Centralizar los endpoints del cronograma para ADMIN,
#   COORDINADOR y CLIENTE/EMPRESA.
#
# Características:
#   - Lista mantenimientos programados por rango de fechas.
#   - Permite filtrar por empresa, sede, técnico, estado y tipo.
#   - Devuelve información enriquecida para pintar calendario/timeline.
#   - No modifica tablas existentes; usa la tabla mantenimientos actual.
# ============================================================

from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import cast, String
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.mantenimiento import Mantenimiento
from app.models.equipo import Equipo
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario


router = APIRouter(prefix="/cronograma", tags=["Cronograma PRO"])


# ============================================================
# HELPERS DE FECHAS
# ============================================================

def hoy() -> date:
    """Retorna la fecha actual del servidor."""
    return date.today()


def parse_fecha(valor: Optional[str], default: date) -> date:
    """
    Convierte una fecha enviada como texto YYYY-MM-DD a date.
    Si viene vacía o inválida, usa un valor por defecto seguro.
    """
    if not valor:
        return default

    try:
        return datetime.fromisoformat(valor.replace("Z", "")).date()
    except Exception:
        return default


def calcular_rango(fecha_inicio: Optional[str], fecha_fin: Optional[str]):
    """
    Calcula el rango visible del cronograma.
    Por defecto muestra desde hoy hasta 30 días después.
    """
    inicio = parse_fecha(fecha_inicio, hoy())
    fin = parse_fecha(fecha_fin, inicio + timedelta(days=30))

    if fin < inicio:
        fin = inicio + timedelta(days=30)

    return inicio, fin


# ============================================================
# HELPERS DE RELACIONES
# ============================================================

def buscar_por_id_texto(db: Session, modelo, valor_id):
    """
    Busca un registro comparando IDs como texto.
    Esto hace el router tolerante a tablas con UUID o Integer.
    """
    if valor_id is None:
        return None

    return db.query(modelo).filter(cast(modelo.id, String) == str(valor_id)).first()


def obtener_tecnico_nombre(db: Session, tecnico_id):
    """
    Obtiene el nombre visible del técnico.
    Si el técnico está vinculado a un usuario, usa nombre_completo.
    """
    tecnico = buscar_por_id_texto(db, Tecnico, tecnico_id)
    if not tecnico:
        return None

    usuario_id = getattr(tecnico, "usuario_id", None)
    usuario = buscar_por_id_texto(db, Usuario, usuario_id) if usuario_id else None

    if usuario and getattr(usuario, "nombre_completo", None):
        return usuario.nombre_completo

    return (
        getattr(tecnico, "nombre", None)
        or getattr(tecnico, "especialidad", None)
        or f"Técnico {tecnico_id}"
    )


def cronograma_item(db: Session, mantenimiento: Mantenimiento):
    """
    Construye un objeto limpio para el frontend.
    Incluye datos de equipo, empresa, sede y técnico.
    """
    equipo = buscar_por_id_texto(db, Equipo, mantenimiento.equipo_id)
    empresa = buscar_por_id_texto(db, Empresa, getattr(equipo, "empresa_id", None)) if equipo else None
    sede = buscar_por_id_texto(db, Sede, getattr(equipo, "sede_id", None)) if equipo else None

    fecha = mantenimiento.fecha_programada
    estado = mantenimiento.estado or "PROGRAMADO"

    return {
        "id": str(mantenimiento.id),
        "title": f"{mantenimiento.tipo or 'Mantenimiento'} - {getattr(equipo, 'nombre', 'Equipo')}",
        "tipo": mantenimiento.tipo,
        "descripcion": mantenimiento.descripcion,
        "fecha_programada": fecha.isoformat() if fecha else None,
        "estado": estado,
        "equipo_id": str(mantenimiento.equipo_id) if mantenimiento.equipo_id else None,
        "equipo_nombre": getattr(equipo, "nombre", None) if equipo else None,
        "equipo_codigo": getattr(equipo, "codigo_id", None) if equipo else None,
        "equipo_serie": getattr(equipo, "serie", None) if equipo else None,
        "equipo_ubicacion": getattr(equipo, "ubicacion", None) if equipo else None,
        "empresa_id": str(getattr(equipo, "empresa_id", "")) if equipo else None,
        "empresa_nombre": getattr(empresa, "nombre", None) if empresa else None,
        "sede_id": str(getattr(equipo, "sede_id", "")) if equipo else None,
        "sede_nombre": getattr(sede, "nombre", None) if sede else None,
        "tecnico_id": str(mantenimiento.tecnico_id) if mantenimiento.tecnico_id else None,
        "tecnico_nombre": obtener_tecnico_nombre(db, mantenimiento.tecnico_id),
        "observaciones": mantenimiento.observaciones,
        "costo": float(mantenimiento.costo) if mantenimiento.costo is not None else None,
        "vencido": bool(fecha and fecha < hoy() and estado not in ["FINALIZADO", "ANULADO"]),
    }


def aplicar_filtros_base(
    query,
    empresa_id: Optional[str],
    sede_id: Optional[str],
    tecnico_id: Optional[str],
    estado: Optional[str],
    tipo: Optional[str],
):
    """
    Aplica filtros opcionales sin romper compatibilidad con UUID/int.
    """
    if estado:
        query = query.filter(Mantenimiento.estado == estado)

    if tipo:
        query = query.filter(Mantenimiento.tipo.ilike(f"%{tipo}%"))

    if tecnico_id:
        query = query.filter(cast(Mantenimiento.tecnico_id, String) == str(tecnico_id))

    # Empresa y sede pertenecen a Equipo, por eso se filtran con subconsulta.
    if empresa_id:
        equipos_empresa = query.session.query(Equipo.id).filter(cast(Equipo.empresa_id, String) == str(empresa_id))
        query = query.filter(cast(Mantenimiento.equipo_id, String).in_([str(e[0]) for e in equipos_empresa.all()]))

    if sede_id:
        equipos_sede = query.session.query(Equipo.id).filter(cast(Equipo.sede_id, String) == str(sede_id))
        query = query.filter(cast(Mantenimiento.equipo_id, String).in_([str(e[0]) for e in equipos_sede.all()]))

    return query


# ============================================================
# ENDPOINT ADMIN / COORDINADOR
# ============================================================

@router.get("/admin")
def cronograma_admin(
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicial YYYY-MM-DD"),
    fecha_fin: Optional[str] = Query(None, description="Fecha final YYYY-MM-DD"),
    empresa_id: Optional[str] = Query(None),
    sede_id: Optional[str] = Query(None),
    tecnico_id: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Cronograma general para administradores.
    Devuelve mantenimientos programados dentro del rango seleccionado.
    """
    inicio, fin = calcular_rango(fecha_inicio, fecha_fin)

    query = db.query(Mantenimiento).filter(
        Mantenimiento.fecha_programada.isnot(None),
        Mantenimiento.fecha_programada >= inicio,
        Mantenimiento.fecha_programada <= fin,
    )

    query = aplicar_filtros_base(query, empresa_id, sede_id, tecnico_id, estado, tipo)

    mantenimientos = query.order_by(Mantenimiento.fecha_programada.asc(), Mantenimiento.id.asc()).all()
    items = [cronograma_item(db, m) for m in mantenimientos]

    return {
        "fecha_inicio": inicio.isoformat(),
        "fecha_fin": fin.isoformat(),
        "total": len(items),
        "items": items,
    }


# ============================================================
# ENDPOINT CLIENTE / EMPRESA
# ============================================================

@router.get("/cliente/{empresa_id}")
def cronograma_cliente(
    empresa_id: str,
    fecha_inicio: Optional[str] = Query(None, description="Fecha inicial YYYY-MM-DD"),
    fecha_fin: Optional[str] = Query(None, description="Fecha final YYYY-MM-DD"),
    sede_id: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Cronograma filtrado por empresa.
    Importante: el frontend solo envía la empresa del usuario cliente.
    En producción se recomienda reforzar con JWT y validar empresa_id del token.
    """
    inicio, fin = calcular_rango(fecha_inicio, fecha_fin)

    query = db.query(Mantenimiento).filter(
        Mantenimiento.fecha_programada.isnot(None),
        Mantenimiento.fecha_programada >= inicio,
        Mantenimiento.fecha_programada <= fin,
    )

    query = aplicar_filtros_base(
        query=query,
        empresa_id=empresa_id,
        sede_id=sede_id,
        tecnico_id=None,
        estado=estado,
        tipo=tipo,
    )

    mantenimientos = query.order_by(Mantenimiento.fecha_programada.asc(), Mantenimiento.id.asc()).all()
    items = [cronograma_item(db, m) for m in mantenimientos]

    return {
        "empresa_id": empresa_id,
        "fecha_inicio": inicio.isoformat(),
        "fecha_fin": fin.isoformat(),
        "total": len(items),
        "items": items,
    }


# ============================================================
# ENDPOINT RESUMEN RÁPIDO
# ============================================================

@router.get("/resumen")
def resumen_cronograma(db: Session = Depends(get_db)):
    """
    Resumen ejecutivo para tarjetas del cronograma.
    """
    hoy_fecha = hoy()
    proximo_mes = hoy_fecha + timedelta(days=30)

    pendientes_30 = db.query(Mantenimiento).filter(
        Mantenimiento.fecha_programada.isnot(None),
        Mantenimiento.fecha_programada >= hoy_fecha,
        Mantenimiento.fecha_programada <= proximo_mes,
        Mantenimiento.estado.notin_(["FINALIZADO", "ANULADO"]),
    ).count()

    vencidos = db.query(Mantenimiento).filter(
        Mantenimiento.fecha_programada.isnot(None),
        Mantenimiento.fecha_programada < hoy_fecha,
        Mantenimiento.estado.notin_(["FINALIZADO", "ANULADO"]),
    ).count()

    finalizados = db.query(Mantenimiento).filter(
        Mantenimiento.fecha_programada.isnot(None),
        Mantenimiento.fecha_programada >= hoy_fecha,
        Mantenimiento.fecha_programada <= proximo_mes,
        Mantenimiento.estado == "FINALIZADO",
    ).count()

    return {
        "pendientes_30_dias": pendientes_30,
        "vencidos": vencidos,
        "finalizados_30_dias": finalizados,
    }
