import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class OtRepuesto(Base):
    __tablename__ = "ot_repuestos"
    __table_args__ = (Index("ix_ot_repuestos_tenant_ot", "empresa_id", "mantenimiento_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    mantenimiento_id = Column(UUID(as_uuid=True), ForeignKey("mantenimientos.id", ondelete="CASCADE"), nullable=False)
    descripcion = Column(String(250), nullable=False)
    referencia = Column(String(120), nullable=True)
    cantidad = Column(Numeric(12, 3), nullable=False)
    unidad = Column(String(30), nullable=False, default="UNIDAD")
    costo_unitario = Column(Numeric(14, 2), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
