# =========================================================
# MODELO TECNICO
# Tabla: tecnicos
# Perfil técnico vinculado a un usuario con rol TECNICO
# =========================================================

import uuid

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Tecnico(Base):
    __tablename__ = "tecnicos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        unique=True,
    )

    documento = Column(String(50), nullable=True)
    telefono = Column(String(50), nullable=True)
    especialidad = Column(String(150), nullable=True)
    cargo = Column(String(150), nullable=True)

    activo = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación directa con usuarios.
    # Esto permite obtener tecnico.usuario.nombre_completo.
    usuario = relationship("Usuario")