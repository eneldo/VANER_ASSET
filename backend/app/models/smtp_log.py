# ============================================================
# MODELO: SMTP Inteligente SaaS PRO
# Archivo: backend/app/models/smtp_log.py
# FASE 34.2.3
# ============================================================

import uuid
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.database import Base


class SMTPLog(Base):
    """
    Historial de correos enviados/probados desde el motor SMTP inteligente.
    No reemplaza el módulo de notificaciones actual; solo registra eventos SMTP.
    """

    __tablename__ = "smtp_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    destinatario = Column(String(255), nullable=False, index=True)
    asunto = Column(String(255), nullable=False)
    plantilla = Column(String(100), nullable=True, index=True)
    modulo_origen = Column(String(80), nullable=False, default="smtp_inteligente", index=True)
    estado = Column(String(30), nullable=False, default="PENDIENTE", index=True)
    mensaje_error = Column(Text, nullable=True)
    enviado = Column(Boolean, nullable=False, default=False)
    intentos = Column(Integer, nullable=False, default=0)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    enviado_en = Column(DateTime(timezone=True), nullable=True)
