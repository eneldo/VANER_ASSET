# =========================================================
# MODELO EQUIPO
# Tabla: equipos
# Guarda los datos básicos del equipo - PASO 1
# =========================================================

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy import JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Equipo(Base):
    __tablename__ = "equipos"

    # Identificador único del equipo
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relaciones principales
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sede_id = Column(UUID(as_uuid=True), ForeignKey("sedes.id"), nullable=False, index=True)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id"), nullable=False, index=True)

    # Responsable actual del equipo
    responsable_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True, index=True)

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

    # Indicador de vida útil
    vida_util_meses = Column(Integer, nullable=True)
    # Control de cuántos meses de vida útil quedan

    # Estado lógico
    activo = Column(Boolean, default=True)

    # Auditoría
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Historial de cambios (JSON - tracking simplificado)
    # Registra cambios de: responsable, ubicacion, estado, criticidad
    # Formato: [{"timestamp": datetime, "campo": str, "anterior": any, "nuevo": any, "usuario_id": uuid}]
    historial_cambios = Column(MutableList.as_mutable(JSON), nullable=True)
