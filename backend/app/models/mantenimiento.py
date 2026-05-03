# =========================================================
# MODELO MANTENIMIENTO
# Tabla: mantenimientos
# Gestiona mantenimientos preventivos, correctivos, calibración e inspección
# =========================================================

import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    # Identificador único del mantenimiento
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Equipo al que pertenece el mantenimiento
    equipo_id = Column(UUID(as_uuid=True), ForeignKey("equipos.id"), nullable=False)

    # Técnico asignado al mantenimiento
    tecnico_id = Column(UUID(as_uuid=True), ForeignKey("tecnicos.id"), nullable=True)

    # Tipo: PREVENTIVO, CORRECTIVO, CALIBRACION, INSPECCION
    tipo = Column(String(50), nullable=False)

    # Estado: PROGRAMADO, ASIGNADO, EN_PROCESO, PAUSADO, FINALIZADO, ANULADO
    estado = Column(String(50), default="PROGRAMADO")

    # Fechas del mantenimiento
    fecha_programada = Column(DateTime, nullable=False)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)

    # Información diligenciada por el técnico
    estado_inicial = Column(Text, nullable=True)
    acciones_realizadas = Column(Text, nullable=True)
    resultado_final = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())