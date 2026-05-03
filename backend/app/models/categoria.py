# =========================================================
# MODELO CATEGORIA
# Tabla: categorias
# Clasifica los equipos: Biomédico, Refrigeración, CCTV, etc.
# =========================================================

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    # Identificador único de la categoría
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Nombre de la categoría
    nombre = Column(String(100), nullable=False, unique=True)

    # Descripción opcional
    descripcion = Column(Text, nullable=True)

    # Estado lógico
    activo = Column(Boolean, default=True)

    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())