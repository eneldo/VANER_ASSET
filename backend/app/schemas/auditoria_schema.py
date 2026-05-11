# ============================================================
# FASE 30 - SCHEMAS PYDANTIC: AUDITORÍA PRO
# Archivo: backend/app/schemas/auditoria_schema.py
# Objetivo:
#   Definir los modelos de entrada/salida para los endpoints
#   de auditoría avanzada.
# ============================================================

from datetime import datetime
from typing import Any, Dict, Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class AuditoriaEventoCreate(BaseModel):
    """Payload para registrar manualmente un evento de auditoría."""

    usuario_id: Optional[UUID] = None
    usuario_nombre: Optional[str] = None
    usuario_rol: Optional[str] = None
    empresa_id: Optional[UUID] = None
    modulo: str = Field(..., min_length=2, max_length=80)
    accion: str = Field(..., min_length=2, max_length=80)
    entidad: Optional[str] = None
    entidad_id: Optional[str] = None
    descripcion: Optional[str] = None
    ip_origen: Optional[str] = None
    user_agent: Optional[str] = None
    nivel: str = "INFO"
    metadata: Optional[Dict[str, Any]] = None


class AuditoriaEventoOut(BaseModel):
    """Respuesta completa de un evento de auditoría."""

    id: UUID
    usuario_id: Optional[UUID] = None
    usuario_nombre: Optional[str] = None
    usuario_rol: Optional[str] = None
    empresa_id: Optional[UUID] = None
    modulo: str
    accion: str
    entidad: Optional[str] = None
    entidad_id: Optional[str] = None
    descripcion: Optional[str] = None
    ip_origen: Optional[str] = None
    user_agent: Optional[str] = None
    nivel: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditoriaResumenOut(BaseModel):
    """Métricas rápidas para el dashboard de auditoría."""

    total_eventos: int
    eventos_hoy: int
    eventos_warning: int
    eventos_error: int
    eventos_security: int
    modulos: List[dict]
    acciones: List[dict]
