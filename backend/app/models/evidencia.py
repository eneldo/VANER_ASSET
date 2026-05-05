# =========================================================
# MODELO EVIDENCIA PRO
# Tabla: evidencias
# Guarda fotos/PDF asociados a un mantenimiento y equipo
# =========================================================

import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Evidencia(Base):
    __tablename__ = "evidencias"

    # Identificador único de la evidencia
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Mantenimiento relacionado
    mantenimiento_id = Column(
        UUID(as_uuid=True),
        ForeignKey("mantenimientos.id"),
        nullable=False
    )

    # Equipo relacionado.
    # Esto permite crear galería de evidencias por equipo.
    equipo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipos.id"),
        nullable=False
    )

    # Tipo de evidencia:
    # ANTES, DURANTE, DESPUES, SOPORTE
    tipo = Column(String(30), nullable=False)

    # Ruta donde queda guardado el archivo
    archivo_url = Column(Text, nullable=False)

    # Nombre original del archivo subido
    nombre_original = Column(String(255), nullable=True)

    # Descripción opcional
    descripcion = Column(Text, nullable=True)

    # Fecha de carga
    created_at = Column(DateTime, server_default=func.now())