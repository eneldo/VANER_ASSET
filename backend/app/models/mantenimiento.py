# ============================================================
# MODELO: Mantenimiento
# Archivo: backend/app/models/mantenimiento.py
# FASE 32 — Coordinador PRO / Mantenimientos PRO
# ============================================================

import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    # ========================================================
    # ID PRINCIPAL UUID
    # ========================================================

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # ========================================================
    # RELACIONES PRINCIPALES
    # ========================================================

    equipo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    tecnico_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tecnicos.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    sede_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sedes.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # ========================================================
    # INFORMACIÓN DEL MANTENIMIENTO
    # ========================================================

    tipo = Column(String(50), nullable=False)
    # PROGRAMADO, PREVENTIVO, CORRECTIVO, URGENTE, ANULADO

    estado = Column(String(30), nullable=False, default="PROGRAMADO")
    # PROGRAMADO, EN_PROGRESO, COMPLETADO, CANCELADO, ANULADO

    prioridad = Column(String(20), nullable=True, default="MEDIA")
    # BAJA, MEDIA, ALTA, CRITICA

    descripcion = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    estado_inicial = Column(Text, nullable=True)
    estado_inicial_equipo = Column(Text, nullable=True)

    acciones_realizadas = Column(Text, nullable=True)
    resultado_final = Column(Text, nullable=True)

    falla_incidencia = Column(Text, nullable=True)
    diagnostico = Column(Text, nullable=True)
    trabajo_realizado = Column(Text, nullable=True)

    # Repuestos utilizados
    repuestos = Column(JSON, nullable=True)
    # [{ "id": uuid, "codigo": str, "descripcion": str, "cantidad": int, "costo_unitual": Numeric }]

    # Costos detallados
    costo = Column(Numeric(12, 2), nullable=True)
    costo_mano_obra = Column(Numeric(12, 2), nullable=True)
    costo_repuestos = Column(Numeric(12, 2), nullable=True)
    costo_total = Column(Numeric(12, 2), nullable=True)

    # Evidencias
    evidencia_fotos = Column(JSON, nullable=True)
    # [{"url": str, "descripcion": str, "fecha_subida": datetime}]
    evidencia_documentos = Column(JSON, nullable=True)
    # [{"url": str, "tipo": str, "descripcion": str, "fecha_subida": datetime}]

    solucion = Column(Text, nullable=True)
    cerrado = Column(Boolean, default=False)
    fecha_cierre = Column(DateTime, nullable=True)

    # Responsable
    responsable_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True, index=True)

    # Auditoría interna
    observacion_estado = Column(Text, nullable=True)
    motivo_anulacion = Column(Text, nullable=True)

    # ========================================================
    # FECHAS OPERATIVAS
    # ========================================================

    fecha_programada = Column(DateTime, nullable=True)

    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)

    fecha_asignacion = Column(DateTime, nullable=True)
    fecha_pausa = Column(DateTime, nullable=True)
    fecha_finalizacion = Column(DateTime, nullable=True)

    # Seguimiento de movimiento de activo
    tipo_movimiento = Column(String(50), nullable=True)
    # ASIGNACIÓN, DEVOLUCIÓN, TRANSFERENCIA, BAJA

    activo_afectado_id = Column(UUID(as_uuid=True), nullable=True)
    activo_afectado_tipo = Column(String(50), nullable=True)
    # EQUIPO, REPUESTO, CONSUMIBLE

    fecha_inicio_programada = Column(DateTime, nullable=True)
    fecha_fin_programada = Column(DateTime, nullable=True)

    # ========================================================
    # UBICACIÓN
    # ========================================================

    latitud = Column(String(100), nullable=True)
    longitud = Column(String(100), nullable=True)

    # ========================================================
    # FECHAS DEL SISTEMA
    # ========================================================

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    creado_en = Column(DateTime, server_default=func.now())
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # ========================================================
    # RELACIONES ORM
    # ========================================================

    equipo = relationship("Equipo")
    tecnico = relationship("Tecnico")
    empresa = relationship("Empresa")
    sede = relationship("Sede")

    historial = relationship(
        "HistMantenimiento",
        back_populates="mantenimiento",
        cascade="all, delete-orphan"
    )