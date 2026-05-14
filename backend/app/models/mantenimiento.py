# ============================================================
# MODELO: Mantenimiento
# Archivo: backend/app/models/mantenimiento.py
# FASE 32 — Coordinador PRO / Mantenimientos PRO
# ============================================================

import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    # ========================================================
    # ID PRINCIPAL UUID
    # ========================================================

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # ========================================================
    # RELACIONES PRINCIPALES
    # ========================================================

    equipo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    tecnico_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tecnicos.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    sede_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sedes.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # ========================================================
    # INFORMACIÓN DEL MANTENIMIENTO
    # ========================================================

    tipo = Column(String(50), nullable=False)
    estado = Column(String(30), nullable=False, default="PROGRAMADO")

    descripcion = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    estado_inicial = Column(Text, nullable=True)
    estado_inicial_equipo = Column(Text, nullable=True)

    acciones_realizadas = Column(Text, nullable=True)
    resultado_final = Column(Text, nullable=True)

    observacion_estado = Column(Text, nullable=True)
    motivo_anulacion = Column(Text, nullable=True)

    costo = Column(Numeric(12, 2), nullable=True)

    # ========================================================
    # FECHAS OPERATIVAS
    # ========================================================

    fecha_programada = Column(DateTime, nullable=True)

    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)

    fecha_asignacion = Column(DateTime, nullable=True)
    fecha_pausa = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)

    fecha_inicio_programada = Column(DateTime, nullable=True)
    fecha_fin_programada = Column(DateTime, nullable=True)

    # ========================================================
    # UBICACIÓN
    # ========================================================

    latitud = Column(String(100), nullable=True)
    longitud = Column(String(100), nullable=True)

    # ========================================================
    # FECHAS DEL SISTEMA
    # ========================================================

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    creado_en = Column(DateTime, server_default=func.now())
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # ========================================================
    # RELACIONES ORM
    # ========================================================

    equipo = relationship("Equipo")
    tecnico = relationship("Tecnico")
    empresa = relationship("Empresa")
    sede = relationship("Sede")

    historial = relationship(
        "HistMantenimiento",
        back_populates="mantenimiento",
        cascade="all, delete-orphan"
    )