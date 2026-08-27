# ============================================================
# SCHEMAS: Repuestos y Consumibles
# ============================================================

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel


# ============================================================
# CATEGORÍAS
# ============================================================

class CategoriaRepuestoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaRepuestoCreate(CategoriaRepuestoBase):
    pass

class CategoriaRepuestoOut(CategoriaRepuestoBase):
    id: str
    empresa_id: str
    activo: bool
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ============================================================
# UNIDADES DE MEDIDA
# ============================================================

class UnidadMedidaBase(BaseModel):
    nombre: str
    abreviatura: str

class UnidadMedidaCreate(UnidadMedidaBase):
    pass

class UnidadMedidaOut(UnidadMedidaBase):
    id: str
    activo: bool
    class Config:
        from_attributes = True


# ============================================================
# REPUESTOS (CATÁLOGO)
# ============================================================

class RepuestoBase(BaseModel):
    codigo: str
    codigo_barras: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    tipo: str = "REPUESTO"
    categoria_id: Optional[str] = None
    referencia: Optional[str] = None
    marca: Optional[str] = None
    fabricante: Optional[str] = None
    unidad_medida_id: Optional[str] = None
    precio_promedio: Optional[Decimal] = None
    ultimo_costo: Optional[Decimal] = None
    stock_minimo: Optional[Decimal] = None
    stock_maximo: Optional[Decimal] = None
    punto_reposicion: Optional[Decimal] = None
    tiempo_reposicion_dias: Optional[int] = None
    maneja_lote: bool = False
    maneja_serial: bool = False
    control_vencimiento: bool = False
    foto_url: Optional[str] = None
    ficha_tecnica_url: Optional[str] = None

class RepuestoCreate(RepuestoBase):
    pass

class RepuestoUpdate(BaseModel):
    codigo: Optional[str] = None
    codigo_barras: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    categoria_id: Optional[str] = None
    referencia: Optional[str] = None
    marca: Optional[str] = None
    fabricante: Optional[str] = None
    unidad_medida_id: Optional[str] = None
    precio_promedio: Optional[Decimal] = None
    ultimo_costo: Optional[Decimal] = None
    stock_minimo: Optional[Decimal] = None
    stock_maximo: Optional[Decimal] = None
    punto_reposicion: Optional[Decimal] = None
    tiempo_reposicion_dias: Optional[int] = None
    maneja_lote: Optional[bool] = None
    maneja_serial: Optional[bool] = None
    control_vencimiento: Optional[bool] = None
    foto_url: Optional[str] = None
    ficha_tecnica_url: Optional[str] = None
    activo: Optional[bool] = None

class RepuestoOut(RepuestoBase):
    id: str
    empresa_id: str
    activo: bool
    creado_por: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ============================================================
# BODEGAS
# ============================================================

class BodegaBase(BaseModel):
    nombre: str
    sede_id: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    responsable_id: Optional[str] = None

class BodegaCreate(BodegaBase):
    pass

class BodegaUpdate(BaseModel):
    nombre: Optional[str] = None
    sede_id: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    responsable_id: Optional[str] = None
    activo: Optional[bool] = None

class BodegaOut(BodegaBase):
    id: str
    empresa_id: str
    activo: bool
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ============================================================
# EXISTENCIAS
# ============================================================

class ExistenciaOut(BaseModel):
    id: str
    empresa_id: str
    repuesto_id: str
    bodega_id: str
    existencia_fisica: Decimal
    cantidad_reservada: Decimal
    costo_promedio: Optional[Decimal] = None
    ultimo_costo: Optional[Decimal] = None
    lote: Optional[str] = None
    serial: Optional[str] = None
    fecha_vencimiento: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ============================================================
# MOVIMIENTOS
# ============================================================

class MovimientoCreate(BaseModel):
    repuesto_id: str
    bodega_origen_id: Optional[str] = None
    bodega_destino_id: Optional[str] = None
    tipo_movimiento: str
    cantidad: Decimal
    unidad: str = "UNIDAD"
    costo_unitario: Optional[Decimal] = None
    mantenimiento_id: Optional[str] = None
    documento: Optional[str] = None
    motivo: Optional[str] = None
    idempotency_key: Optional[str] = None

class MovimientoOut(BaseModel):
    id: str
    empresa_id: str
    repuesto_id: str
    bodega_origen_id: Optional[str] = None
    bodega_destino_id: Optional[str] = None
    tipo_movimiento: str
    cantidad: Decimal
    unidad: str
    costo_unitario: Optional[Decimal] = None
    costo_total: Optional[Decimal] = None
    existencia_anterior: Optional[Decimal] = None
    existencia_posterior: Optional[Decimal] = None
    mantenimiento_id: Optional[str] = None
    documento: Optional[str] = None
    motivo: Optional[str] = None
    usuario_id: Optional[str] = None
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ============================================================
# SOLICITUDES
# ============================================================

class SolicitudCreate(BaseModel):
    mantenimiento_id: str
    repuesto_id: str
    bodega_id: Optional[str] = None
    cantidad_solicitada: Decimal
    observaciones: Optional[str] = None

class SolicitudUpdate(BaseModel):
    cantidad_aprobada: Optional[Decimal] = None
    estado: Optional[str] = None
    observaciones: Optional[str] = None
    bodega_id: Optional[str] = None

class SolicitudOut(BaseModel):
    id: str
    empresa_id: str
    mantenimiento_id: str
    repuesto_id: str
    bodega_id: Optional[str] = None
    cantidad_solicitada: Decimal
    cantidad_aprobada: Optional[Decimal] = None
    cantidad_entregada: Optional[Decimal] = None
    cantidad_devuelta: Optional[Decimal] = None
    estado: str
    observaciones: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ============================================================
# PROVEEDORES
# ============================================================

class ProveedorBase(BaseModel):
    nombre: str
    nit: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    tiempo_entrega_dias: Optional[int] = None

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    nit: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    tiempo_entrega_dias: Optional[int] = None
    activo: Optional[bool] = None

class ProveedorOut(ProveedorBase):
    id: str
    empresa_id: str
    activo: bool
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True


# ============================================================
# COMPATIBILIDAD
# ============================================================

class CompatibilidadCreate(BaseModel):
    repuesto_id: str
    equipo_categoria_id: Optional[str] = None
    equipo_marca: Optional[str] = None
    equipo_modelo: Optional[str] = None
    equipo_id: Optional[str] = None
    notas: Optional[str] = None

class CompatibilidadOut(BaseModel):
    id: str
    repuesto_id: str
    equipo_categoria_id: Optional[str] = None
    equipo_marca: Optional[str] = None
    equipo_modelo: Optional[str] = None
    equipo_id: Optional[str] = None
    notas: Optional[str] = None
    activo: bool
    class Config:
        from_attributes = True


# ============================================================
# DASHBOARD / INDICADORES
# ============================================================

class DashboardRepuestos(BaseModel):
    total_repuestos_activos: int
    total_unidades_disponibles: Decimal
    repuestos_stock_bajo: int
    repuestos_agotados: int
    valor_inventario: Decimal
    solicitudes_pendientes: int
    reservas_pendientes: int
    entregas_periodo: int
    ordenes_detenidas: int
