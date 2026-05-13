# =========================================================
# MODELO AUDITORÍA PRO
# Archivo: backend/app/models/auditoria_pro.py
# =========================================================
# Tabla central de trazabilidad empresarial:
# - actividad de usuarios,
# - eventos de seguridad,
# - accesos denegados,
# - operaciones críticas,
# - IP, navegador, request_id y resultado.
# =========================================================

import uuid
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import Base


class AuditoriaProEvento(Base):
    """Evento de auditoría y monitoreo del sistema SaaS."""

    __tablename__ = "auditoria_pro_eventos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Usuario / empresa
    usuario_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    usuario_email = Column(String(180), nullable=True, index=True)
    usuario_nombre = Column(String(220), nullable=True)
    rol = Column(String(60), nullable=True, index=True)
    empresa_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Funcionalidad
    modulo = Column(String(100), nullable=False, default="SISTEMA", index=True)
    accion = Column(String(100), nullable=False, default="EVENTO", index=True)
    recurso_tipo = Column(String(120), nullable=True)
    recurso_id = Column(String(120), nullable=True)

    # HTTP / seguridad
    metodo = Column(String(20), nullable=True)
    ruta = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    ip_origen = Column(String(80), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(120), nullable=True, index=True)

    # Resultado
    permitido = Column(Boolean, nullable=False, default=True, index=True)
    severidad = Column(String(30), nullable=False, default="INFO", index=True)
    detalle = Column(Text, nullable=True)
    datos_extra = Column(JSONB, nullable=True)

    creado_en = Column(DateTime(timezone=False), server_default=func.now(), nullable=False, index=True)
