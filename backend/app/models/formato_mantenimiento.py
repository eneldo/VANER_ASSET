# ============================================================
# MODELO: FormatoMantenimiento
# Archivo: backend/app/models/formato_mantenimiento.py
# ============================================================

import uuid

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class FormatoMantenimiento(Base):
    __tablename__ = "formatos_mantenimiento"

    # =========================================================
    # ID local del formato
    # =========================================================
    id = Column(Integer, primary_key=True, index=True)

    # =========================================================
    # Relaciones UUID
    # =========================================================
    mantenimiento_id = Column(
        UUID(as_uuid=True),
        ForeignKey("mantenimientos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    tecnico_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tecnicos.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # =========================================================
    # Datos generales
    # =========================================================
    fecha = Column(Date, nullable=True)
    numero_ot = Column(String(80), nullable=True)
    numero_inventario = Column(String(120), nullable=True)
    ubicacion = Column(String(180), nullable=True)

    mantenimiento_tipo = Column(String(50), default="Preventivo")

    tecnico_nombre = Column(String(180), nullable=True)
    tecnico_auxiliar = Column(String(180), nullable=True)

    tipo_equipo = Column(String(80), nullable=True)

    # =========================================================
    # Datos dinámicos
    # =========================================================
    trabajos_realizados = Column(JSONB, default=dict)
    datos_funcionamiento = Column(JSONB, default=dict)
    repuestos_utilizados = Column(JSONB, default=list)

    observaciones = Column(Text, nullable=True)

    # =========================================================
    # Firmas
    # =========================================================
    firma_usuario = Column(Text, nullable=True)
    firma_operario = Column(Text, nullable=True)
    firma_coordinador = Column(Text, nullable=True)

    # =========================================================
    # Fechas
    # =========================================================
    creado_en = Column(
        DateTime(timezone=False),
        server_default=func.now()
    )

    actualizado_en = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now()
    )

    # =========================================================
    # Relaciones ORM
    # =========================================================
    mantenimiento = relationship("Mantenimiento")
    tecnico = relationship("Tecnico")