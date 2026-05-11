# ============================================================
# UTILIDAD: Exportador PDF PRO sin dependencias externas
# Proyecto: SGA PRO - Fase 27 Exportación PRO
# Archivo: backend/app/utils/pdf_exporter.py
#
# Función:
# - Generar PDF básico en formato texto usando únicamente Python.
# - Evita instalar ReportLab/fpdf y reduce fallas de dependencias.
# - Ideal para reportes ejecutivos, auditoría y listados filtrados.
# ============================================================

from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Dict, Any
import textwrap


BASE_DIR = Path(__file__).resolve().parents[1]
EXPORT_DIR = BASE_DIR / "exports" / "pdf"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _escape_pdf(text: str) -> str:
    """Escapa caracteres especiales del estándar PDF."""
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _value(value: Any) -> str:
    """Convierte valores de BD a texto seguro para el PDF."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _lineas_desde_datos(titulo: str, columnas: List[str], filas: Iterable[Dict[str, Any]]) -> List[str]:
    """Construye líneas de texto legibles para insertar en el PDF."""
    lineas = [
        titulo.upper(),
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "-" * 100,
    ]

    filas_lista = list(filas)
    if not filas_lista:
        lineas.append("No se encontraron registros para los filtros seleccionados.")
        return lineas

    for index, fila in enumerate(filas_lista, start=1):
        lineas.append(f"REGISTRO {index}")
        for columna in columnas:
            etiqueta = columna.replace("_", " ").upper()
            contenido = _value(fila.get(columna))
            texto = f"{etiqueta}: {contenido}"
            lineas.extend(textwrap.wrap(texto, width=105) or [texto])
        lineas.append("-" * 100)

    return lineas


def crear_pdf(nombre_base: str, titulo: str, columnas: List[str], filas: Iterable[Dict[str, Any]]) -> Path:
    """
    Crea un PDF básico multipágina.

    Nota técnica:
    Este generador escribe sintaxis PDF directa. No tiene tablas gráficas,
    pero genera un archivo .pdf real y portable sin librerías adicionales.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = EXPORT_DIR / f"{nombre_base}_{timestamp}.pdf"

    lineas = _lineas_desde_datos(titulo, columnas, filas)
    lineas_por_pagina = 42
    paginas = [lineas[i:i + lineas_por_pagina] for i in range(0, len(lineas), lineas_por_pagina)] or [[]]

    objetos = []

    # Objeto 1: catálogo.
    objetos.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # Objeto 2: páginas. Se completa cuando sabemos cuántas hay.
    kids = " ".join(f"{3 + i * 2} 0 R" for i in range(len(paginas)))
    objetos.append(f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {len(paginas)} >>\nendobj\n")

    for i, pagina in enumerate(paginas):
        page_obj = 3 + i * 2
        content_obj = 4 + i * 2

        # Contenido de texto de cada página.
        y = 800
        stream_lines = ["BT", "/F1 9 Tf"]
        for linea in pagina:
            stream_lines.append(f"50 {y} Td ({_escape_pdf(linea)}) Tj")
            stream_lines.append(f"-50 -16 Td")
            y -= 16
        stream_lines.append("ET")
        stream = "\n".join(stream_lines)

        objetos.append(
            f"{page_obj} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] "
            f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
            f"/Contents {content_obj} 0 R >>\nendobj\n"
        )
        objetos.append(
            f"{content_obj} 0 obj\n"
            f"<< /Length {len(stream.encode('latin-1', errors='ignore'))} >>\n"
            f"stream\n{stream}\nendstream\nendobj\n"
        )

    # Escritura con tabla xref.
    contenido = "%PDF-1.4\n"
    offsets = [0]
    for obj in objetos:
        offsets.append(len(contenido.encode("latin-1", errors="ignore")))
        contenido += obj

    xref_pos = len(contenido.encode("latin-1", errors="ignore"))
    contenido += f"xref\n0 {len(objetos) + 1}\n"
    contenido += "0000000000 65535 f \n"
    for offset in offsets[1:]:
        contenido += f"{offset:010d} 00000 n \n"
    contenido += f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF"

    archivo.write_bytes(contenido.encode("latin-1", errors="ignore"))
    return archivo
