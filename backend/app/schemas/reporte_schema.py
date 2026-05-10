# ============================================================
# FASE 26 - SGA PRO
# Schemas Pydantic para Reportes y Auditoría
# Archivo: backend/app/schemas/reporte_schema.py
# ============================================================

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AuditoriaOut(BaseModel):
    """
    Respuesta pública para auditoría operativa.
    """

    id: UUID
    usuario_id: Optional[UUID] = None
    usuario_nombre: Optional[str] = None
    usuario_rol: Optional[str] = None

    modulo: str
    accion: str

    entidad: Optional[str] = None
    entidad_id: Optional[UUID] = None

    estado_anterior: Optional[str] = None
    estado_nuevo: Optional[str] = None

    descripcion: Optional[str] = None

    ip_origen: Optional[str] = None
    user_agent: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True


class ReporteResumenOut(BaseModel):
    """
    Resumen general para tarjetas del módulo Reportes PRO.
    """

    total_empresas: int
    total_sedes: int
    total_equipos: int
    total_mantenimientos: int

    mantenimientos_programados: int
    mantenimientos_en_proceso: int
    mantenimientos_finalizados: int
    mantenimientos_anulados: int

    equipos_operativos: int
    equipos_fuera_servicio: int
    equipos_criticos: int