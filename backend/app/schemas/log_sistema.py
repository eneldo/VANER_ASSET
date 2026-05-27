# ============================================================
# SCHEMAS: Logs Inteligentes
# Archivo: backend/app/schemas/log_sistema.py
# FASE 34.2.5
# ============================================================

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class LogSistemaBase(BaseModel):
    modulo: str = Field(default="sistema", max_length=80)
    nivel: str = Field(default="INFO", max_length=20)
    evento: str = Field(default="evento", max_length=160)
    mensaje: Optional[str] = None
    usuario: Optional[str] = None
    ip: Optional[str] = None
    metodo: Optional[str] = None
    ruta: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class LogSistemaCreate(LogSistemaBase):
    pass


class LogSistemaOut(LogSistemaBase):
    id: UUID
    creado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class LogSistemaResumen(BaseModel):
    total: int
    info: int
    warning: int
    error: int
    critical: int
    modulos: list[str]


class LogSistemaFiltro(BaseModel):
    modulo: Optional[str] = None
    nivel: Optional[str] = None
    texto: Optional[str] = None
    limite: int = 100
