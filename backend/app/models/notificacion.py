# ============================================================
# MODELO: Notificacion
# Archivo: backend/app/models/notificacion.py
# ============================================================

import uuid

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Notificacion(Base):

    __tablename__ = "notificaciones"

    # =========================================================
    # ID local
    # =========================================================
    id = Column(Integer, primary_key=True, index=True)

    # =========================================================
    # Destino
    # =========================================================
    rol_destino = Column(String(30), nullable=False, index=True)

    # =========================================================
    # Relaciones UUID
    # =========================================================
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
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

    equipo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipos.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    mantenimiento_id = Column(
        UUID(as_uuid=True),
        ForeignKey("mantenimientos.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    tecnico_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tecnicos.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # =========================================================
    # Clasificación
    # =========================================================
    tipo = Column(String(40), nullable=False, default="INFO", index=True)

    prioridad = Column(
        String(20),
        nullable=False,
        default="MEDIA",
        index=True
    )

    # =========================================================
    # Contenido
    # =========================================================
    titulo = Column(String(180), nullable=False)

    mensaje = Column(Text, nullable=True)

    enlace = Column(String(255), nullable=True)

    # =========================================================
    # Estado lectura
    # =========================================================
    leida = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    creado_en = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    leido_en = Column(DateTime, nullable=True)

    # =========================================================
    # Relaciones ORM
    # =========================================================
    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    empresa = relationship("Empresa", foreign_keys=[empresa_id])

    sede = relationship("Sede", foreign_keys=[sede_id])

    equipo = relationship("Equipo", foreign_keys=[equipo_id])

    mantenimiento = relationship(
        "Mantenimiento",
        foreign_keys=[mantenimiento_id]
    )

    tecnico = relationship(
        "Tecnico",
        foreign_keys=[tecnico_id]
    )