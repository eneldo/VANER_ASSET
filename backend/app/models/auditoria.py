# ============================================================
# MODELO: Auditoría del Sistema
# Proyecto: SGAHolding
# Descripción:
# Registra eventos importantes del sistema como creación,
# edición, eliminación, cambios de estado e ingresos críticos.
# ============================================================

import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class AuditoriaSistema(Base):
    __tablename__ = "auditoria_sistema"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    usuario_id = Column(UUID(as_uuid=True), nullable=True)
    usuario_nombre = Column(String(150), nullable=True)
    usuario_rol = Column(String(50), nullable=True)

    modulo = Column(String(100), nullable=False)
    accion = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)

    entidad = Column(String(100), nullable=True)
    entidad_id = Column(UUID(as_uuid=True), nullable=True)

    ip_origen = Column(String(100), nullable=True)
    user_agent = Column(Text, nullable=True)

    fecha = Column(DateTime(timezone=False), server_default=func.now())