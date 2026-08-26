# =========================================================
# MODELO PASSWORD HISTORY
# Archivo: backend/app/models/password_history.py
#
# Almacena hashes de contraseñas anteriores para impedir
# reutilización. Aislamiento multiempresa por usuario_id.
# =========================================================

import uuid

from sqlalchemy import Column, DateTime, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class PasswordHistory(Base):
    """Historial de hashes de contraseñas por usuario."""

    __tablename__ = "password_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    empresa_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    password_hash = Column(String, nullable=False)
    motivo = Column(String(60), nullable=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_password_history_usuario_fecha", "usuario_id", "created_at"),
    )
