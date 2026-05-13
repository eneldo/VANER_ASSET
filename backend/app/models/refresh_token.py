# =========================================================
# MODELO REFRESH TOKEN - FASE 31.1 JWT PRO
# Tabla: refresh_tokens
#
# Objetivo:
#   Guardar de forma segura las sesiones largas del usuario.
#   IMPORTANTE: No se almacena el refresh token en texto plano,
#   solo su hash SHA-256 para evitar robo de sesión desde la BD.
# =========================================================

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    # Identificador interno del registro
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Usuario dueño de la sesión
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)

    # Hash seguro del refresh token. Nunca guardar el token real.
    token_hash = Column(String(255), nullable=False, unique=True, index=True)

    # JWT ID del refresh token. Permite rotación y trazabilidad.
    jti = Column(String(120), nullable=False, unique=True, index=True)

    # Datos útiles para auditoría de sesiones
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(80), nullable=True)

    # Control de vida útil y revocación
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True, index=True)
    replaced_by_jti = Column(String(120), nullable=True)

    # Fecha de creación del registro
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
