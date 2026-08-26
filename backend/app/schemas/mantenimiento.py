# ============================================================
# SCHEMAS: Mantenimientos PRO
# Archivo: app/schemas/mantenimiento.py
# Proyecto: SGA Empresarial
# Fase 18.2 / 18.3
#
# IMPORTANTE:
# Tu base de datos está usando UUID en los IDs.
# Por eso en los schemas usamos str para:
#   - id
#   - equipo_id
#   - tecnico_id
#   - mantenimiento_id
#
# Esto evita errores tipo:
# ResponseValidationError: Input should be a valid integer
# ============================================================

from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel


# ============================================================
# BASE GENERAL DEL MANTENIMIENTO
# Se usa como base para crear mantenimientos.
# ============================================================

class MantenimientoBase(BaseModel):
    equipo_id: str
    tipo: str
    descripcion: Optional[str] = None
    prioridad: Optional[str] = "MEDIA"

    fecha_programada: Optional[datetime] = None
    fecha_inicio_programada: Optional[datetime] = None
    fecha_fin_programada: Optional[datetime] = None

    observaciones: Optional[str] = None
    estado_inicial_equipo: Optional[str] = None
    acciones_realizadas: Optional[str] = None
    resultado_final: Optional[str] = None
    latitud: Optional[str] = None
    longitud: Optional[str] = None

    falla_incidencia: Optional[str] = None
    diagnostico: Optional[str] = None
    trabajo_realizado: Optional[str] = None
    repuestos: Optional[list] = None

    costo: Optional[Decimal] = None
    costo_mano_obra: Optional[Decimal] = None
    costo_repuestos: Optional[Decimal] = None
    costo_total: Optional[Decimal] = None

    evidencia_fotos: Optional[list] = None
    evidencia_documentos: Optional[list] = None

    solucion: Optional[str] = None
    cerrado: Optional[bool] = False
    responsable_id: Optional[str] = None

    tipo_movimiento: Optional[str] = None
    activo_afectado_id: Optional[str] = None
    activo_afectado_tipo: Optional[str] = None


# ============================================================
# CREAR MANTENIMIENTO
# Payload usado por POST /mantenimientos/
# ============================================================

class MantenimientoCreate(MantenimientoBase):
    pass


# ============================================================
# ACTUALIZAR MANTENIMIENTO
# Payload usado por PUT /mantenimientos/{id}
# Todos los campos son opcionales para permitir edición parcial.
# ============================================================

class MantenimientoUpdate(BaseModel):
    equipo_id: Optional[str] = None
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    fecha_programada: Optional[datetime] = None
    fecha_inicio_programada: Optional[datetime] = None
    fecha_fin_programada: Optional[datetime] = None
    observaciones: Optional[str] = None
    estado_inicial_equipo: Optional[str] = None
    acciones_realizadas: Optional[str] = None
    resultado_final: Optional[str] = None
    latitud: Optional[str] = None
    longitud: Optional[str] = None
    falla_incidencia: Optional[str] = None
    diagnostico: Optional[str] = None
    trabajo_realizado: Optional[str] = None
    repuestos: Optional[list] = None
    costo: Optional[Decimal] = None
    costo_mano_obra: Optional[Decimal] = None
    costo_repuestos: Optional[Decimal] = None
    costo_total: Optional[Decimal] = None
    evidencia_fotos: Optional[list] = None
    evidencia_documentos: Optional[list] = None
    solucion: Optional[str] = None
    cerrado: Optional[bool] = None
    responsable_id: Optional[str] = None
    tipo_movimiento: Optional[str] = None
    activo_afectado_id: Optional[str] = None
    activo_afectado_tipo: Optional[str] = None


# ============================================================
# ASIGNAR TÉCNICO
# Payload usado por:
# PATCH /mantenimientos/{id}/asignar-tecnico
# ============================================================

class AsignarTecnicoRequest(BaseModel):
    # ID del técnico.
    # En tu BD también viene como UUID, por eso es str.
    tecnico_id: str

    # Observación opcional de asignación.
    observacion: Optional[str] = "Técnico asignado al mantenimiento."

    # Usuario que realiza la acción.
    creado_por: Optional[str] = "Sistema"


# ============================================================
# CAMBIAR ESTADO
# Payload usado por:
# PATCH /mantenimientos/{id}/cambiar-estado
# ============================================================

class CambiarEstadoRequest(BaseModel):
    # Estado nuevo:
    # PROGRAMADO, ASIGNADO, EN_PROCESO, PAUSADO, FINALIZADO, ANULADO.
    estado_nuevo: str

    # Observación o motivo del cambio.
    observacion: Optional[str] = None

    # Usuario que realiza el cambio.
    creado_por: Optional[str] = "Sistema"


# ============================================================
# SALIDA DEL HISTORIAL
# Response usado por GET /mantenimientos/{id}/historial
# ============================================================

class HistMantenimientoOut(BaseModel):
    # ID del registro histórico.
    id: str

    # ID del mantenimiento relacionado.
    mantenimiento_id: str

    # Estado anterior.
    estado_anterior: Optional[str] = None

    # Estado nuevo.
    estado_nuevo: str

    # Técnico relacionado al evento.
    tecnico_id: Optional[str] = None

    # Observación registrada.
    observacion: Optional[str] = None

    # Usuario que realizó el cambio.
    creado_por: Optional[str] = None

    # Fecha del evento.
    fecha_evento: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# SALIDA PRINCIPAL DEL MANTENIMIENTO
# Response usado por:
# GET /mantenimientos/
# GET /mantenimientos/{id}
# POST /mantenimientos/
# PUT /mantenimientos/{id}
# PATCH /mantenimientos/{id}/...
# ============================================================

class MantenimientoOut(BaseModel):
    id: str
    equipo_id: str
    tipo: str
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    fecha_programada: Optional[datetime] = None
    estado: str
    tecnico_id: Optional[str] = None
    responsable_id: Optional[str] = None

    fecha_asignacion: Optional[datetime] = None
    fecha_inicio: Optional[datetime] = None
    fecha_pausa: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None

    observaciones: Optional[str] = None
    observacion_estado: Optional[str] = None
    motivo_anulacion: Optional[str] = None

    falla_incidencia: Optional[str] = None
    diagnostico: Optional[str] = None
    trabajo_realizado: Optional[str] = None
    repuestos: Optional[list] = None

    costo: Optional[Decimal] = None
    costo_mano_obra: Optional[Decimal] = None
    costo_repuestos: Optional[Decimal] = None
    costo_total: Optional[Decimal] = None

    evidencia_fotos: Optional[list] = None
    evidencia_documentos: Optional[list] = None

    solucion: Optional[str] = None
    cerrado: Optional[bool] = None
    fecha_cierre: Optional[datetime] = None

    tipo_movimiento: Optional[str] = None
    activo_afectado_id: Optional[str] = None
    activo_afectado_tipo: Optional[str] = None

    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# SALIDA DETALLADA CON HISTORIAL
# Response usado por GET /mantenimientos/{id}
# ============================================================

class MantenimientoDetalleOut(MantenimientoOut):
    historial: List[HistMantenimientoOut] = []
