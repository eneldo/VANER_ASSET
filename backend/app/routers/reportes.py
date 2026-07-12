# ============================================================
# ROUTER: Reportes PRO
# Archivo: backend/app/routers/reportes.py
# Función:
# - Consultar mantenimientos filtrados por empresa, sede, estado y fechas
# - Generar reporte en Excel
# - Generar reporte en PDF
# ============================================================

from io import BytesIO
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from app.database import get_db
from app.core.auth_dependencies import require_roles

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes PRO"],
    dependencies=[Depends(require_roles("ADMIN"))],
)


# ============================================================
# FUNCIÓN BASE: Consulta de mantenimientos con filtros
# ============================================================
def consultar_mantenimientos(
    db: Session,
    empresa_id: Optional[int] = None,
    sede_id: Optional[int] = None,
    estado: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
):
    query = """
        SELECT
            m.id,
            COALESCE(e.nombre, 'Sin empresa') AS empresa,
            COALESCE(s.nombre, 'Sin sede') AS sede,
            COALESCE(eq.nombre, 'Sin equipo') AS equipo,
            COALESCE(eq.codigo_inventario, '') AS codigo_inventario,
            COALESCE(t.nombre, 'Sin técnico') AS tecnico,
            COALESCE(m.tipo, '') AS tipo,
            COALESCE(m.estado, '') AS estado,
            m.fecha_programada,
            m.fecha_inicio,
            m.fecha_fin,
            COALESCE(m.costo::text, '0') AS costo,
            COALESCE(m.observaciones, '') AS observaciones
        FROM mantenimientos m
        LEFT JOIN equipos eq ON eq.id = m.equipo_id
        LEFT JOIN sedes s ON s.id = eq.sede_id
        LEFT JOIN empresas e ON e.id = eq.empresa_id
        LEFT JOIN tecnicos t ON t.id = m.tecnico_id
        WHERE 1 = 1
    """

    params = {}

    if empresa_id:
        query += " AND e.id = :empresa_id"
        params["empresa_id"] = empresa_id

    if sede_id:
        query += " AND s.id = :sede_id"
        params["sede_id"] = sede_id

    if estado:
        query += " AND m.estado = :estado"
        params["estado"] = estado

    if fecha_inicio:
        query += " AND m.fecha_programada >= :fecha_inicio"
        params["fecha_inicio"] = fecha_inicio

    if fecha_fin:
        query += " AND m.fecha_programada <= :fecha_fin"
        params["fecha_fin"] = fecha_fin

    query += " ORDER BY m.fecha_programada DESC NULLS LAST, m.id DESC"

    result = db.execute(text(query), params).mappings().all()
    return [dict(row) for row in result]


# ============================================================
# ENDPOINT: Listar datos para vista previa
# ============================================================
@router.get("/mantenimientos")
def reporte_mantenimientos(
    empresa_id: Optional[int] = Query(None),
    sede_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    data = consultar_mantenimientos(
        db=db,
        empresa_id=empresa_id,
        sede_id=sede_id,
        estado=estado,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )

    return {
        "total": len(data),
        "items": data,
    }


# ============================================================
# ENDPOINT: Exportar Excel
# ============================================================
@router.get("/mantenimientos/excel")
def exportar_mantenimientos_excel(
    empresa_id: Optional[int] = Query(None),
    sede_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    data = consultar_mantenimientos(
        db=db,
        empresa_id=empresa_id,
        sede_id=sede_id,
        estado=estado,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Mantenimientos"

    titulo = "REPORTE PRO DE MANTENIMIENTOS"
    ws.merge_cells("A1:L1")
    ws["A1"] = titulo
    ws["A1"].font = Font(size=16, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor="1E3A8A")
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:L2")
    ws["A2"] = f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ws["A2"].alignment = Alignment(horizontal="center")

    headers = [
        "ID",
        "Empresa",
        "Sede",
        "Equipo",
        "Código inventario",
        "Técnico",
        "Tipo",
        "Estado",
        "Fecha programada",
        "Fecha inicio",
        "Fecha fin",
        "Costo",
    ]

    ws.append([])
    ws.append(headers)

    header_row = 4
    fill_header = PatternFill("solid", fgColor="2563EB")
    font_header = Font(color="FFFFFF", bold=True)
    border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    for cell in ws[header_row]:
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center")
        cell.border = border

    for item in data:
        ws.append([
            item["id"],
            item["empresa"],
            item["sede"],
            item["equipo"],
            item["codigo_inventario"],
            item["tecnico"],
            item["tipo"],
            item["estado"],
            str(item["fecha_programada"] or ""),
            str(item["fecha_inicio"] or ""),
            str(item["fecha_fin"] or ""),
            item["costo"],
        ])

    for row in ws.iter_rows(min_row=5):
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(vertical="center")

    widths = [8, 25, 25, 25, 20, 25, 18, 18, 18, 18, 18, 14]
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[ws.cell(row=4, column=index).column_letter].width = width

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"reporte_mantenimientos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )


# ============================================================
# ENDPOINT: Exportar PDF
# ============================================================
@router.get("/mantenimientos/pdf")
def exportar_mantenimientos_pdf(
    empresa_id: Optional[int] = Query(None),
    sede_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    data = consultar_mantenimientos(
        db=db,
        empresa_id=empresa_id,
        sede_id=sede_id,
        estado=estado,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )

    output = BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("REPORTE PRO DE MANTENIMIENTOS", styles["Title"])
    subtitle = Paragraph(
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"],
    )

    elements.append(title)
    elements.append(subtitle)
    elements.append(Spacer(1, 12))

    table_data = [[
        "Empresa",
        "Sede",
        "Equipo",
        "Técnico",
        "Tipo",
        "Estado",
        "Programado",
        "Costo",
    ]]

    for item in data:
        table_data.append([
            item["empresa"],
            item["sede"],
            item["equipo"],
            item["tecnico"],
            item["tipo"],
            item["estado"],
            str(item["fecha_programada"] or ""),
            str(item["costo"] or "0"),
        ])

    table = Table(table_data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))

    elements.append(table)
    doc.build(elements)

    output.seek(0)

    filename = f"reporte_mantenimientos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )


# ============================================================
# ENDPOINTS AUXILIARES: Empresas y sedes para filtros
# ============================================================
@router.get("/filtros/empresas")
def obtener_empresas_filtro(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT id, nombre
            FROM empresas
            ORDER BY nombre ASC
        """)
    ).mappings().all()

    return [dict(row) for row in result]


@router.get("/filtros/sedes")
def obtener_sedes_filtro(
    empresa_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = """
        SELECT id, nombre, empresa_id
        FROM sedes
        WHERE 1 = 1
    """

    params = {}

    if empresa_id:
        query += " AND empresa_id = :empresa_id"
        params["empresa_id"] = empresa_id

    query += " ORDER BY nombre ASC"

    result = db.execute(text(query), params).mappings().all()
    return [dict(row) for row in result]
