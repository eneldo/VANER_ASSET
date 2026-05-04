# =========================================================
# MODELO EQUIPO
# Tabla: equipos
# Guarda los datos básicos del equipo - PASO 1
# =========================================================

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Equipo(Base):
    __tablename__ = "equipos"

    # Identificador único del equipo
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones principales
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    sede_id = Column(UUID(as_uuid=True), ForeignKey("sedes.id"), nullable=False)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id"), nullable=True)

    # Datos básicos del equipo
    nombre = Column(String(150), nullable=False)
    marca = Column(String(100), nullable=True)
    modelo = Column(String(100), nullable=True)
    serie = Column(String(100), nullable=True)
    ubicacion = Column(String(150), nullable=True)
    invima = Column(String(100), nullable=True)

    # Código interno o código de inventario
    codigo_id = Column(String(100), unique=True, nullable=True)
    # Número o código de inventario físico/institucional
    inventario = Column(String(100), nullable=True)

    # Estado del equipo:
    # OPERATIVO, EN_MANTENIMIENTO, FUERA_DE_SERVICIO, BAJA
    estado = Column(String(50), default="OPERATIVO")

    # Criticidad:
    # BAJA, MEDIA, ALTA, CRITICA
    criticidad = Column(String(50), default="MEDIA")

    # Estado lógico
    activo = Column(Boolean, default=True)

    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())