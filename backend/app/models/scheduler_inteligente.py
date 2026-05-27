# ============================================================
# MODELOS - SCHEDULER INTELIGENTE PRO
# Archivo: backend/app/models/scheduler_inteligente.py
# Fase 34.2.7
# ============================================================

import uuid
from sqlalchemy import Column, String, Boolean, Integer, Text, Date, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class SchedulerRegla(Base):
    """Regla configurable para generar o sugerir mantenimientos."""

    __tablename__ = "scheduler_reglas_mantenimiento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    nombre = Column(String(180), nullable=False)
    descripcion = Column(Text, nullable=True)

    equipo_id = Column(Integer, ForeignKey("equipos.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnicos.id", ondelete="SET NULL"), nullable=True, index=True)

    tipo_mantenimiento = Column(String(60), nullable=False, default="PREVENTIVO")
    frecuencia_dias = Column(Integer, nullable=False, default=30)
    fecha_inicio = Column(Date, nullable=False)
    proxima_fecha = Column(Date, nullable=True, index=True)

    prioridad = Column(String(30), nullable=False, default="MEDIA")
    estado_inicial = Column(String(30), nullable=False, default="PROGRAMADO")

    # MANUAL: no genera; SEMIAUTOMATICO: crea sugerencia; AUTOMATICO: crea mantenimiento.
    modo = Column(String(30), nullable=False, default="SEMIAUTOMATICO")
    activo = Column(Boolean, nullable=False, default=True)

    ultimo_mantenimiento_id = Column(Integer, nullable=True)
    ultima_ejecucion = Column(DateTime(timezone=True), nullable=True)

    configuracion = Column(JSON, nullable=True, default=dict)

    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SchedulerSugerencia(Base):
    """Sugerencia generada por el scheduler para aprobación manual."""

    __tablename__ = "scheduler_sugerencias_mantenimiento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    regla_id = Column(UUID(as_uuid=True), ForeignKey("scheduler_reglas_mantenimiento.id", ondelete="CASCADE"), nullable=False, index=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnicos.id", ondelete="SET NULL"), nullable=True)

    tipo_mantenimiento = Column(String(60), nullable=False, default="PREVENTIVO")
    fecha_programada = Column(Date, nullable=False, index=True)
    prioridad = Column(String(30), nullable=False, default="MEDIA")

    estado = Column(String(30), nullable=False, default="PENDIENTE")  # PENDIENTE/APROBADA/RECHAZADA/GENERADA
    mensaje = Column(Text, nullable=True)
    mantenimiento_id = Column(Integer, nullable=True)

    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SchedulerLog(Base):
    """Bitácora de ejecuciones del scheduler inteligente."""

    __tablename__ = "scheduler_inteligente_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nivel = Column(String(20), nullable=False, default="INFO")
    evento = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True, default=dict)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
