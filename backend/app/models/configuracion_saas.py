# ============================================================
# MODELO: Configuración Inteligente SaaS
# Archivo: backend/app/models/configuracion_saas.py
# Fase 34.1 - Configuración Inteligente SaaS PRO
# ============================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.database import Base
from app.product import PRODUCT_NAME


class ConfiguracionSaaS(Base):
    """
    Tabla única para guardar la configuración global de la plataforma SGA SaaS.

    Se usa una sola fila activa con id=1 para evitar crear muchas columnas rígidas.
    Los bloques JSONB permiten crecer la configuración sin romper la base de datos.
    """

    __tablename__ = "configuracion_saas"

    id = Column(Integer, primary_key=True, index=True, default=1)

    # Datos visuales / identidad de plataforma
    nombre_plataforma = Column(String(150), nullable=False, default=PRODUCT_NAME)
    logo_url = Column(Text, nullable=True)
    color_primario = Column(String(20), nullable=False, default="#2563eb")
    color_secundario = Column(String(20), nullable=False, default="#0f172a")
    color_acento = Column(String(20), nullable=False, default="#22c55e")

    # Bloques inteligentes configurables
    smtp = Column(JSONB, nullable=False, default=dict)
    backups = Column(JSONB, nullable=False, default=dict)
    evidencias = Column(JSONB, nullable=False, default=dict)
    mantenimiento = Column(JSONB, nullable=False, default=dict)
    notificaciones = Column(JSONB, nullable=False, default=dict)

    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
