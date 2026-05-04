# =========================================================
# MODELO: EQUIPO HOJA DE VIDA TÉCNICA
# Tabla: equipo_hoja_vida
# PASO 2 del registro del equipo
# =========================================================

import uuid
from sqlalchemy import Column, String, Text, Boolean, Date, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class EquipoHojaVida(Base):
    __tablename__ = "equipo_hoja_vida"

    # Identificador único
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relación 1 a 1 con la tabla equipos
    equipo_id = Column(UUID(as_uuid=True), ForeignKey("equipos.id"), nullable=False, unique=True)

    # =====================================================
    # REGISTRO HISTÓRICO
    # =====================================================
    adquisicion = Column(String(150), nullable=True)
    costo = Column(Numeric(14, 2), nullable=True)
    fecha_compra = Column(Date, nullable=True)
    fecha_instalacion = Column(Date, nullable=True)
    proveedor = Column(String(150), nullable=True)
    pais_fabricacion = Column(String(100), nullable=True)
    fecha_fabricacion = Column(Date, nullable=True)
    vida_util = Column(String(100), nullable=True)
    requiere_calibracion = Column(Boolean, default=False)

    # =====================================================
    # REGISTRO TÉCNICO DE FUNCIONAMIENTO
    # =====================================================
    rango_voltaje = Column(String(100), nullable=True)
    rango_presion = Column(String(100), nullable=True)
    gas_refrigerante = Column(String(100), nullable=True)
    capacidad = Column(String(100), nullable=True)
    rango_corriente = Column(String(100), nullable=True)
    rango_velocidad = Column(String(100), nullable=True)
    rango_potencia = Column(String(100), nullable=True)
    rango_temperatura = Column(String(100), nullable=True)
    frecuencia = Column(String(100), nullable=True)
    rango_humedad = Column(String(100), nullable=True)
    otros = Column(Text, nullable=True)

    # =====================================================
    # REGISTRO DE APOYO TÉCNICO - MANUALES
    # =====================================================
    manual_operacion = Column(Boolean, default=False)
    manual_mantenimiento = Column(Boolean, default=False)
    manual_partes = Column(Boolean, default=False)
    manual_despiece = Column(Boolean, default=False)

    # =====================================================
    # REGISTRO DE APOYO TÉCNICO - PLANOS
    # =====================================================
    plano_electronico = Column(Boolean, default=False)
    plano_electrico = Column(Boolean, default=False)
    plano_neumatico = Column(Boolean, default=False)
    plano_mecanico = Column(Boolean, default=False)

    # =====================================================
    # CLASIFICACIÓN BIOMÉDICA
    # =====================================================
    clase_diagnostico = Column(Boolean, default=False)
    clase_prevencion = Column(Boolean, default=False)
    clase_rehabilitacion = Column(Boolean, default=False)
    clase_analisis = Column(Boolean, default=False)

    # =====================================================
    # CLASIFICACIÓN DE RIESGO
    # =====================================================
    riesgo_bajo = Column(Boolean, default=False)
    riesgo_moderado = Column(Boolean, default=False)
    riesgo_alto = Column(Boolean, default=False)
    riesgo_elevado = Column(Boolean, default=False)

    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())