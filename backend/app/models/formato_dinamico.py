# ============================================================
# MODELOS: FORMATOS Y BITÁCORAS DINÁMICAS PRO
# Archivo: backend/app/models/formato_dinamico.py
# Fase 33 - SGA PRO
# ============================================================
# Estos modelos permiten que una bitácora cambie automáticamente
# según el tipo de equipo asignado al mantenimiento.
# ============================================================

import uuid
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class TipoFormato(Base):
    """
    Catálogo maestro de formatos técnicos dinámicos.
    Ejemplos: CCTV, ASCENSOR, PLANTA_ELECTRICA, BOMBA_AGUA.
    """

    __tablename__ = "tipos_formatos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    codigo = Column(String(80), unique=True, nullable=False, index=True)
    nombre = Column(String(180), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    campos = relationship(
        "CampoFormato",
        back_populates="formato",
        cascade="all, delete-orphan",
        order_by="CampoFormato.orden.asc()",
    )


class CampoFormato(Base):
    """
    Campos o actividades de checklist de un formato.
    tipo_campo soportado en frontend: checkbox, texto, numero, select, textarea.
    """

    __tablename__ = "formatos_campos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    formato_id = Column(UUID(as_uuid=True), ForeignKey("tipos_formatos.id", ondelete="CASCADE"), nullable=False, index=True)

    seccion = Column(String(180), nullable=False, default="General")
    nombre_campo = Column(String(250), nullable=False)
    tipo_campo = Column(String(50), default="checkbox")
    opciones = Column(Text, nullable=True)  # Para selects, separadas por coma.
    obligatorio = Column(Boolean, default=False)
    orden = Column(Integer, default=1)
    activo = Column(Boolean, default=True)

    formato = relationship("TipoFormato", back_populates="campos")
    respuestas = relationship("BitacoraRespuesta", back_populates="campo")


class BitacoraDinamica(Base):
    """
    Encabezado de la bitácora diligenciada por el técnico.
    Una bitácora pertenece a un mantenimiento y a un formato dinámico.
    """

    __tablename__ = "bitacoras_dinamicas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    mantenimiento_id = Column(UUID(as_uuid=True), ForeignKey("mantenimientos.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(UUID(as_uuid=True), ForeignKey("tecnicos.id", ondelete="SET NULL"), nullable=True, index=True)
    formato_id = Column(UUID(as_uuid=True), ForeignKey("tipos_formatos.id", ondelete="SET NULL"), nullable=True, index=True)

    estado_inicial = Column(String(120), nullable=True)
    estado_final = Column(String(120), nullable=True)
    observaciones = Column(Text, nullable=True)
    recomendaciones = Column(Text, nullable=True)
    repuestos_utilizados = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    formato = relationship("TipoFormato")
    respuestas = relationship("BitacoraRespuesta", back_populates="bitacora", cascade="all, delete-orphan")


class BitacoraRespuesta(Base):
    """
    Respuestas individuales de cada campo/checklist diligenciado.
    """

    __tablename__ = "bitacoras_respuestas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    bitacora_id = Column(UUID(as_uuid=True), ForeignKey("bitacoras_dinamicas.id", ondelete="CASCADE"), nullable=False, index=True)
    campo_id = Column(UUID(as_uuid=True), ForeignKey("formatos_campos.id", ondelete="SET NULL"), nullable=True, index=True)

    valor = Column(Text, nullable=True)
    observacion = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    bitacora = relationship("BitacoraDinamica", back_populates="respuestas")
    campo = relationship("CampoFormato", back_populates="respuestas")
