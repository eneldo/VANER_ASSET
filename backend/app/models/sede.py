# =========================================================
# MODELO SEDE
# Tabla: sedes
# Cada sede pertenece a una empresa
# =========================================================

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Sede(Base):
    __tablename__ = "sedes"

    # Identificador único
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relación con empresa
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)

    # Datos principales de la sede
    nombre = Column(String(150), nullable=False)
    direccion = Column(Text, nullable=True)
    telefono = Column(String(50), nullable=True)
    responsable = Column(String(150), nullable=True)

    # Estado lógico
    activo = Column(Boolean, default=True)

    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())