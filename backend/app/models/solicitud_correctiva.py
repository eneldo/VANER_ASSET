import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class SolicitudCorrectiva(Base):
    __tablename__ = "solicitudes_correctivas"
    __table_args__ = (
        Index("ix_solicitudes_tenant_estado", "empresa_id", "estado"),
        Index("ix_solicitudes_tenant_fecha", "empresa_id", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False)
    sede_id = Column(UUID(as_uuid=True), ForeignKey("sedes.id", ondelete="RESTRICT"), nullable=False)
    equipo_id = Column(UUID(as_uuid=True), ForeignKey("equipos.id", ondelete="SET NULL"), nullable=True)
    solicitante_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    mantenimiento_id = Column(UUID(as_uuid=True), ForeignKey("mantenimientos.id", ondelete="SET NULL"), nullable=True)
    client_request_id = Column(String(80), nullable=True, unique=True)

    titulo = Column(String(160), nullable=False)
    descripcion = Column(Text, nullable=False)
    prioridad = Column(String(20), nullable=False, default="EMERGENCIA")
    estado = Column(String(30), nullable=False, default="NUEVA")
    contacto_nombre = Column(String(150), nullable=True)
    contacto_telefono = Column(String(50), nullable=True)
    respuesta_coordinador = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    atendida_at = Column(DateTime, nullable=True)
