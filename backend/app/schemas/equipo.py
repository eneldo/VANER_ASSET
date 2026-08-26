# =========================================================
# SCHEMAS EQUIPO
# Validan datos básicos del equipo - PASO 1
# Incluye control de movimientos FASE 7
# =========================================================

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class EquipoBase(BaseModel):
    # Relaciones principales
    empresa_id: UUID
    sede_id: UUID
    categoria_id: UUID

    # Datos básicos del equipo
    nombre: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    ubicacion: Optional[str] = None
    invima: Optional[str] = None
    codigo_id: Optional[str] = None
    inventario: Optional[str] = None

    # Estado y criticidad
    estado: str = "OPERATIVO"
    criticidad: str = "MEDIA"
    responsable_id: Optional[UUID] = None
    vida_util_meses: Optional[int] = Field(None, gt=0)

    # Estado lógico
    activo: bool = True


class EquipoCreate(EquipoBase):
    # Schema para crear equipo básico
    pass


class EquipoUpdate(BaseModel):
    # Schema para actualizar parcialmente el equipo
    empresa_id: Optional[UUID] = None
    sede_id: Optional[UUID] = None
    categoria_id: Optional[UUID] = None

    nombre: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    ubicacion: Optional[str] = None
    invima: Optional[str] = None
    codigo_id: Optional[str] = None
    inventario: Optional[str] = None

    estado: Optional[str] = None
    criticidad: Optional[str] = None
    responsable_id: Optional[UUID] = None
    vida_util_meses: Optional[int] = Field(None, gt=0)
    activo: Optional[bool] = None


class EquipoOut(EquipoBase):
    # Respuesta completa de equipo
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    responsable_id: Optional[UUID] = None
    vida_util_meses: Optional[int] = None
    historial_cambios: Optional[list] = None

    class Config:
        from_attributes = True


# =========================================================
# ESQUEMAS MOVIMIENTOS EQUIPO - FASE 7
# =========================================================

TIPOS_MOVIMIENTO = [
    "ASIGNACION",
    "DEVOLUCION",
    "TRANSFERENCIA",
    "BAJA"
]

ESTADOS_EQUIPO = [
    "OPERATIVO",
    "EN_MANTENIMIENTO",
    "FUERA_DE_SERVICIO",
    "BAJA"
]


class EquipoMovimientoBase(BaseModel):
    usuario_id: Optional[UUID] = Field(None, description="ID legado del usuario que realiza la acción")
    observacion: Optional[str] = Field(None, description="Observaciones del movimiento")


class EquipoAsignar(EquipoMovimientoBase):
    """Asignar equipo a un responsable"""
    responsable_id: UUID = Field(..., description="ID del nuevo responsable")
    ubicacion: Optional[str] = Field(None, description="Nueva ubicación del equipo")


class EquipoDevolver(EquipoMovimientoBase):
    """Devolver equipo (liberar responsable)"""
    ubicacion: Optional[str] = Field(None, description="Ubicación donde se devuelve")


class EquipoTransferir(EquipoMovimientoBase):
    """Transferir equipo entre sedes/áreas/responsables"""
    nuevo_responsable_id: Optional[UUID] = Field(None, description="Nuevo responsable (opcional)")
    nueva_sede_id: Optional[UUID] = Field(None, description="Nueva sede (opcional)")
    nueva_ubicacion: Optional[str] = Field(None, description="Nueva ubicación (opcional)")


class EquipoBaja(EquipoMovimientoBase):
    """Dar de baja un equipo"""
    motivo: str = Field(..., description="Motivo de la baja")
    estado_final: str = Field(default="BAJA", description="Estado final: BAJA o FUERA_DE_SERVICIO")


class EquipoHistorialItem(BaseModel):
    """Item individual del historial de cambios"""
    timestamp: datetime
    campo: str
    anterior: Optional[str] = None
    nuevo: Optional[str] = None
    usuario_id: Optional[str] = None
    tipo_movimiento: Optional[str] = None
    observacion: Optional[str] = None


class EquipoHistorialOut(BaseModel):
    """Respuesta completa con historial de movimientos"""
    id: UUID
    nombre: str
    estado: str
    responsable_id: Optional[UUID] = None
    ubicacion: Optional[str] = None
    vida_util_meses: Optional[int] = None
    historial_cambios: List[EquipoHistorialItem] = []

    class Config:
        from_attributes = True
