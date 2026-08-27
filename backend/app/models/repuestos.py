# ============================================================
# MODELOS: Repuestos y Consumibles
# Módulo completo de inventario, bodegas, movimientos,
# solicitudes, proveedores y compatibilidad.
# ============================================================

import uuid
from sqlalchemy import (
    Column, String, Text, DateTime, Date, ForeignKey, Numeric,
    Boolean, Integer, Index, UniqueConstraint, CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


# ============================================================
# CATEGORÍAS DE REPUESTOS
# ============================================================

class CategoriaRepuesto(Base):
    __tablename__ = "categorias_repuestos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("empresa_id", "nombre", name="uq_categoria_repuesto_empresa_nombre"),
    )


# ============================================================
# UNIDADES DE MEDIDA
# ============================================================

class UnidadMedida(Base):
    __tablename__ = "unidades_medida"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(60), nullable=False, unique=True)
    abreviatura = Column(String(15), nullable=False, unique=True)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# ============================================================
# CATÁLOGO MAESTRO DE REPUESTOS
# ============================================================

class Repuesto(Base):
    __tablename__ = "repuestos"
    __table_args__ = (
        UniqueConstraint("empresa_id", "codigo", name="uq_repuesto_empresa_codigo"),
        Index("ix_repuestos_empresa_nombre", "empresa_id", "nombre"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)

    codigo = Column(String(60), nullable=False)
    codigo_barras = Column(String(120), nullable=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(String(20), nullable=False, default="REPUESTO")  # REPUESTO / CONSUMIBLE

    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias_repuestos.id", ondelete="SET NULL"), nullable=True)
    referencia = Column(String(120), nullable=True)
    marca = Column(String(100), nullable=True)
    fabricante = Column(String(120), nullable=True)

    unidad_medida_id = Column(UUID(as_uuid=True), ForeignKey("unidades_medida.id", ondelete="SET NULL"), nullable=True)

    precio_promedio = Column(Numeric(14, 4), nullable=True)
    ultimo_costo = Column(Numeric(14, 4), nullable=True)

    stock_minimo = Column(Numeric(12, 3), nullable=True, default=0)
    stock_maximo = Column(Numeric(12, 3), nullable=True)
    punto_reposicion = Column(Numeric(12, 3), nullable=True)
    tiempo_reposicion_dias = Column(Integer, nullable=True)

    maneja_lote = Column(Boolean, default=False, nullable=False)
    maneja_serial = Column(Boolean, default=False, nullable=False)
    control_vencimiento = Column(Boolean, default=False, nullable=False)

    foto_url = Column(Text, nullable=True)
    ficha_tecnica_url = Column(Text, nullable=True)

    activo = Column(Boolean, default=True, nullable=False, index=True)
    creado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ============================================================
# BODEGAS
# ============================================================

class Bodega(Base):
    __tablename__ = "bodegas"
    __table_args__ = (
        UniqueConstraint("empresa_id", "nombre", name="uq_bodega_empresa_nombre"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    sede_id = Column(UUID(as_uuid=True), ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    nombre = Column(String(120), nullable=False)
    direccion = Column(Text, nullable=True)
    telefono = Column(String(30), nullable=True)
    responsable_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# ============================================================
# EXISTENCIAS (stock por repuesto por bodega)
# ============================================================

class Existencia(Base):
    __tablename__ = "existencias_repuestos"
    __table_args__ = (
        UniqueConstraint("repuesto_id", "bodega_id", "lote", "serial", name="uq_existencia_repuesto_bodega_lote_serial"),
        Index("ix_existencias_empresa", "empresa_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    repuesto_id = Column(UUID(as_uuid=True), ForeignKey("repuestos.id", ondelete="CASCADE"), nullable=False, index=True)
    bodega_id = Column(UUID(as_uuid=True), ForeignKey("bodegas.id", ondelete="CASCADE"), nullable=False, index=True)

    existencia_fisica = Column(Numeric(12, 3), nullable=False, default=0)
    cantidad_reservada = Column(Numeric(12, 3), nullable=False, default=0)
    costo_promedio = Column(Numeric(14, 4), nullable=True)
    ultimo_costo = Column(Numeric(14, 4), nullable=True)

    lote = Column(String(60), nullable=True)
    serial = Column(String(60), nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("repuesto_id", "bodega_id", "lote", "serial", name="uq_existencia_repuesto_bodega_lote_serial"),
        Index("ix_existencias_empresa", "empresa_id"),
        CheckConstraint("existencia_fisica >= 0", name="ck_existencia_fisica_no_negativa"),
        CheckConstraint("cantidad_reservada >= 0", name="ck_cantidad_reservada_no_negativa"),
    )

    repuesto = relationship("Repuesto")
    bodega = relationship("Bodega")


# ============================================================
# MOVIMIENTOS DE INVENTARIO (inmutables)
# ============================================================

class MovimientoRepuesto(Base):
    __tablename__ = "movimientos_repuestos"
    __table_args__ = (
        Index("ix_movimientos_empresa_fecha", "empresa_id", "created_at"),
        Index("ix_movimientos_repuesto", "repuesto_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    repuesto_id = Column(UUID(as_uuid=True), ForeignKey("repuestos.id", ondelete="CASCADE"), nullable=False, index=True)
    bodega_origen_id = Column(UUID(as_uuid=True), ForeignKey("bodegas.id", ondelete="SET NULL"), nullable=True)
    bodega_destino_id = Column(UUID(as_uuid=True), ForeignKey("bodegas.id", ondelete="SET NULL"), nullable=True)

    tipo_movimiento = Column(String(30), nullable=False)
    # ENTRADA_COMPRA, ENTRADA_INICIAL, SALIDA_OT, RESERVA, LIBERACION_RESERVA,
    # ENTREGA_TECNICO, CONSUMO, DEVOLUCION, TRANSFERENCIA,
    # AJUSTE_POSITIVO, AJUSTE_NEGATIVO, BAJA_DANO, BAJA_VENCIMIENTO

    cantidad = Column(Numeric(12, 3), nullable=False)
    unidad = Column(String(30), nullable=False, default="UNIDAD")
    costo_unitario = Column(Numeric(14, 4), nullable=True)
    costo_total = Column(Numeric(14, 4), nullable=True)

    existencia_anterior = Column(Numeric(12, 3), nullable=True)
    existencia_posterior = Column(Numeric(12, 3), nullable=True)

    mantenimiento_id = Column(UUID(as_uuid=True), ForeignKey("mantenimientos.id", ondelete="SET NULL"), nullable=True)
    solicitud_id = Column(UUID(as_uuid=True), nullable=True)

    documento = Column(String(120), nullable=True)
    motivo = Column(Text, nullable=True)
    idempotency_key = Column(String(120), nullable=True, unique=True)

    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    repuesto = relationship("Repuesto")
    bodega_origen = relationship("Bodega", foreign_keys=[bodega_origen_id])
    bodega_destino = relationship("Bodega", foreign_keys=[bodega_destino_id])


# ============================================================
# SOLICITUDES DE REPUESTOS
# ============================================================

class SolicitudRepuesto(Base):
    __tablename__ = "solicitudes_repuestos"
    __table_args__ = (
        Index("ix_solicitudes_empresa_estado", "empresa_id", "estado"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    mantenimiento_id = Column(UUID(as_uuid=True), ForeignKey("mantenimientos.id", ondelete="CASCADE"), nullable=False, index=True)
    repuesto_id = Column(UUID(as_uuid=True), ForeignKey("repuestos.id", ondelete="CASCADE"), nullable=False, index=True)
    bodega_id = Column(UUID(as_uuid=True), ForeignKey("bodegas.id", ondelete="SET NULL"), nullable=True)

    cantidad_solicitada = Column(Numeric(12, 3), nullable=False)
    cantidad_aprobada = Column(Numeric(12, 3), nullable=True)
    cantidad_entregada = Column(Numeric(12, 3), nullable=True)
    cantidad_devuelta = Column(Numeric(12, 3), nullable=True)

    estado = Column(String(30), nullable=False, default="SOLICITADO")
    # SOLICITADO, APROBADO, RESERVADO, ENTREGADO, CONSUMIDO,
    # DEVUELTO_PARCIAL, DEVUELTO, RECHAZADO, CANCELADO

    observaciones = Column(Text, nullable=True)
    solicitado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    autorizado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    entregado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    repuesto = relationship("Repuesto")
    bodega = relationship("Bodega")
    mantenimiento = relationship("Mantenimiento")


# ============================================================
# PROVEEDORES
# ============================================================

class ProveedorRepuesto(Base):
    __tablename__ = "proveedores_repuestos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    nit = Column(String(30), nullable=True)
    contacto = Column(String(120), nullable=True)
    telefono = Column(String(30), nullable=True)
    email = Column(String(120), nullable=True)
    direccion = Column(Text, nullable=True)
    tiempo_entrega_dias = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


# ============================================================
# REPUESTO ↔ PROVEEDOR (N:N)
# ============================================================

class RepuestoProveedor(Base):
    __tablename__ = "repuesto_proveedor"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repuesto_id = Column(UUID(as_uuid=True), ForeignKey("repuestos.id", ondelete="CASCADE"), nullable=False, index=True)
    proveedor_id = Column(UUID(as_uuid=True), ForeignKey("proveedores_repuestos.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo_proveedor = Column(String(60), nullable=True)
    precio_unitario = Column(Numeric(14, 4), nullable=True)
    tiempo_entrega_dias = Column(Integer, nullable=True)
    es_principal = Column(Boolean, default=False, nullable=False)
    fecha_ultima_compra = Column(Date, nullable=True)

    __table_args__ = (
        UniqueConstraint("repuesto_id", "proveedor_id", name="uq_repuesto_proveedor"),
    )


# ============================================================
# COMPATIBILIDAD REPUESTO ↔ EQUIPO
# ============================================================

class RepuestoCompatibilidad(Base):
    __tablename__ = "repuestos_compatibilidad"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repuesto_id = Column(UUID(as_uuid=True), ForeignKey("repuestos.id", ondelete="CASCADE"), nullable=False, index=True)
    equipo_categoria_id = Column(UUID(as_uuid=True), nullable=True)
    equipo_marca = Column(String(100), nullable=True)
    equipo_modelo = Column(String(100), nullable=True)
    equipo_id = Column(UUID(as_uuid=True), ForeignKey("equipos.id", ondelete="CASCADE"), nullable=True)
    notas = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    repuesto = relationship("Repuesto")
    equipo = relationship("Equipo")
