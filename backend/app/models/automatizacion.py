# ============================================================
# MODELOS: Automatización SaaS PRO
# Archivo: backend/app/models/automatizacion.py
# Fase 34.2.1 - Núcleo Automatización SaaS
# ============================================================
# Este módulo es independiente. No modifica mantenimientos,
# evidencias, técnico, cliente ni configuración actual.
# ============================================================

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Automatizacion(Base):
    """
    Configuración central de cada automatización del sistema.

    Ejemplos de módulos:
    - backups
    - smtp
    - whatsapp
    - monitor
    - mantenimientos
    - limpieza_logs
    - devops
    """

    __tablename__ = "automatizaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    modulo = Column(String(80), nullable=False, unique=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)

    activo = Column(Boolean, nullable=False, default=False)
    frecuencia_minutos = Column(Integer, nullable=False, default=60)

    estado = Column(String(30), nullable=False, default="INACTIVO")
    mensaje = Column(Text, nullable=True)

    ultima_ejecucion = Column(DateTime(timezone=True), nullable=True)
    proxima_ejecucion = Column(DateTime(timezone=True), nullable=True)

    configuracion = Column(JSON, nullable=True, default=dict)

    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    logs = relationship("AutomatizacionLog", back_populates="automatizacion", cascade="all, delete-orphan")


class AutomatizacionLog(Base):
    """Historial de ejecución de jobs de automatización."""

    __tablename__ = "automatizacion_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    automatizacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("automatizaciones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    modulo = Column(String(80), nullable=False, index=True)
    nivel = Column(String(20), nullable=False, default="INFO")
    evento = Column(String(120), nullable=False)
    mensaje = Column(Text, nullable=True)
    duracion_ms = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True, default=dict)

    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    automatizacion = relationship("Automatizacion", back_populates="logs")
