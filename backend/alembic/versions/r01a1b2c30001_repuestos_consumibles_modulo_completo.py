"""Repuestos y Consumibles - Módulo completo de inventario

Revision ID: r01a1b2c30001
Revises: p91e4f720001
Create Date: 2026-08-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, NUMERIC

revision = "r01a1b2c30001"
down_revision = "p91e4f720001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Categorías de repuestos
    op.create_table(
        "categorias_repuestos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("empresa_id", UUID(as_uuid=True), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("activo", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("empresa_id", "nombre", name="uq_categoria_repuesto_empresa_nombre"),
    )

    # Unidades de medida
    op.create_table(
        "unidades_medida",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("nombre", sa.String(60), nullable=False, unique=True),
        sa.Column("abreviatura", sa.String(15), nullable=False, unique=True),
        sa.Column("activo", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Insertar unidades de medida básicas
    op.execute("""
        INSERT INTO unidades_medida (nombre, abreviatura, activo) VALUES
        ('Unidad', 'UN', true),
        ('Metro', 'M', true),
        ('Litro', 'L', true),
        ('Kilogramo', 'KG', true),
        ('Juego', 'JG', true),
        ('Par', 'PR', true),
        ('Rollo', 'RL', true),
        ('Galón', 'GL', true),
        ('Caja', 'CJ', true),
        ('Bulto', 'BT', true)
    """)

    # Catálogo maestro de repuestos
    op.create_table(
        "repuestos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("empresa_id", UUID(as_uuid=True), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("codigo", sa.String(60), nullable=False),
        sa.Column("codigo_barras", sa.String(120), nullable=True),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=True),
        sa.Column("tipo", sa.String(20), server_default="REPUESTO", nullable=False),
        sa.Column("categoria_id", UUID(as_uuid=True), sa.ForeignKey("categorias_repuestos.id", ondelete="SET NULL"), nullable=True),
        sa.Column("referencia", sa.String(120), nullable=True),
        sa.Column("marca", sa.String(100), nullable=True),
        sa.Column("fabricante", sa.String(120), nullable=True),
        sa.Column("unidad_medida_id", UUID(as_uuid=True), sa.ForeignKey("unidades_medida.id", ondelete="SET NULL"), nullable=True),
        sa.Column("precio_promedio", NUMERIC(14, 4), nullable=True),
        sa.Column("ultimo_costo", NUMERIC(14, 4), nullable=True),
        sa.Column("stock_minimo", NUMERIC(12, 3), server_default="0"),
        sa.Column("stock_maximo", NUMERIC(12, 3), nullable=True),
        sa.Column("punto_reposicion", NUMERIC(12, 3), nullable=True),
        sa.Column("tiempo_reposicion_dias", sa.Integer, nullable=True),
        sa.Column("maneja_lote", sa.Boolean, server_default="false", nullable=False),
        sa.Column("maneja_serial", sa.Boolean, server_default="false", nullable=False),
        sa.Column("control_vencimiento", sa.Boolean, server_default="false", nullable=False),
        sa.Column("foto_url", sa.Text, nullable=True),
        sa.Column("ficha_tecnica_url", sa.Text, nullable=True),
        sa.Column("activo", sa.Boolean, server_default="true", nullable=False, index=True),
        sa.Column("creado_por", UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("empresa_id", "codigo", name="uq_repuesto_empresa_codigo"),
    )
    op.create_index("ix_repuestos_empresa_nombre", "repuestos", ["empresa_id", "nombre"])

    # Bodegas
    op.create_table(
        "bodegas",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("empresa_id", UUID(as_uuid=True), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sede_id", UUID(as_uuid=True), sa.ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("direccion", sa.Text, nullable=True),
        sa.Column("telefono", sa.String(30), nullable=True),
        sa.Column("responsable_id", UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("activo", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("empresa_id", "nombre", name="uq_bodega_empresa_nombre"),
    )

    # Existencias (stock por repuesto por bodega)
    op.create_table(
        "existencias_repuestos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("empresa_id", UUID(as_uuid=True), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("repuesto_id", UUID(as_uuid=True), sa.ForeignKey("repuestos.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("bodega_id", UUID(as_uuid=True), sa.ForeignKey("bodegas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("existencia_fisica", NUMERIC(12, 3), server_default="0", nullable=False),
        sa.Column("cantidad_reservada", NUMERIC(12, 3), server_default="0", nullable=False),
        sa.Column("costo_promedio", NUMERIC(14, 4), nullable=True),
        sa.Column("ultimo_costo", NUMERIC(14, 4), nullable=True),
        sa.Column("lote", sa.String(60), nullable=True),
        sa.Column("serial", sa.String(60), nullable=True),
        sa.Column("fecha_vencimiento", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint("repuesto_id", "bodega_id", "lote", "serial", name="uq_existencia_repuesto_bodega_lote_serial"),
        sa.CheckConstraint("existencia_fisica >= 0", name="ck_existencia_fisica_no_negativa"),
        sa.CheckConstraint("cantidad_reservada >= 0", name="ck_cantidad_reservada_no_negativa"),
    )
    op.create_index("ix_existencias_empresa", "existencias_repuestos", ["empresa_id"])

    # Movimientos de inventario (inmutables)
    op.create_table(
        "movimientos_repuestos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("empresa_id", UUID(as_uuid=True), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("repuesto_id", UUID(as_uuid=True), sa.ForeignKey("repuestos.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("bodega_origen_id", UUID(as_uuid=True), sa.ForeignKey("bodegas.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bodega_destino_id", UUID(as_uuid=True), sa.ForeignKey("bodegas.id", ondelete="SET NULL"), nullable=True),
        sa.Column("tipo_movimiento", sa.String(30), nullable=False),
        sa.Column("cantidad", NUMERIC(12, 3), nullable=False),
        sa.Column("unidad", sa.String(30), server_default="UNIDAD", nullable=False),
        sa.Column("costo_unitario", NUMERIC(14, 4), nullable=True),
        sa.Column("costo_total", NUMERIC(14, 4), nullable=True),
        sa.Column("existencia_anterior", NUMERIC(12, 3), nullable=True),
        sa.Column("existencia_posterior", NUMERIC(12, 3), nullable=True),
        sa.Column("mantenimiento_id", UUID(as_uuid=True), sa.ForeignKey("mantenimientos.id", ondelete="SET NULL"), nullable=True),
        sa.Column("solicitud_id", UUID(as_uuid=True), nullable=True),
        sa.Column("documento", sa.String(120), nullable=True),
        sa.Column("motivo", sa.Text, nullable=True),
        sa.Column("idempotency_key", sa.String(120), nullable=True, unique=True),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_movimientos_empresa_fecha", "movimientos_repuestos", ["empresa_id", "created_at"])
    op.create_index("ix_movimientos_repuesto", "movimientos_repuestos", ["repuesto_id"])

    # Solicitudes de repuestos
    op.create_table(
        "solicitudes_repuestos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("empresa_id", UUID(as_uuid=True), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("mantenimiento_id", UUID(as_uuid=True), sa.ForeignKey("mantenimientos.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("repuesto_id", UUID(as_uuid=True), sa.ForeignKey("repuestos.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("bodega_id", UUID(as_uuid=True), sa.ForeignKey("bodegas.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cantidad_solicitada", NUMERIC(12, 3), nullable=False),
        sa.Column("cantidad_aprobada", NUMERIC(12, 3), nullable=True),
        sa.Column("cantidad_entregada", NUMERIC(12, 3), nullable=True),
        sa.Column("cantidad_devuelta", NUMERIC(12, 3), nullable=True),
        sa.Column("estado", sa.String(30), server_default="SOLICITADO", nullable=False),
        sa.Column("observaciones", sa.Text, nullable=True),
        sa.Column("solicitado_por", UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("autorizado_por", UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("entregado_por", UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_solicitudes_empresa_estado", "solicitudes_repuestos", ["empresa_id", "estado"])

    # Proveedores
    op.create_table(
        "proveedores_repuestos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("empresa_id", UUID(as_uuid=True), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("nit", sa.String(30), nullable=True),
        sa.Column("contacto", sa.String(120), nullable=True),
        sa.Column("telefono", sa.String(30), nullable=True),
        sa.Column("email", sa.String(120), nullable=True),
        sa.Column("direccion", sa.Text, nullable=True),
        sa.Column("tiempo_entrega_dias", sa.Integer, nullable=True),
        sa.Column("activo", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Relación repuesto ↔ proveedor
    op.create_table(
        "repuesto_proveedor",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("repuesto_id", UUID(as_uuid=True), sa.ForeignKey("repuestos.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("proveedor_id", UUID(as_uuid=True), sa.ForeignKey("proveedores_repuestos.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("codigo_proveedor", sa.String(60), nullable=True),
        sa.Column("precio_unitario", NUMERIC(14, 4), nullable=True),
        sa.Column("tiempo_entrega_dias", sa.Integer, nullable=True),
        sa.Column("es_principal", sa.Boolean, server_default="false", nullable=False),
        sa.Column("fecha_ultima_compra", sa.Date, nullable=True),
        sa.UniqueConstraint("repuesto_id", "proveedor_id", name="uq_repuesto_proveedor"),
    )

    # Compatibilidad repuesto ↔ equipo
    op.create_table(
        "repuestos_compatibilidad",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("repuesto_id", UUID(as_uuid=True), sa.ForeignKey("repuestos.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("equipo_categoria_id", UUID(as_uuid=True), nullable=True),
        sa.Column("equipo_marca", sa.String(100), nullable=True),
        sa.Column("equipo_modelo", sa.String(100), nullable=True),
        sa.Column("equipo_id", UUID(as_uuid=True), sa.ForeignKey("equipos.id", ondelete="CASCADE"), nullable=True),
        sa.Column("notas", sa.Text, nullable=True),
        sa.Column("activo", sa.Boolean, server_default="true", nullable=False),
    )

    # Agregar columnas a ot_repuestos para vincular con catálogo
    op.add_column("ot_repuestos", sa.Column("repuesto_id", UUID(as_uuid=True), sa.ForeignKey("repuestos.id", ondelete="SET NULL"), nullable=True))
    op.add_column("ot_repuestos", sa.Column("bodega_id", UUID(as_uuid=True), sa.ForeignKey("bodegas.id", ondelete="SET NULL"), nullable=True))
    op.add_column("ot_repuestos", sa.Column("solicitud_id", UUID(as_uuid=True), nullable=True))


def downgrade() -> None:
    op.drop_table("repuestos_compatibilidad")
    op.drop_table("repuesto_proveedor")
    op.drop_table("proveedores_repuestos")
    op.drop_table("solicitudes_repuestos")
    op.drop_index("ix_movimientos_repuesto", "movimientos_repuestos")
    op.drop_index("ix_movimientos_empresa_fecha", "movimientos_repuestos")
    op.drop_table("movimientos_repuestos")
    op.drop_table("existencias_repuestos")
    op.drop_table("bodegas")
    op.drop_index("ix_repuestos_empresa_nombre", "repuestos")
    op.drop_table("repuestos")
    op.drop_table("unidades_medida")
    op.drop_table("categorias_repuestos")
