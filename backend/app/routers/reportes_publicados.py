import html
import os
import uuid
import base64
from io import BytesIO
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.platypus import CondPageBreak, Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.equipo import Equipo
from app.models.empresa import Empresa
from app.models.evidencia import Evidencia
from app.models.mantenimiento import Mantenimiento
from app.models.reporte_publicado import ReportePublicado
from app.models.sede import Sede
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.models.ot_repuesto import OtRepuesto
from app.models.ot_incidencia import OtIncidencia
from app.models.formato_mantenimiento import FormatoMantenimiento
from app.models.plantilla_reporte import PlantillaReporte
from app.routers.auth import obtener_usuario_actual
from app.product import PRODUCT_NAME
from app.services.evidencia_service import get_evidencia_path


router = APIRouter(prefix="/reportes-publicados", tags=["Reportes publicados"])
REPORTES_DIR = (Path(os.getenv("EXPORT_DIR") or settings.EXPORT_DIR).resolve() / "reportes_privados")
REPORTES_DIR.mkdir(parents=True, exist_ok=True)


class ReporteOTCreate(BaseModel):
    mantenimiento_id: UUID


class ReporteMensualCreate(BaseModel):
    empresa_id: UUID | None = None
    periodo_inicio: date
    periodo_fin: date


def _rol(usuario):
    return str(getattr(usuario, "rol", "") or "").upper()


def _autorizar_empresa(usuario, empresa_id, escritura=False):
    rol = _rol(usuario)
    if rol == "ADMIN":
        return
    if rol == "COORDINADOR" and str(usuario.empresa_id) == str(empresa_id):
        return
    if not escritura and rol in {"EMPRESA", "CLIENTE"} and str(usuario.empresa_id) == str(empresa_id):
        return
    raise HTTPException(status_code=403, detail="Sin acceso a reportes de esta empresa")


def _serializar(reporte):
    return {
        "id": str(reporte.id),
        "empresa_id": str(reporte.empresa_id),
        "mantenimiento_id": str(reporte.mantenimiento_id) if reporte.mantenimiento_id else None,
        "tipo": reporte.tipo,
        "titulo": reporte.titulo,
        "estado": reporte.estado,
        "periodo_inicio": str(reporte.periodo_inicio) if reporte.periodo_inicio else None,
        "periodo_fin": str(reporte.periodo_fin) if reporte.periodo_fin else None,
        "created_at": reporte.created_at.isoformat() if reporte.created_at else None,
        "aprobado_at": reporte.aprobado_at.isoformat() if reporte.aprobado_at else None,
        "descarga_url": f"/reportes-publicados/{reporte.id}/archivo",
    }


def _tabla_info(datos, styles):
    rows = [[Paragraph(f"<b>{html.escape(str(k))}</b>", styles["BodyText"]), Paragraph(html.escape(str(v or "—")), styles["BodyText"])] for k, v in datos]
    table = Table(rows, colWidths=[150, 370])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def _imagen_firma(value, width=145, height=55):
    if not str(value or "").startswith("data:image/png;base64,"):
        return None
    try:
        contenido = base64.b64decode(value.split(",", 1)[1], validate=True)
        imagen = Image(BytesIO(contenido), width=width, height=height, kind="proportional")
        imagen.hAlign = "CENTER"
        return imagen
    except Exception:
        return None


def _texto_pdf(value, default="-"):
    texto = str(value or "").strip()
    return texto or default


def _fecha_pdf(value):
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %I:%M %p")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    return _texto_pdf(value)


def _parrafo_pdf(value, style):
    texto = html.escape(_texto_pdf(value)).replace("\n", "<br/>")
    return Paragraph(texto, style)


def _logo_empresa_path(empresa):
    logo_url = getattr(empresa, "logo_url", None)
    if not logo_url:
        return None
    path = Path(os.getenv("UPLOAD_DIR") or settings.UPLOAD_DIR).resolve() / "logos" / Path(logo_url).name
    return path if path.exists() else None


def _imagen_archivo(path, max_width, max_height):
    width, height = ImageReader(str(path)).getSize()
    escala = min(max_width / width, max_height / height)
    imagen = Image(str(path), width=width * escala, height=height * escala)
    imagen.hAlign = "CENTER"
    return imagen


def _titulo_seccion(numero, titulo, styles, color_primario):
    tabla = Table(
        [[
            Paragraph(str(numero), styles["SectionNumber"]),
            Paragraph(html.escape(titulo), styles["SectionTitle"]),
        ]],
        colWidths=[30, 494],
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(color_primario)),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#EAF0F8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCD7E6")),
    ]))
    return tabla


def _estilos_reporte(color_primario):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportHero",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        textColor=colors.HexColor(color_primario),
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#52657D"),
    ))
    styles.add(ParagraphStyle(
        name="CellLabel",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.6,
        leading=9.5,
        textColor=colors.HexColor("#32445C"),
    ))
    styles.add(ParagraphStyle(
        name="CellValue",
        parent=styles["BodyText"],
        fontSize=8.2,
        leading=10.5,
        textColor=colors.HexColor("#111827"),
    ))
    styles.add(ParagraphStyle(
        name="SectionNumber",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=colors.HexColor("#1F3655"),
    ))
    styles.add(ParagraphStyle(
        name="EvidenceTitle",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="EvidenceText",
        parent=styles["BodyText"],
        fontSize=7.8,
        leading=10,
        textColor=colors.HexColor("#26364B"),
    ))
    styles.add(ParagraphStyle(
        name="EvidenceMeta",
        parent=styles["BodyText"],
        fontSize=6.8,
        leading=8,
        textColor=colors.HexColor("#64748B"),
    ))
    styles.add(ParagraphStyle(
        name="SignatureName",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.8,
        leading=9.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#172033"),
    ))
    styles.add(ParagraphStyle(
        name="SignatureRole",
        parent=styles["BodyText"],
        fontSize=7,
        leading=8.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
    ))
    return styles


def _tabla_campos(datos, styles):
    rows = []
    for indice in range(0, len(datos), 2):
        izquierda = datos[indice]
        derecha = datos[indice + 1] if indice + 1 < len(datos) else ("", "")
        rows.append([
            _parrafo_pdf(izquierda[0], styles["CellLabel"]),
            _parrafo_pdf(izquierda[1], styles["CellValue"]),
            _parrafo_pdf(derecha[0], styles["CellLabel"]),
            _parrafo_pdf(derecha[1], styles["CellValue"]),
        ])
    table = Table(rows, colWidths=[82, 180, 82, 180])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDF3FA")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EDF3FA")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D4DEEA")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def _tabla_ejecucion(datos, styles):
    rows = [
        [_parrafo_pdf(etiqueta, styles["CellLabel"]), _parrafo_pdf(valor, styles["CellValue"])]
        for etiqueta, valor in datos
    ]
    table = Table(rows, colWidths=[125, 399])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDF3FA")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D4DEEA")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def _decorador_paginas(empresa, mantenimiento, plantilla, logo_path, generado_en):
    color_primario = colors.HexColor(plantilla.color_primario)
    empresa_nombre = _texto_pdf(getattr(empresa, "nombre", None), "Empresa cliente")
    pie = _texto_pdf(
        getattr(plantilla, "pie_pagina", None),
        f"{empresa_nombre} | Documento generado por {PRODUCT_NAME}",
    )
    numero_ot = str(mantenimiento.id)

    def decorar(canvas, doc):
        page_width, page_height = letter
        canvas.saveState()
        canvas.setTitle(f"Informe de mantenimiento OT {numero_ot}")
        canvas.setAuthor(PRODUCT_NAME)
        canvas.setFillColor(color_primario)
        canvas.rect(0, page_height - 13, page_width, 13, stroke=0, fill=1)

        logo_x = 38
        if logo_path:
            try:
                width, height = ImageReader(str(logo_path)).getSize()
                escala = min(72 / width, 40 / height)
                canvas.drawImage(
                    str(logo_path), logo_x, page_height - 65,
                    width=width * escala, height=height * escala,
                    preserveAspectRatio=True, mask="auto",
                )
            except Exception:
                logo_path_local = None
            else:
                logo_path_local = logo_path
        else:
            logo_path_local = None

        if not logo_path_local:
            canvas.setFillColor(color_primario)
            canvas.roundRect(logo_x, page_height - 65, 48, 38, 7, stroke=0, fill=1)
            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 12)
            canvas.drawCentredString(logo_x + 24, page_height - 51, "SGA")

        canvas.setFillColor(colors.HexColor("#172033"))
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(102, page_height - 37, empresa_nombre[:58])
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(102, page_height - 50, "GESTIÓN TÉCNICA DE ACTIVOS Y MANTENIMIENTO")

        canvas.setFillColor(color_primario)
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.drawRightString(page_width - 38, page_height - 36, f"OT {numero_ot[:18]}")
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.setFont("Helvetica", 7)
        canvas.drawRightString(page_width - 38, page_height - 49, f"Generado: {generado_en}")
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.6)
        canvas.line(38, page_height - 76, page_width - 38, page_height - 76)

        canvas.line(38, 42, page_width - 38, 42)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.setFont("Helvetica", 6.8)
        canvas.drawString(38, 28, pie[:105])
        canvas.drawRightString(page_width - 38, 28, f"Página {doc.page}")
        canvas.restoreState()

    return decorar


def _tarjeta_evidencia(evidencia, styles, color_primario):
    tipo = str(evidencia.tipo or "SOPORTE").upper()
    colores_tipo = {
        "ANTES": "#475569",
        "DURANTE": "#D97706",
        "DESPUES": "#15803D",
        "SOPORTE": color_primario,
    }
    contenido_imagen = Paragraph("Archivo adjunto no visualizable", styles["EvidenceText"])
    path = get_evidencia_path(evidencia.archivo_url)
    if path.exists() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
        try:
            contenido_imagen = _imagen_archivo(path, 148, 142)
        except Exception:
            contenido_imagen = Paragraph("Imagen no disponible para incrustar", styles["EvidenceText"])
    meta = " | ".join(filter(None, [
        _texto_pdf(getattr(evidencia, "nombre_original", None), Path(evidencia.archivo_url).name),
        _fecha_pdf(getattr(evidencia, "created_at", None)),
    ]))
    card = Table([
        [Paragraph(html.escape(tipo), styles["EvidenceTitle"])],
        [contenido_imagen],
        [_parrafo_pdf(evidencia.descripcion, styles["EvidenceText"])],
        [_parrafo_pdf(meta, styles["EvidenceMeta"])],
    ], colWidths=[164])
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor(colores_tipo.get(tipo, color_primario))),
        ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.55, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, 1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return card


ORDEN_TIPOS_EVIDENCIA = {
    "ANTES": 0,
    "DURANTE": 1,
    "DESPUES": 2,
    "SOPORTE": 3,
}


def _ordenar_evidencias(evidencias):
    def prioridad(evidencia):
        tipo = str(getattr(evidencia, "tipo", None) or "SOPORTE").strip().upper()
        return ORDEN_TIPOS_EVIDENCIA.get(tipo, len(ORDEN_TIPOS_EVIDENCIA))

    return sorted(evidencias, key=prioridad)


def _tabla_evidencias(evidencias, styles, color_primario):
    evidencias_ordenadas = _ordenar_evidencias(evidencias)
    cards = [_tarjeta_evidencia(item, styles, color_primario) for item in evidencias_ordenadas]
    rows = []
    for indice in range(0, len(cards), 3):
        rows.append([
            cards[indice],
            cards[indice + 1] if indice + 1 < len(cards) else "",
            cards[indice + 2] if indice + 2 < len(cards) else "",
        ])
    table = Table(rows, colWidths=[172, 172, 172], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return table


def _celda_firma(imagen, nombre, rol, styles):
    contenido = [imagen] if imagen else [Spacer(1, 52)]
    contenido.extend([
        Paragraph("________________________________", styles["SignatureRole"]),
        _parrafo_pdf(nombre, styles["SignatureName"]),
        _parrafo_pdf(rol, styles["SignatureRole"]),
    ])
    return contenido


def _tabla_firmas(firma_cliente, firma_gerente, nombres, styles):
    table = Table([[
        _celda_firma(firma_cliente, nombres[0], "Cliente / Usuario", styles),
        _celda_firma(firma_gerente, nombres[1], "Gerente / Coordinador SGA", styles),
    ]], colWidths=[261, 261])
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.45, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return table


def _plantilla_activa(db, empresa_id, tipo):
    item = db.query(PlantillaReporte).filter(
        or_(PlantillaReporte.empresa_id == empresa_id, PlantillaReporte.empresa_id.is_(None)),
        PlantillaReporte.tipo.in_([tipo, "AMBOS"]),
        PlantillaReporte.activo.is_(True),
    ).order_by(
        (PlantillaReporte.empresa_id == empresa_id).desc(),
        PlantillaReporte.updated_at.desc(),
    ).first()
    return item or SimpleNamespace(
        titulo="REPORTE DE ORDEN DE TRABAJO" if tipo == "OT" else "REPORTE MENSUAL",
        color_primario="#1E3A8A", pie_pagina=None, incluir_logo=True,
        incluir_evidencias=True, incluir_firmas=True, incluir_costos=False,
    )


def _generar_pdf_ot(db, mantenimiento, destino):
    equipo = db.query(Equipo).filter(Equipo.id == mantenimiento.equipo_id).first()
    empresa_id = mantenimiento.empresa_id or getattr(equipo, "empresa_id", None)
    sede_id = mantenimiento.sede_id or getattr(equipo, "sede_id", None)
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first() if empresa_id else None
    sede = db.query(Sede).filter(Sede.id == sede_id).first() if sede_id else None
    tecnico = db.query(Tecnico).filter(Tecnico.id == mantenimiento.tecnico_id).first() if mantenimiento.tecnico_id else None
    usuario_tecnico = db.query(Usuario).filter(Usuario.id == tecnico.usuario_id).first() if tecnico else None
    gerente = db.query(Usuario).filter(
        Usuario.empresa_id == empresa_id,
        Usuario.rol == "COORDINADOR",
        Usuario.activo.is_(True),
    ).order_by(Usuario.nombre_completo).first() if empresa_id else None
    evidencias = db.query(Evidencia).filter(
        Evidencia.mantenimiento_id == mantenimiento.id
    ).order_by(Evidencia.created_at).all()
    descripciones_evidencia = {}
    for evidencia in evidencias:
        tipo = str(evidencia.tipo or "SOPORTE").upper()
        if tipo not in descripciones_evidencia and str(evidencia.descripcion or "").strip():
            descripciones_evidencia[tipo] = evidencia.descripcion.strip()
    repuestos = db.query(OtRepuesto).filter(OtRepuesto.mantenimiento_id == mantenimiento.id).all()
    incidencias = db.query(OtIncidencia).filter(OtIncidencia.mantenimiento_id == mantenimiento.id).all()
    formato = db.query(FormatoMantenimiento).filter(
        FormatoMantenimiento.mantenimiento_id == mantenimiento.id
    ).first()
    plantilla = _plantilla_activa(db, empresa_id, "OT")
    color_primario = plantilla.color_primario or "#1E3A8A"
    styles = _estilos_reporte(color_primario)
    logo_path = _logo_empresa_path(empresa) if plantilla.incluir_logo else None
    generado_en = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    decorador = _decorador_paginas(
        empresa, mantenimiento, plantilla, logo_path, generado_en
    )
    doc = SimpleDocTemplate(
        str(destino),
        pagesize=letter,
        rightMargin=38,
        leftMargin=38,
        topMargin=88,
        bottomMargin=54,
        title=f"Informe de mantenimiento OT {mantenimiento.id}",
        author=PRODUCT_NAME,
    )

    estado = _texto_pdf(mantenimiento.estado, "SIN ESTADO").upper()
    estado_color = "#15803D" if estado == "FINALIZADO" else color_primario
    estado_badge = Table(
        [[Paragraph(html.escape(estado), styles["EvidenceTitle"])]],
        colWidths=[116],
    )
    estado_badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(estado_color)),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor(estado_color)),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    hero = Table([[
        [
            Paragraph("INFORME COMPLETO DE MANTENIMIENTO", styles["ReportHero"]),
            Paragraph(
                f"Orden de trabajo {_texto_pdf(mantenimiento.id)} | Documento técnico de cierre",
                styles["ReportSubtitle"],
            ),
        ],
        estado_badge,
    ]], colWidths=[400, 124])
    hero.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))

    inventario = getattr(equipo, "inventario", None) or getattr(formato, "numero_inventario", None)
    ubicacion = getattr(equipo, "ubicacion", None) or getattr(formato, "ubicacion", None)
    marca_modelo = " / ".join(filter(None, [
        getattr(equipo, "marca", None),
        getattr(equipo, "modelo", None),
    ]))
    tecnico_nombre = (
        getattr(usuario_tecnico, "nombre_completo", None)
        or getattr(formato, "tecnico_nombre", None)
    )
    story = [hero, Spacer(1, 13)]
    story += [
        _titulo_seccion(1, "Identificación del servicio", styles, color_primario),
        Spacer(1, 7),
    ]
    datos_generales = [
        ("Empresa", getattr(empresa, "nombre", None)),
        ("NIT", getattr(empresa, "nit", None)),
        ("Sede", getattr(sede, "nombre", None)),
        ("Ubicación", ubicacion),
        ("Equipo", getattr(equipo, "nombre", None)),
        ("Inventario", inventario),
        ("Código interno", getattr(equipo, "codigo_id", None)),
        ("Serie", getattr(equipo, "serie", None)),
        ("Marca / modelo", marca_modelo),
        ("Tipo", mantenimiento.tipo),
        ("Técnico", tecnico_nombre),
        ("Fecha programada", _fecha_pdf(mantenimiento.fecha_programada)),
        ("Fecha de inicio", _fecha_pdf(mantenimiento.fecha_inicio)),
        ("Fecha de finalización", _fecha_pdf(mantenimiento.fecha_finalizacion or mantenimiento.fecha_fin)),
    ]
    if plantilla.incluir_costos:
        datos_generales.append(("Costo", mantenimiento.costo))
    story += [_tabla_campos(datos_generales, styles), Spacer(1, 12)]

    story += [
        _titulo_seccion(2, "Ejecución técnica", styles, color_primario),
        Spacer(1, 7),
        _tabla_ejecucion([
            ("Estado inicial", mantenimiento.estado_inicial or mantenimiento.estado_inicial_equipo or descripciones_evidencia.get("ANTES")),
            ("Acciones realizadas", mantenimiento.acciones_realizadas or descripciones_evidencia.get("DURANTE")),
            ("Resultado final", mantenimiento.resultado_final or descripciones_evidencia.get("DESPUES")),
            ("Observaciones", mantenimiento.observaciones or getattr(formato, "observaciones", None)),
        ], styles),
        Spacer(1, 12),
    ]

    story += [
        _titulo_seccion(3, "Repuestos utilizados", styles, color_primario),
        Spacer(1, 7),
    ]
    if repuestos:
        rows = [["Descripción", "Referencia", "Cantidad", "Unidad"]] + [[
            _parrafo_pdf(item.descripcion, styles["CellValue"]),
            _parrafo_pdf(item.referencia, styles["CellValue"]),
            _parrafo_pdf(item.cantidad, styles["CellValue"]),
            _parrafo_pdf(item.unidad, styles["CellValue"]),
        ] for item in repuestos]
        tabla = Table(rows, repeatRows=1, colWidths=[260, 110, 70, 84])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(color_primario)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(tabla)
    else:
        story.append(Paragraph("No se utilizaron repuestos.", styles["CellValue"]))

    story += [
        Spacer(1, 12),
        _titulo_seccion(4, "Incidencias y novedades", styles, color_primario),
        Spacer(1, 7),
    ]
    if incidencias:
        rows = [["Tipo", "Severidad", "Descripción", "Estado"]] + [[
            _parrafo_pdf(item.tipo, styles["CellValue"]),
            _parrafo_pdf(item.severidad, styles["CellValue"]),
            _parrafo_pdf(item.descripcion, styles["CellValue"]),
            _parrafo_pdf("Resuelta" if item.resuelta else "Pendiente", styles["CellValue"]),
        ] for item in incidencias]
        tabla = Table(rows, repeatRows=1, colWidths=[75, 75, 290, 84])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(color_primario)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(tabla)
    else:
        story.append(Paragraph("No se registraron incidencias.", styles["CellValue"]))

    firma_cliente = _imagen_firma(getattr(formato, "firma_usuario", None)) if formato else None
    firma_gerente_valor = getattr(formato, "firma_coordinador", None) if formato else None
    firma_gerente = _imagen_firma(firma_gerente_valor)
    gerente_nombre = (
        firma_gerente_valor
        if firma_gerente_valor and not str(firma_gerente_valor).startswith("data:image/")
        else getattr(gerente, "nombre_completo", None)
    )
    if plantilla.incluir_evidencias:
        story += [
            Spacer(1, 14),
            CondPageBreak(275),
            _titulo_seccion(5, "Evidencias fotográficas", styles, color_primario),
            Spacer(1, 8),
        ]
        if not evidencias:
            story.append(Paragraph("No se registraron evidencias.", styles["CellValue"]))
        else:
            story.append(_tabla_evidencias(evidencias, styles, color_primario))

    if plantilla.incluir_firmas:
        story += [
            Spacer(1, 14),
            CondPageBreak(175),
            _titulo_seccion(6, "Aprobación y firmas", styles, color_primario),
            Spacer(1, 7),
            _tabla_firmas(
                firma_cliente,
                firma_gerente,
                [
                    getattr(empresa, "nombre", None),
                    gerente_nombre or "Gerente responsable",
                ],
                styles,
            ),
        ]

    doc.build(story, onFirstPage=decorador, onLaterPages=decorador)
def _generar_pdf_mensual(db, empresa_id, inicio, fin, destino):
    styles = getSampleStyleSheet()
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    equipos = db.query(Equipo).filter(Equipo.empresa_id == empresa_id).all()
    ids = [e.id for e in equipos]
    items = db.query(Mantenimiento).filter(
        Mantenimiento.equipo_id.in_(ids),
        Mantenimiento.fecha_programada >= inicio,
        Mantenimiento.fecha_programada <= fin,
    ).order_by(Mantenimiento.fecha_programada).all() if ids else []
    equipos_map = {e.id: e for e in equipos}
    plantilla = _plantilla_activa(db, empresa_id, "MENSUAL")
    doc = SimpleDocTemplate(str(destino), pagesize=landscape(letter), rightMargin=26, leftMargin=26, topMargin=28, bottomMargin=28)
    rows = [["Fecha", "Equipo", "Tipo", "Estado", "Acciones / resultado"]]
    for item in items:
        rows.append([
            str(item.fecha_programada or ""), getattr(equipos_map.get(item.equipo_id), "nombre", ""),
            item.tipo or "", item.estado or "", (item.resultado_final or item.acciones_realizadas or "")[:180],
        ])
    table = Table(rows, repeatRows=1, colWidths=[115, 150, 85, 90, 290])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(plantilla.color_primario)), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#cbd5e1")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    doc.build([
        Paragraph(f"{html.escape(plantilla.titulo)} — {html.escape(getattr(empresa, 'nombre', 'Empresa'))}", styles["Title"]),
        Paragraph(f"Periodo: {inicio} a {fin} · Total OTs: {len(items)}", styles["BodyText"]), Spacer(1, 12), table,
        *(([Spacer(1, 16), Paragraph(html.escape(plantilla.pie_pagina), styles["Italic"])] if plantilla.pie_pagina else [])),
    ])


@router.post("/ot", status_code=201)
def generar_reporte_ot(data: ReporteOTCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    if _rol(usuario) not in {"ADMIN", "COORDINADOR"}:
        raise HTTPException(status_code=403, detail="Solo coordinación puede generar reportes")
    mantenimiento = db.query(Mantenimiento).filter(Mantenimiento.id == data.mantenimiento_id).first()
    if not mantenimiento:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    _autorizar_empresa(usuario, mantenimiento.empresa_id, escritura=True)
    if str(mantenimiento.estado or "").upper() != "FINALIZADO":
        raise HTTPException(status_code=409, detail="La OT debe estar finalizada para generar su reporte")
    reporte_id = uuid.uuid4()
    filename = f"reporte_ot_{reporte_id}.pdf"
    _generar_pdf_ot(db, mantenimiento, REPORTES_DIR / filename)
    reporte = ReportePublicado(
        id=reporte_id, empresa_id=mantenimiento.empresa_id, mantenimiento_id=mantenimiento.id,
        creado_por_id=usuario.id, tipo="OT", titulo=f"Reporte OT — {mantenimiento.id}", storage_key=filename,
    )
    db.add(reporte); db.commit(); db.refresh(reporte)
    return _serializar(reporte)


@router.post("/mensual", status_code=201)
def generar_reporte_mensual(data: ReporteMensualCreate, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    if _rol(usuario) not in {"ADMIN", "COORDINADOR"}:
        raise HTTPException(status_code=403, detail="Solo coordinación puede generar reportes")
    empresa_id = data.empresa_id if _rol(usuario) == "ADMIN" else usuario.empresa_id
    if not empresa_id or data.periodo_fin < data.periodo_inicio:
        raise HTTPException(status_code=422, detail="Empresa o periodo inválido")
    _autorizar_empresa(usuario, empresa_id, escritura=True)
    reporte_id = uuid.uuid4(); filename = f"reporte_mensual_{reporte_id}.pdf"
    _generar_pdf_mensual(db, empresa_id, data.periodo_inicio, data.periodo_fin, REPORTES_DIR / filename)
    reporte = ReportePublicado(
        id=reporte_id, empresa_id=empresa_id, creado_por_id=usuario.id, tipo="MENSUAL",
        titulo=f"Reporte mensual {data.periodo_inicio} — {data.periodo_fin}", storage_key=filename,
        periodo_inicio=data.periodo_inicio, periodo_fin=data.periodo_fin,
    )
    db.add(reporte); db.commit(); db.refresh(reporte)
    return _serializar(reporte)


@router.get("/")
def listar_reportes(db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    query = db.query(ReportePublicado)
    rol = _rol(usuario)
    if rol == "ADMIN":
        pass
    elif rol in {"COORDINADOR", "EMPRESA", "CLIENTE"}:
        query = query.filter(ReportePublicado.empresa_id == usuario.empresa_id)
    else:
        raise HTTPException(status_code=403, detail="Sin acceso a reportes")
    if rol in {"EMPRESA", "CLIENTE"}:
        query = query.filter(ReportePublicado.estado.in_(["APROBADO", "PUBLICADO"]))
    return [_serializar(item) for item in query.order_by(ReportePublicado.created_at.desc()).all()]


@router.post("/{reporte_id}/aprobar")
def aprobar_reporte(reporte_id: UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    if _rol(usuario) not in {"ADMIN", "COORDINADOR"}:
        raise HTTPException(status_code=403, detail="Solo coordinación puede aprobar reportes")
    reporte = db.query(ReportePublicado).filter(ReportePublicado.id == reporte_id).first()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    _autorizar_empresa(usuario, reporte.empresa_id, escritura=True)
    reporte.estado = "APROBADO"; reporte.aprobado_por_id = usuario.id; reporte.aprobado_at = datetime.utcnow(); reporte.publicado_at = datetime.utcnow()
    db.commit(); db.refresh(reporte)
    return _serializar(reporte)


@router.get("/{reporte_id}/archivo")
def descargar_reporte(reporte_id: UUID, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    reporte = db.query(ReportePublicado).filter(ReportePublicado.id == reporte_id).first()
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    _autorizar_empresa(usuario, reporte.empresa_id, escritura=False)
    if _rol(usuario) in {"EMPRESA", "CLIENTE"} and reporte.estado not in {"APROBADO", "PUBLICADO"}:
        raise HTTPException(status_code=403, detail="El reporte todavía no ha sido aprobado")
    path = REPORTES_DIR / Path(reporte.storage_key).name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Archivo de reporte no disponible")
    return FileResponse(str(path), media_type="application/pdf", filename=f"{reporte.titulo}.pdf", headers={"Cache-Control": "private, no-store"})
