# ============================================================
# MODELO: Historial de Mantenimiento
# Archivo: app/models/hist_mantenimiento.py
# Objetivo:
#   Guardar cada cambio de estado de un mantenimiento.
# ============================================================

import uuid

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class HistMantenimiento(Base):
    __tablename__ = "hist_mantenimiento"

    # =========================================================
    # ID principal del historial
    # =========================================================
    id = Column(Integer, primary_key=True, index=True)

    # =========================================================
    # Mantenimiento relacionado
    # IMPORTANTE:
    # mantenimientos.id usa UUID
    # por eso aquí también debe ser UUID
    # =========================================================
    mantenimiento_id = Column(
        UUID(as_uuid=True),
        ForeignKey("mantenimientos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # =========================================================
    # Estado anterior
    # =========================================================
    estado_anterior = Column(String(30), nullable=True)

    # =========================================================
    # Estado nuevo
    # =========================================================
    estado_nuevo = Column(String(30), nullable=False)

    # =========================================================
    # Técnico relacionado
    # tecnicos.id sigue siendo INTEGER
    # =========================================================
    tecnico_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tecnicos.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # =========================================================
    # Observaciones
    # =========================================================
    observacion = Column(Text, nullable=True)

    # =========================================================
    # Usuario que generó el cambio
    # =========================================================
    creado_por = Column(String(120), nullable=True)

    # =========================================================
    # Fecha automática
    # =========================================================
    fecha_evento = Column(
        DateTime(timezone=False),
        server_default=func.now()
    )

    # =========================================================
    # Relaciones ORM
    # =========================================================
    mantenimiento = relationship(
        "Mantenimiento",
        back_populates="historial"
    )

    tecnico = relationship("Tecnico")