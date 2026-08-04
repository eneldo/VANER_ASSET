# ============================================================
# ROUTER: Exportaciones PRO
# Proyecto: SGAHolding - Fase 27
# Archivo: backend/app/routers/exportaciones.py
#
# Objetivo:
# - Exportar reportes del sistema en Excel y PDF.
# - Permitir filtros por empresa, sede, estado y rango de fechas.
# - Mantener consultas robustas usando SQL texto para evitar fallas
#   por diferencias temporales entre modelos y columnas reales de BD.
# ============================================================

from typing import Optional, List, Dict, Any, Tuple

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.excel_exporter import crear_excel
from app.utils.pdf_exporter import crear_pdf


router = APIRouter(prefix="/exportaciones", tags=["Exportaciones PRO"])


# ============================================================
# HELPERS GENERALES
# ============================================================

def _rows_to_dicts(result) -> List[Dict[str, Any]]:
    """Convierte resultados SQLAlchemy RowMapping a lista de diccionarios."""
    return [dict(row._mapping) for row in result]


def _descargar(path, media_type: str):
    """Retorna el archivo generado como descarga del navegador."""
    return FileResponse(
        path=str(path),
        media_type=media_type,
        filename=path.name,
    )


def _generar_archivo(formato: str, nombre: str, titulo: str, columnas: List[str], filas: List[Dict[str, Any]]):
    """
    Genera Excel o PDF según el formato solicitado.
    Formatos soportados: excel, pdf.
    """
    if formato == "excel":
        path = crear_excel(nombre, titulo, columnas, filas)
        return _descargar(
            path,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    path = crear_pdf(nombre, titulo, columnas, filas)
    return _descargar(path, "application/pdf")


def _filtros_base(
    empresa_id: Optional[str],
    sede_id: Optional[str],
    estado: Optional[str],
    fecha_inicio: Optional[str],
    fecha_fin: Optional[str],
) -> Tuple[str, Dict[str, Any]]:
    """
    Construye filtros reutilizables para reportes vinculados a equipos.

    Nota:
    Se usa ::text en uniones/filtros para tolerar UUID/int heredados durante
    la transición del proyecto sin romper la exportación.
    """
    condiciones = []
    params: Dict[str, Any] = {}

    if empresa_id:
        condiciones.append("e.empresa_id::text = :empresa_id")
        params["empresa_id"] = empresa_id

    if sede_id:
        condiciones.append("e.sede_id::text = :sede_id")
        params["sede_id"] = sede_id

    if estado:
        condiciones.append("UPPER(COALESCE(m.estado, e.estado, '')) = UPPER(:estado)")
        params["estado"] = estado

    if fecha_inicio:
        condiciones.append("COALESCE(m.fecha_programada::date, m.creado_en::date, CURRENT_DATE) >= :fecha_inicio")
        params["fecha_inicio"] = fecha_inicio

    if fecha_fin:
        condiciones.append("COALESCE(m.fecha_programada::date, m.creado_en::date, CURRENT_DATE) <= :fecha_fin")
        params["fecha_fin"] = fecha_fin

    where = " WHERE " + " AND ".join(condiciones) if condiciones else ""
    return where, params


# ============================================================
# CATÁLOGOS PARA FILTROS DEL FRONTEND
# ============================================================

@router.get("/catalogos")
def catalogos_exportacion(db: Session = Depends(get_db)):
    """
    Entrega catálogos básicos para los filtros del módulo Exportaciones.
    """
    empresas = _rows_to_dicts(db.execute(text("SELECT id::text, nombre FROM empresas ORDER BY nombre")))
    sedes = _rows_to_dicts(db.execute(text("SELECT id::text, empresa_id::text, nombre FROM sedes ORDER BY nombre")))

    estados_mantenimiento = _rows_to_dicts(
        db.execute(text("SELECT DISTINCT estado FROM mantenimientos WHERE estado IS NOT NULL ORDER BY estado"))
    )
    estados_equipo = _rows_to_dicts(
        db.execute(text("SELECT DISTINCT estado FROM equipos WHERE estado IS NOT NULL ORDER BY estado"))
    )

    return {
        "empresas": empresas,
        "sedes": sedes,
        "estados_mantenimiento": [x["estado"] for x in estados_mantenimiento],
        "estados_equipo": [x["estado"] for x in estados_equipo],
    }


# ============================================================
# REPORTE GENERAL DEL SISTEMA
# ============================================================

@router.get("/reporte-general/{formato}")
def exportar_reporte_general(
    formato: str,
    db: Session = Depends(get_db),
):
    """
    Exporta indicadores generales del sistema.
    Incluye empresas, sedes, equipos, mantenimientos, técnicos y auditoría.
    """
    sql = text(
        """
        SELECT 'Empresas registradas' AS indicador, COUNT(*)::text AS total FROM empresas
        UNION ALL SELECT 'Sedes registradas', COUNT(*)::text FROM sedes
        UNION ALL SELECT 'Equipos registrados', COUNT(*)::text FROM equipos
        UNION ALL SELECT 'Mantenimientos registrados', COUNT(*)::text FROM mantenimientos
        UNION ALL SELECT 'Técnicos registrados', COUNT(*)::text FROM tecnicos
        UNION ALL SELECT 'Eventos de auditoría', COUNT(*)::text FROM auditoria_sistema
        """
    )
    filas = _rows_to_dicts(db.execute(sql))
    columnas = ["indicador", "total"]
    return _generar_archivo(formato, "reporte_general_sga", "Reporte General SGAHolding", columnas, filas)


# ============================================================
# REPORTE DE EQUIPOS
# ============================================================

@router.get("/equipos/{formato}")
def exportar_equipos(
    formato: str,
    empresa_id: Optional[str] = Query(None),
    sede_id: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Exporta inventario de equipos filtrado por empresa, sede y estado.
    """
    condiciones = []
    params: Dict[str, Any] = {}

    if empresa_id:
        condiciones.append("eq.empresa_id::text = :empresa_id")
        params["empresa_id"] = empresa_id
    if sede_id:
        condiciones.append("eq.sede_id::text = :sede_id")
        params["sede_id"] = sede_id
    if estado:
        condiciones.append("UPPER(COALESCE(eq.estado, '')) = UPPER(:estado)")
        params["estado"] = estado

    where = " WHERE " + " AND ".join(condiciones) if condiciones else ""

    sql = text(
        f"""
        SELECT
            eq.codigo_id,
            eq.inventario,
            eq.nombre AS equipo,
            emp.nombre AS empresa,
            se.nombre AS sede,
            cat.nombre AS categoria,
            eq.marca,
            eq.modelo,
            eq.serie,
            eq.ubicacion,
            eq.estado,
            eq.criticidad,
            eq.created_at AS fecha_creacion
        FROM equipos eq
        LEFT JOIN empresas emp ON emp.id::text = eq.empresa_id::text
        LEFT JOIN sedes se ON se.id::text = eq.sede_id::text
        LEFT JOIN categorias cat ON cat.id::text = eq.categoria_id::text
        {where}
        ORDER BY emp.nombre, se.nombre, eq.nombre
        """
    )

    columnas = [
        "codigo_id", "inventario", "equipo", "empresa", "sede", "categoria",
        "marca", "modelo", "serie", "ubicacion", "estado", "criticidad", "fecha_creacion",
    ]
    filas = _rows_to_dicts(db.execute(sql, params))
    return _generar_archivo(formato, "reporte_equipos", "Reporte de Equipos SGAHolding", columnas, filas)


# ============================================================
# REPORTE DE MANTENIMIENTOS
# ============================================================

@router.get("/mantenimientos/{formato}")
def exportar_mantenimientos(
    formato: str,
    empresa_id: Optional[str] = Query(None),
    sede_id: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Exporta mantenimientos con filtros operativos.
    """
    where, params = _filtros_base(empresa_id, sede_id, estado, fecha_inicio, fecha_fin)

    sql = text(
        f"""
        SELECT
            m.id::text AS mantenimiento_id,
            emp.nombre AS empresa,
            se.nombre AS sede,
            e.nombre AS equipo,
            e.codigo_id,
            m.tipo,
            m.estado,
            m.fecha_programada,
            m.fecha_inicio,
            m.fecha_finalizacion,
            u.nombre_completo AS tecnico,
            m.descripcion,
            m.observaciones,
            m.costo,
            m.creado_en
        FROM mantenimientos m
        LEFT JOIN equipos e ON e.id::text = m.equipo_id::text
        LEFT JOIN empresas emp ON emp.id::text = e.empresa_id::text
        LEFT JOIN sedes se ON se.id::text = e.sede_id::text
        LEFT JOIN tecnicos t ON t.id::text = m.tecnico_id::text
        LEFT JOIN usuarios u ON u.id::text = t.usuario_id::text
        {where}
        ORDER BY COALESCE(m.fecha_programada, m.creado_en::date) DESC, m.id DESC
        """
    )

    columnas = [
        "mantenimiento_id", "empresa", "sede", "equipo", "codigo_id", "tipo", "estado",
        "fecha_programada", "fecha_inicio", "fecha_finalizacion", "tecnico",
        "descripcion", "observaciones", "costo", "creado_en",
    ]
    filas = _rows_to_dicts(db.execute(sql, params))
    return _generar_archivo(formato, "reporte_mantenimientos", "Reporte de Mantenimientos SGAHolding", columnas, filas)


# ============================================================
# REPORTE DE AUDITORÍA
# ============================================================

@router.get("/auditoria/{formato}")
def exportar_auditoria(
    formato: str,
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Exporta eventos de auditoría del sistema.
    """
    condiciones = []
    params: Dict[str, Any] = {}

    if fecha_inicio:
        condiciones.append("fecha::date >= :fecha_inicio")
        params["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        condiciones.append("fecha::date <= :fecha_fin")
        params["fecha_fin"] = fecha_fin

    where = " WHERE " + " AND ".join(condiciones) if condiciones else ""

    sql = text(
        f"""
        SELECT
            fecha,
            usuario_nombre,
            usuario_rol,
            modulo,
            accion,
            descripcion,
            entidad,
            entidad_id::text,
            ip_origen
        FROM auditoria_sistema
        {where}
        ORDER BY fecha DESC
        LIMIT 5000
        """
    )

    columnas = [
        "fecha", "usuario_nombre", "usuario_rol", "modulo", "accion",
        "descripcion", "entidad", "entidad_id", "ip_origen",
    ]
    filas = _rows_to_dicts(db.execute(sql, params))
    return _generar_archivo(formato, "reporte_auditoria", "Reporte de Auditoría SGAHolding", columnas, filas)
