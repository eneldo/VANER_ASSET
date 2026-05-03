# =========================================================
# MODELO EMPRESA
# Tabla: empresas
# Guarda las empresas cliente del sistema SGA PRO
# =========================================================

import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Empresa(Base):
    __tablename__ = "empresas"

    # Identificador único
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Datos principales de la empresa
    nombre = Column(String(150), nullable=False)
    nit = Column(String(50), nullable=True)
    telefono = Column(String(50), nullable=True)
    direccion = Column(Text, nullable=True)
    correo = Column(String(150), nullable=True)

    # Logo usado en la hoja de vida del equipo
    logo_url = Column(Text, nullable=True)

    # Estado lógico
    activo = Column(Boolean, default=True)

    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())