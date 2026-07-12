import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class PlantillaReporte(Base):
    __tablename__ = "plantillas_reporte"
    __table_args__ = (Index("ix_plantillas_reporte_scope", "empresa_id", "tipo", "activo"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=True)
    creado_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    nombre = Column(String(150), nullable=False)
    tipo = Column(String(20), nullable=False, default="AMBOS")
    titulo = Column(String(220), nullable=False)
    color_primario = Column(String(7), nullable=False, default="#1E3A8A")
    pie_pagina = Column(Text, nullable=True)
    incluir_logo = Column(Boolean, nullable=False, default=True)
    incluir_evidencias = Column(Boolean, nullable=False, default=True)
    incluir_firmas = Column(Boolean, nullable=False, default=True)
    incluir_costos = Column(Boolean, nullable=False, default=False)
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
