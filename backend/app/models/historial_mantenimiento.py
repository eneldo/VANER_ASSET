# =========================================================
# MODELO HISTORIAL MANTENIMIENTO
# Tabla: historial_mantenimiento
# Guarda auditoría de cambios de estado de mantenimientos
# =========================================================

import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class HistorialMantenimiento(Base):
    __tablename__ = "historial_mantenimiento"

    # Identificador único
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Mantenimiento relacionado
    mantenimiento_id = Column(UUID(as_uuid=True), ForeignKey("mantenimientos.id"), nullable=False)

    # Usuario que ejecuta el cambio
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    # Estado anterior y nuevo
    estado_anterior = Column(String(50), nullable=True)
    estado_nuevo = Column(String(50), nullable=True)

    # Comentario del cambio
    comentario = Column(Text, nullable=True)

    # Fecha del cambio
    created_at = Column(DateTime, server_default=func.now())