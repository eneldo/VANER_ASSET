import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class OtIncidencia(Base):
    __tablename__ = "ot_incidencias"
    __table_args__ = (Index("ix_ot_incidencias_tenant_ot", "empresa_id", "mantenimiento_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    mantenimiento_id = Column(UUID(as_uuid=True), ForeignKey("mantenimientos.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(40), nullable=False, default="TECNICA")
    severidad = Column(String(20), nullable=False, default="MEDIA")
    descripcion = Column(Text, nullable=False)
    resuelta = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
