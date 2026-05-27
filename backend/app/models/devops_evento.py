# ============================================================
# MODELO: DevOps Evento
# Archivo: backend/app/models/devops_evento.py
# FASE 34.2.6
# ============================================================

import uuid
from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class DevOpsEvento(Base):
    __tablename__ = "devops_eventos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    modulo = Column(String(80), nullable=False, default="devops")
    nivel = Column(String(20), nullable=False, default="INFO")
    evento = Column(String(120), nullable=False)
    mensaje = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
