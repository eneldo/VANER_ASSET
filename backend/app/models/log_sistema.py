# ============================================================
# MODELO: LogSistema
# Archivo: backend/app/models/log_sistema.py
# FASE 34.2.5 - Logs Inteligentes SaaS PRO
# ============================================================

import uuid
from sqlalchemy import Column, String, Text, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class LogSistema(Base):
    """Registro centralizado de eventos y errores del sistema."""

    __tablename__ = "logs_sistema"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    modulo = Column(String(80), nullable=False, index=True, default="sistema")
    nivel = Column(String(20), nullable=False, index=True, default="INFO")
    evento = Column(String(160), nullable=False, default="evento")
    mensaje = Column(Text, nullable=True)
    usuario = Column(String(160), nullable=True)
    ip = Column(String(80), nullable=True)
    metodo = Column(String(20), nullable=True)
    ruta = Column(String(250), nullable=True)
    metadata_json = Column(JSON, nullable=True, default=dict)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)


Index("ix_logs_sistema_modulo_nivel", LogSistema.modulo, LogSistema.nivel)
Index("ix_logs_sistema_creado_nivel", LogSistema.creado_en, LogSistema.nivel)
