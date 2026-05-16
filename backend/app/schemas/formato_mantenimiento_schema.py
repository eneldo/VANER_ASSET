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


class FormatoMantenimientoOut(FormatoMantenimientoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)