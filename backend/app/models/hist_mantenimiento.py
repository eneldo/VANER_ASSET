# ============================================================
# MODELO: Historial de Mantenimiento
# Archivo: app/models/hist_mantenimiento.py
# Objetivo:
#   Guardar cada cambio de estado de un mantenimiento.
# ============================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class HistMantenimiento(Base):
    __tablename__ = "hist_mantenimiento"

    # ID principal del historial
    id = Column(Integer, primary_key=True, index=True)

    # Mantenimiento relacionado
    mantenimiento_id = Column(
        Integer,
        ForeignKey("mantenimientos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Estado anterior antes del cambio
    estado_anterior = Column(String(30), nullable=True)

    # Estado nuevo aplicado
    estado_nuevo = Column(String(30), nullable=False)

    # Técnico relacionado al evento, si aplica
    tecnico_id = Column(
        Integer,
        ForeignKey("tecnicos.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Observación o nota del cambio
    observacion = Column(Text, nullable=True)

    # Usuario que creó el evento
    creado_por = Column(String(120), nullable=True)

    # Fecha automática del evento
    fecha_evento = Column(DateTime(timezone=False), server_default=func.now())

    # Relaciones ORM
    mantenimiento = relationship("Mantenimiento", back_populates="historial")
    tecnico = relationship("Tecnico")