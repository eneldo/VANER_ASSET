# ============================================================
# FASE 30 - MODELO SQLALCHEMY: AUDITORÍA PRO
# Archivo: backend/app/models/auditoria_evento.py
# Objetivo:
#   Representar la tabla auditoria_eventos en SQLAlchemy.
#   Esta tabla guarda acciones importantes del sistema: creación,
#   edición, eliminación, cambios de estado, accesos y errores.
# ============================================================

import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base


class AuditoriaEvento(Base):
    """Modelo central de eventos de auditoría del sistema."""

    __tablename__ = "auditoria_eventos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Usuario que ejecutó la acción. Se permite NULL para eventos automáticos.
    usuario_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    usuario_nombre = Column(String(180), nullable=True)
    usuario_rol = Column(String(60), nullable=True)

    # Empresa relacionada. Útil para filtrar auditoría multiempresa.
    empresa_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Información principal del evento.
    modulo = Column(String(80), nullable=False, index=True)
    accion = Column(String(80), nullable=False, index=True)
    entidad = Column(String(120), nullable=True)
    entidad_id = Column(String(120), nullable=True)
    descripcion = Column(Text, nullable=True)

    # Datos técnicos de origen.
    ip_origen = Column(String(80), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Nivel: INFO, WARNING, ERROR, SECURITY.
    nivel = Column(String(30), nullable=False, default="INFO", index=True)

    # JSON opcional para guardar cambios, valores anteriores/nuevos, etc.
    meta_data = Column("metadata",JSONB, nullable=True)

    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False, index=True)
