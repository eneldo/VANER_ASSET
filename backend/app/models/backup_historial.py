# ============================================================
# MODELO: BackupHistorial
# Archivo: backend/app/models/backup_historial.py
# Fase 34.2.2 - Backups Inteligentes SaaS PRO
# ============================================================

import uuid
from sqlalchemy import Column, String, Text, Boolean, BigInteger, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class BackupHistorial(Base):
    """Registro histórico de backups manuales y automáticos."""

    __tablename__ = "backup_historial"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tipo = Column(String(50), nullable=False, default="MANUAL")
    estado = Column(String(30), nullable=False, default="PENDIENTE", index=True)

    nombre_archivo = Column(String(255), nullable=True)
    ruta_archivo = Column(Text, nullable=True)
    tamano_bytes = Column(BigInteger, nullable=False, default=0)
    mensaje = Column(Text, nullable=True)

    incluye_db = Column(Boolean, nullable=False, default=True)
    incluye_uploads = Column(Boolean, nullable=False, default=True)
    incluye_codigo = Column(Boolean, nullable=False, default=False)

    iniciado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    finalizado_en = Column(DateTime(timezone=True), nullable=True)
    creado_por = Column(String(120), nullable=True)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
