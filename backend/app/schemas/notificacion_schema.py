# ============================================================
# SCHEMAS: Notificación
# Archivo: backend/app/schemas/notificacion_schema.py
# Fase 29 - Notificaciones y Alertas PRO
# ============================================================

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NotificacionBase(BaseModel):
    """Campos comunes para crear y mostrar notificaciones."""

    rol_destino: str
    usuario_id: Optional[int] = None
    empresa_id: Optional[int] = None
    sede_id: Optional[int] = None
    equipo_id: Optional[int] = None
    mantenimiento_id: Optional[int] = None
    tecnico_id: Optional[int] = None

    tipo: str = "INFO"
    prioridad: str = "MEDIA"
    titulo: str
    mensaje: Optional[str] = None
    enlace: Optional[str] = None


class NotificacionCreate(NotificacionBase):
    """Payload para crear notificación manual o desde otros módulos."""
    pass


class NotificacionOut(NotificacionBase):
    """Respuesta enviada al frontend."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    leida: bool
    creado_en: datetime
    leido_en: Optional[datetime] = None


class NotificacionResumen(BaseModel):
    """KPIs rápidos para campana o dashboard."""

    total: int
    no_leidas: int
    alta: int
    media: int
    baja: int
