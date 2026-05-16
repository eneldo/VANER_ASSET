# ============================================================
# SCHEMAS: FORMATOS Y BITÁCORAS DINÁMICAS PRO
# Archivo: backend/app/schemas/formato_dinamico_schema.py
# ============================================================

from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


class CampoFormatoBase(BaseModel):
    seccion: str = "General"
    nombre_campo: str
    tipo_campo: str = "checkbox"
    opciones: Optional[str] = None
    obligatorio: bool = False
    orden: int = 1
    activo: bool = True


class CampoFormatoCreate(CampoFormatoBase):
    formato_id: UUID


class CampoFormatoOut(CampoFormatoBase):
    id: UUID
    formato_id: UUID

    class Config:
        from_attributes = True


class TipoFormatoCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True


class TipoFormatoOut(BaseModel):
    id: UUID
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True
    campos: List[CampoFormatoOut] = []

    class Config:
        from_attributes = True


class BitacoraRespuestaIn(BaseModel):
    campo_id: UUID
    valor: Optional[str] = None
    observacion: Optional[str] = None


class BitacoraGuardarIn(BaseModel):
    mantenimiento_id: UUID
    tecnico_id: Optional[UUID] = None
    formato_id: Optional[UUID] = None
    estado_inicial: Optional[str] = None
    estado_final: Optional[str] = None
    observaciones: Optional[str] = None
    recomendaciones: Optional[str] = None
    repuestos_utilizados: Optional[str] = None
    respuestas: List[BitacoraRespuestaIn] = []


class BitacoraRespuestaOut(BaseModel):
    id: UUID
    campo_id: Optional[UUID] = None
    valor: Optional[str] = None
    observacion: Optional[str] = None

    class Config:
        from_attributes = True


class BitacoraOut(BaseModel):
    id: UUID
    mantenimiento_id: UUID
    tecnico_id: Optional[UUID] = None
    formato_id: Optional[UUID] = None
    estado_inicial: Optional[str] = None
    estado_final: Optional[str] = None
    observaciones: Optional[str] = None
    recomendaciones: Optional[str] = None
    repuestos_utilizados: Optional[str] = None
    respuestas: List[BitacoraRespuestaOut] = []

    class Config:
        from_attributes = True


class BitacoraContextoOut(BaseModel):
    mantenimiento: Dict[str, Any]
    equipo: Dict[str, Any]
    formato: TipoFormatoOut
    bitacora: Optional[BitacoraOut] = None
