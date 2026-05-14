# ============================================================
# SCHEMAS AUDITORÍA / AUDITORÍA PRO
# Archivo: backend/app/schemas/auditoria_schema.py
#
# Compatible con:
# - app/routers/auditoria.py
# - app/routers/auditoria_pro.py
# - FastAPI Pydantic v2
# ============================================================

from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ============================================================
# BASE
# ============================================================

class AuditoriaEventoBase(BaseModel):
    usuario_id: Optional[UUID] = None
    usuario_email: Optional[str] = None
    usuario_nombre: Optional[str] = None
    rol: Optional[str] = None
    empresa_id: Optional[UUID] = None

    modulo: Optional[str] = None
    accion: Optional[str] = None

    recurso_tipo: Optional[str] = None
    recurso_id: Optional[str] = None

    metodo: Optional[str] = None
    ruta: Optional[str] = None

    status_code: Optional[int] = None

    ip_origen: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None

    permitido: Optional[bool] = True
    severidad: Optional[str] = "INFO"

    detalle: Optional[str] = None
    datos_extra: Optional[Any] = None


# ============================================================
# CREATE
# ============================================================

class AuditoriaEventoCreate(AuditoriaEventoBase):
    pass


# ============================================================
# UPDATE
# ============================================================

class AuditoriaEventoUpdate(BaseModel):
    detalle: Optional[str] = None
    severidad: Optional[str] = None
    permitido: Optional[bool] = None
    datos_extra: Optional[Any] = None


# ============================================================
# RESPONSE / OUT
# ============================================================

class AuditoriaEventoOut(AuditoriaEventoBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    creado_en: Optional[datetime] = None


# ============================================================
# RESPUESTA PAGINADA
# ============================================================

class AuditoriaEventosResponse(BaseModel):
    total: int
    limit: int
    offset: int
    eventos: list[AuditoriaEventoOut]


# ============================================================
# RESUMEN
# ============================================================

class AuditoriaResumenResponse(BaseModel):
    total_eventos: int
    permitidos: int
    denegados: int
    errores: int


# ============================================================
# ALIAS DE COMPATIBILIDAD
# Compatibles con routers antiguos
# ============================================================

AuditoriaEventoResponse = AuditoriaEventoOut
AuditoriaResumenOut = AuditoriaResumenResponse