# ============================================================
# MODELO: FormatoMantenimiento
# Archivo: backend/app/models/formato_mantenimiento.py
# Descripción:
# Guarda el formulario técnico tipo hoja impresa para mantenimientos
# preventivos/correctivos de aires acondicionados.
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class FormatoMantenimiento(Base):
    __tablename__ = "formatos_mantenimiento"

    id = Column(Integer, primary_key=True, index=True)

    # Relación lógica con mantenimiento
    mantenimiento_id = Column(Integer, nullable=False, index=True)
    tecnico_id = Column(Integer, nullable=True)

    # Datos generales del formato
    fecha = Column(Date, nullable=True)
    numero_ot = Column(String(80), nullable=True)
    numero_inventario = Column(String(120), nullable=True)
    ubicacion = Column(String(180), nullable=True)

    mantenimiento_tipo = Column(String(50), default="Preventivo")
    tecnico_nombre = Column(String(180), nullable=True)
    tecnico_auxiliar = Column(String(180), nullable=True)

    # Tipo de equipo seleccionado
    tipo_equipo = Column(String(80), nullable=True)

    # Datos dinámicos del formato
    trabajos_realizados = Column(JSONB, default=dict)
    datos_funcionamiento = Column(JSONB, default=dict)
    repuestos_utilizados = Column(JSONB, default=list)

    observaciones = Column(Text, nullable=True)

    # Firmas en base64 o texto
    firma_usuario = Column(Text, nullable=True)
    firma_operario = Column(Text, nullable=True)
    firma_coordinador = Column(Text, nullable=True)

    creado_en = Column(DateTime(timezone=False), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())