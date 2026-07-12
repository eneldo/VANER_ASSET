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
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
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


def _imagen_firma(value):
    if not str(value or "").startswith("data:image/png;base64,"):
        return None


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
    try:
        contenido = base64.b64decode(value.split(",", 1)[1], validate=True)
        imagen = Image(BytesIO(contenido), width=190, height=72)
        imagen.hAlign = "CENTER"
        return imagen
    except Exception:
        return None


def _generar_pdf_ot(db, mantenimiento, destino):
    styles = getSampleStyleSheet()
    equipo = db.query(Equipo).filter(Equipo.id == mantenimiento.equipo_id).first()
    empresa = db.query(Empresa).filter(Empresa.id == mantenimiento.empresa_id).first()
    sede = db.query(Sede).filter(Sede.id == mantenimiento.sede_id).first()
    tecnico = db.query(Tecnico).filter(Tecnico.id == mantenimiento.tecnico_id).first() if mantenimiento.tecnico_id else None
    usuario_tecnico = db.query(Usuario).filter(Usuario.id == tecnico.usuario_id).first() if tecnico else None
    evidencias = db.query(Evidencia).filter(Evidencia.mantenimiento_id == mantenimiento.id).order_by(Evidencia.created_at).all()
    repuestos = db.query(OtRepuesto).filter(OtRepuesto.mantenimiento_id == mantenimiento.id).all()
    incidencias = db.query(OtIncidencia).filter(OtIncidencia.mantenimiento_id == mantenimiento.id).all()
    formato = db.query(FormatoMantenimiento).filter(FormatoMantenimiento.mantenimiento_id == mantenimiento.id).first()
    plantilla = _plantilla_activa(db, mantenimiento.empresa_id, "OT")

    doc = SimpleDocTemplate(str(destino), pagesize=letter, rightMargin=38, leftMargin=38, topMargin=34, bottomMargin=34)
    story = []
    if plantilla.incluir_logo and getattr(empresa, "logo_url", None):
        logo_path = Path(os.getenv("UPLOAD_DIR") or settings.UPLOAD_DIR).resolve() / "logos" / Path(empresa.logo_url).name
        if logo_path.exists():
            try:
                logo = Image(str(logo_path), width=110, height=55, kind="proportional"); logo.hAlign = "LEFT"; story.append(logo)
            except Exception:
                pass
    story += [Paragraph(html.escape(plantilla.titulo), styles["Title"]), Spacer(1, 8)]
    story.append(_tabla_info([
        ("Empresa", getattr(empresa, "nombre", None)), ("Sede", getattr(sede, "nombre", None)),
        ("Equipo", getattr(equipo, "nombre", None)), ("Código", getattr(equipo, "codigo_id", None)),
        ("Tipo", mantenimiento.tipo), ("Estado", mantenimiento.estado),
        ("Técnico", getattr(usuario_tecnico, "nombre_completo", None)),
        ("Fecha programada", mantenimiento.fecha_programada),
        ("Inicio", mantenimiento.fecha_inicio), ("Finalización", mantenimiento.fecha_finalizacion or mantenimiento.fecha_fin),
        *(([("Costo", mantenimiento.costo)] if plantilla.incluir_costos else [])),
    ], styles))
    story += [Spacer(1, 14), Paragraph("Ejecución técnica", styles["Heading2"])]
    story.append(_tabla_info([
        ("Estado inicial", mantenimiento.estado_inicial or mantenimiento.estado_inicial_equipo),
        ("Acciones realizadas", mantenimiento.acciones_realizadas),
        ("Resultado final", mantenimiento.resultado_final),
        ("Observaciones", mantenimiento.observaciones),
    ], styles))
    story += [Spacer(1, 14), Paragraph("Repuestos utilizados", styles["Heading2"])]
    if repuestos:
        rows = [["Descripción", "Referencia", "Cantidad", "Unidad"]] + [[
            item.descripcion, item.referencia or "", str(item.cantidad), item.unidad,
        ] for item in repuestos]
        tabla = Table(rows, repeatRows=1, colWidths=[260, 110, 70, 80])
        tabla.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .35, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(plantilla.color_primario)), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]))
        story.append(tabla)
    else:
        story.append(Paragraph("No se utilizaron repuestos.", styles["BodyText"]))
    story += [Spacer(1, 14), Paragraph("Incidencias", styles["Heading2"])]
    if incidencias:
        for item in incidencias:
            story.append(Paragraph(
                f"<b>{html.escape(item.tipo)} · {html.escape(item.severidad)}</b> — {html.escape(item.descripcion)} ({'Resuelta' if item.resuelta else 'Pendiente'})",
                styles["BodyText"],
            ))
    else:
        story.append(Paragraph("No se registraron incidencias.", styles["BodyText"]))
    firma_cliente = _imagen_firma(getattr(formato, "firma_usuario", None)) if formato else None
    firma_tecnico = _imagen_firma(getattr(formato, "firma_operario", None)) if formato else None
    if plantilla.incluir_firmas and (firma_cliente or firma_tecnico):
        story += [Spacer(1, 14), Paragraph("Firmas", styles["Heading2"])]
        tabla_firmas = Table([
            [firma_cliente or "Sin firma", firma_tecnico or "Sin firma"],
            ["Cliente / usuario", "Técnico / operario"],
        ], colWidths=[260, 260])
        tabla_firmas.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("BOX", (0, 0), (-1, -1), .35, colors.grey)]))
        story.append(tabla_firmas)
    if plantilla.incluir_evidencias:
        story += [Spacer(1, 14), Paragraph("Evidencias fotográficas", styles["Heading2"])]
        if not evidencias:
            story.append(Paragraph("No se registraron evidencias.", styles["BodyText"]))
        for evidencia in evidencias:
            story.append(Paragraph(f"<b>{html.escape(evidencia.tipo)}</b> — {html.escape(evidencia.descripcion or '')}", styles["BodyText"]))
            path = get_evidencia_path(evidencia.archivo_url)
            if path.exists() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                try:
                    image = Image(str(path), width=360, height=240, kind="proportional")
                    image.hAlign = "LEFT"
                    story += [image, Spacer(1, 10)]
                except Exception:
                    story.append(Paragraph("Imagen no disponible para incrustar.", styles["BodyText"]))
    if plantilla.pie_pagina:
        story += [Spacer(1, 16), Paragraph(html.escape(plantilla.pie_pagina), styles["Italic"])]
    doc.build(story)


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
