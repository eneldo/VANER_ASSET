# ============================================================
# MODELO: Mantenimiento
# Archivo: app/models/mantenimiento.py
# Fase 18.1 / 18.2 - Mantenimientos PRO
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    id = Column(Integer, primary_key=True, index=True)

    equipo_id = Column(Integer, ForeignKey("equipos.id", ondelete="CASCADE"), nullable=False, index=True)

    tipo = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_programada = Column(Date, nullable=True)

    estado = Column(String(30), nullable=False, default="PROGRAMADO")

    tecnico_id = Column(Integer, ForeignKey("tecnicos.id", ondelete="SET NULL"), nullable=True, index=True)

    fecha_asignacion = Column(DateTime, nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_pausa = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)

    observaciones = Column(Text, nullable=True)
    observacion_estado = Column(Text, nullable=True)
    motivo_anulacion = Column(Text, nullable=True)

    costo = Column(Numeric(12, 2), nullable=True)

    creado_en = Column(DateTime, server_default=func.now())
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    equipo = relationship("Equipo")
    tecnico = relationship("Tecnico")
    historial = relationship(
        "HistMantenimiento",
        back_populates="mantenimiento",
        cascade="all, delete-orphan"
    )