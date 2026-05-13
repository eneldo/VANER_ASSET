# =========================================================
# FASE 31.3 - MODELO EVENTOS DE SEGURIDAD
# Archivo: backend/app/models/security_event.py
# Tabla: seguridad_eventos
# Objetivo:
#   Registrar eventos relevantes de seguridad: login, logout,
#   bloqueo, acceso denegado, errores de rate limit, etc.
# =========================================================

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base


class SecurityEvent(Base):
    __tablename__ = "seguridad_eventos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    usuario_id = Column(UUID(as_uuid=True), nullable=True)
    usuario_email = Column(String(180), nullable=True)
    rol = Column(String(60), nullable=True)
    empresa_id = Column(UUID(as_uuid=True), nullable=True)

    evento = Column(String(120), nullable=False)
    modulo = Column(String(120), nullable=True)
    metodo = Column(String(12), nullable=True)
    ruta = Column(String(300), nullable=True)

    ip_origen = Column(String(80), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(80), nullable=True)

    permitido = Column(Boolean, nullable=False, default=True)
    detalle = Column(Text, nullable=True)
    extra = Column(JSONB, nullable=True)

    creado_en = Column(DateTime, server_default=func.now(), nullable=False)
