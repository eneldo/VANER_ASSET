# ============================================================
# SCHEMAS: FormatoMantenimiento
# Archivo: backend/app/schemas/formato_mantenimiento_schema.py
# Descripción:
# Define las estructuras de entrada y salida para FastAPI.
# ============================================================

from datetime import date, datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel


class FormatoMantenimientoBase(BaseModel):
    mantenimiento_id: int
    tecnico_id: Optional[int] = None

    fecha: Optional[date] = None
    numero_ot: Optional[str] = None
    numero_inventario: Optional[str] = None
    ubicacion: Optional[str] = None

    mantenimiento_tipo: Optional[str] = "Preventivo"
    tecnico_nombre: Optional[str] = None
    tecnico_auxiliar: Optional[str] = None

    tipo_equipo: Optional[str] = None

    trabajos_realizados: Optional[Dict[str, Any]] = {}
    datos_funcionamiento: Optional[Dict[str, Any]] = {}
    repuestos_utilizados: Optional[List[Dict[str, Any]]] = []

    observaciones: Optional[str] = None

    firma_usuario: Optional[str] = None
    firma_operario: Optional[str] = None
    firma_coordinador: Optional[str] = None


class FormatoMantenimientoCreate(FormatoMantenimientoBase):
    pass


class FormatoMantenimientoUpdate(BaseModel):
    fecha: Optional[date] = None
    numero_ot: Optional[str] = None
    numero_inventario: Optional[str] = None
    ubicacion: Optional[str] = None

    mantenimiento_tipo: Optional[str] = None
    tecnico_nombre: Optional[str] = None
    tecnico_auxiliar: Optional[str] = None

    tipo_equipo: Optional[str] = None

    trabajos_realizados: Optional[Dict[str, Any]] = None
    datos_funcionamiento: Optional[Dict[str, Any]] = None
    repuestos_utilizados: Optional[List[Dict[str, Any]]] = None

    observaciones: Optional[str] = None

    firma_usuario: Optional[str] = None
    firma_operario: Optional[str] = None
    firma_coordinador: Optional[str] = None


class FormatoMantenimientoOut(FormatoMantenimientoBase):
    id: int
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True