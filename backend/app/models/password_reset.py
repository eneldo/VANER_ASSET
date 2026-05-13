# =========================================================
# MODELO PASSWORD RESET TOKEN - FASE 31.7
# Archivo: backend/app/models/password_reset.py
# =========================================================
# Guarda tokens temporales para recuperación de contraseña.
# Seguridad:
#   - No guarda el token real.
#   - Guarda token_hash SHA-256.
#   - Permite invalidar tokens usados.
# =========================================================

import uuid

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class PasswordResetToken(Base):
    """Token temporal de recuperación de contraseña."""

    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), nullable=False)
    email = Column(String(180), nullable=False, index=True)
    token_hash = Column(String(128), nullable=False, unique=True, index=True)

    usado = Column(Boolean, nullable=False, default=False)

    ip_solicitud = Column(String(80), nullable=True)
    user_agent = Column(Text, nullable=True)

    creado_en = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    expira_en = Column(DateTime(timezone=False), nullable=False)
    usado_en = Column(DateTime(timezone=False), nullable=True)
