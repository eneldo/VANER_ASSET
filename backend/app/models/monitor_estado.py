# ============================================================
# MODELO OPCIONAL MONITOR ESTADO
# Archivo: backend/app/models/monitor_estado.py
# Fase 34.2.4
# ============================================================
# Este modelo queda listo para guardar snapshots históricos.
# En esta fase los endpoints consultan métricas en tiempo real.
# ============================================================

import uuid
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class MonitorEstado(Base):
    __tablename__ = "monitor_estado"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tipo = Column(String(80), nullable=False, index=True)  # VPS, POSTGRESQL, DOCKER
    estado = Column(String(40), nullable=False, default="OK")
    mensaje = Column(String(255), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), index=True)
