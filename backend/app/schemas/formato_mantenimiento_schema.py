# ============================================================
# SCHEMA: Formato de Mantenimiento
# Archivo: backend/app/schemas/formato_mantenimiento_schema.py
# Función:
# - Permitir mantenimiento_id tipo UUID/string.
# - Guardar bitácoras dinámicas para diferentes equipos.
# ============================================================

from typing import Optional, Any
from datetime import date
from pydantic import BaseModel, ConfigDict
from pydantic import field_validator
import base64
import binascii


def validar_firma_png(value):
    if value in (None, ""):
        return None
    if not isinstance(value, str) or not value.startswith("data:image/png;base64,") or len(value) > 1_500_000:
        raise ValueError("La firma debe ser una imagen PNG válida y menor a 1 MB")
    try:
        contenido = base64.b64decode(value.split(",", 1)[1], validate=True)
    except (ValueError, binascii.Error):
        raise ValueError("La firma contiene datos base64 inválidos")
    if len(contenido) < 100 or not contenido.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("La firma no contiene un archivo PNG válido")
    return value


class FormatoMantenimientoBase(BaseModel):
    mantenimiento_id: str
    tecnico_id: Optional[str] = None

    fecha: Optional[date] = None
    numero_ot: Optional[str] = None
    numero_inventario: Optional[str] = None
    ubicacion: Optional[str] = None
    mantenimiento_tipo: Optional[str] = "Preventivo"

    tecnico_nombre: Optional[str] = None
    tecnico_auxiliar: Optional[str] = None
    tipo_equipo: Optional[str] = None

    trabajos_realizados: Optional[dict[str, Any]] = None
    datos_funcionamiento: Optional[dict[str, Any]] = None
    repuestos_utilizados: Optional[list[dict[str, Any]]] = None

    observaciones: Optional[str] = None
    firma_usuario: Optional[str] = None
    firma_operario: Optional[str] = None
    firma_coordinador: Optional[str] = None

    @field_validator("firma_usuario", "firma_operario")
    @classmethod
    def validar_firmas(cls, value):
        return validar_firma_png(value)


class FormatoMantenimientoCreate(FormatoMantenimientoBase):
    pass


class FormatoMantenimientoUpdate(BaseModel):
    tecnico_id: Optional[str] = None

    fecha: Optional[date] = None
    numero_ot: Optional[str] = None
    numero_inventario: Optional[str] = None
    ubicacion: Optional[str] = None
    mantenimiento_tipo: Optional[str] = None

    tecnico_nombre: Optional[str] = None
    tecnico_auxiliar: Optional[str] = None
    tipo_equipo: Optional[str] = None

    trabajos_realizados: Optional[dict[str, Any]] = None
    datos_funcionamiento: Optional[dict[str, Any]] = None
    repuestos_utilizados: Optional[list[dict[str, Any]]] = None

    observaciones: Optional[str] = None
    firma_usuario: Optional[str] = None
    firma_operario: Optional[str] = None
    firma_coordinador: Optional[str] = None

    @field_validator("firma_usuario", "firma_operario")
    @classmethod
    def validar_firmas(cls, value):
        return validar_firma_png(value)


class FormatoMantenimientoOut(FormatoMantenimientoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
