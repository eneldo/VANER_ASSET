import uuid

from sqlalchemy import Column, String, Text, DateTime, Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class ReportePublicado(Base):
    __tablename__ = "reportes_publicados"
    __table_args__ = (
        Index("ix_reportes_tenant_estado", "empresa_id", "estado"),
        Index("ix_reportes_tenant_periodo", "empresa_id", "periodo_inicio", "periodo_fin"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    mantenimiento_id = Column(UUID(as_uuid=True), ForeignKey("mantenimientos.id", ondelete="SET NULL"), nullable=True)
    creado_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    aprobado_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    tipo = Column(String(30), nullable=False)
    titulo = Column(String(220), nullable=False)
    estado = Column(String(30), nullable=False, default="BORRADOR")
    storage_key = Column(Text, nullable=False)
    periodo_inicio = Column(Date, nullable=True)
    periodo_fin = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    aprobado_at = Column(DateTime, nullable=True)
    publicado_at = Column(DateTime, nullable=True)
