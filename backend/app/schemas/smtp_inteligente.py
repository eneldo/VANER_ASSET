# ============================================================
# SCHEMAS: SMTP Inteligente SaaS PRO
# Archivo: backend/app/schemas/smtp_inteligente.py
# FASE 34.2.3
# ============================================================

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from app.product import PRODUCT_NAME


class SMTPTestRequest(BaseModel):
    destinatario: EmailStr
    asunto: str = Field(default=f"Prueba SMTP {PRODUCT_NAME}", max_length=255)
    mensaje: str = Field(default=f"Correo de prueba enviado desde {PRODUCT_NAME}.")


class SMTPManualRequest(BaseModel):
    destinatario: EmailStr
    asunto: str = Field(max_length=255)
    mensaje: str
    plantilla: Optional[str] = "manual"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SMTPLogOut(BaseModel):
    id: UUID
    destinatario: str
    asunto: str
    plantilla: Optional[str]
    modulo_origen: str
    estado: str
    mensaje_error: Optional[str]
    enviado: bool
    intentos: int
    metadata_json: Dict[str, Any]
    creado_en: Optional[datetime]
    enviado_en: Optional[datetime]

    class Config:
        from_attributes = True


class SMTPStatusOut(BaseModel):
    activo: bool
    configurado: bool
    host: Optional[str] = None
    port: Optional[int] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    use_tls: bool = True
    use_ssl: bool = False
    automatizacion_activa: bool = False
    mensaje: str
