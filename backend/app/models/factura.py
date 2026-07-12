import uuid

from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.database import Base


class Factura(Base):
    __tablename__ = "facturas"
    __table_args__ = (
        Index("ix_facturas_empresa_estado", "empresa_id", "estado"),
        Index("ix_facturas_vencimiento", "fecha_vencimiento"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="RESTRICT"), nullable=False)
    creado_por_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    numero = Column(String(50), nullable=False, unique=True)
    concepto = Column(String(220), nullable=False)
    detalle = Column(JSONB, nullable=False, default=list)
    moneda = Column(String(3), nullable=False, default="COP")
    subtotal = Column(Numeric(14, 2), nullable=False)
    impuesto_porcentaje = Column(Numeric(5, 2), nullable=False, default=0)
    impuesto = Column(Numeric(14, 2), nullable=False, default=0)
    total = Column(Numeric(14, 2), nullable=False)
    estado = Column(String(20), nullable=False, default="BORRADOR")
    periodo_inicio = Column(Date, nullable=False)
    periodo_fin = Column(Date, nullable=False)
    fecha_emision = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    fecha_pago = Column(Date, nullable=True)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
