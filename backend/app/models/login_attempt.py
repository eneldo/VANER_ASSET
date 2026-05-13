# =========================================================
# FASE 31.3 - MODELO INTENTOS DE LOGIN
# Archivo: backend/app/models/login_attempt.py
# Tabla: login_intentos
# Objetivo:
#   Guardar intentos fallidos/exitosos de login y permitir bloqueo temporal.
# =========================================================

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class LoginAttempt(Base):
    __tablename__ = "login_intentos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(180), nullable=False, index=True)
    ip_origen = Column(String(80), nullable=True, index=True)
    exitoso = Column(Boolean, nullable=False, default=False)
    motivo = Column(String(180), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(80), nullable=True)
    intentos_fallidos = Column(Integer, nullable=False, default=0)
    bloqueado_hasta = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, server_default=func.now(), nullable=False)
