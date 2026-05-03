# =========================================================
# SCHEMAS HOJA DE VIDA TÉCNICA
# Validan el PASO 2 de datos técnicos del equipo
# =========================================================

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


class HojaVidaBase(BaseModel):
    # Equipo asociado
    equipo_id: UUID

    # =====================================================
    # REGISTRO HISTÓRICO
    # =====================================================

    adquisicion: Optional[str] = None
    costo: Optional[Decimal] = None
    fecha_compra: Optional[date] = None
    fecha_instalacion: Optional[date] = None
    proveedor: Optional[str] = None
    pais_fabricacion: Optional[str] = None
    fecha_fabricacion: Optional[date] = None
    vida_util: Optional[str] = None
    requiere_calibracion: bool = False

    # =====================================================
    # REGISTRO TÉCNICO DE FUNCIONAMIENTO
    # =====================================================

    rango_voltaje: Optional[str] = None
    rango_presion: Optional[str] = None
    gas_refrigerante: Optional[str] = None
    capacidad: Optional[str] = None
    rango_corriente: Optional[str] = None
    rango_velocidad: Optional[str] = None
    rango_potencia: Optional[str] = None
    rango_temperatura: Optional[str] = None
    frecuencia: Optional[str] = None
    rango_humedad: Optional[str] = None
    otros: Optional[str] = None

    # =====================================================
    # REGISTRO DE APOYO TÉCNICO
    # =====================================================

    manual_operacion: bool = False
    manual_mantenimiento: bool = False
    manual_partes: bool = False
    manual_despiece: bool = False

    plano_electronico: bool = False
    plano_electrico: bool = False
    plano_neumatico: bool = False
    plano_mecanico: bool = False

    # =====================================================
    # CLASIFICACIÓN Y MANTENIMIENTO
    # =====================================================

    clasificacion_biomedica: Optional[str] = None
    clasificacion_riesgo: Optional[str] = None
    periodicidad_mantenimiento: Optional[str] = None
    periodo_calibracion: Optional[str] = None

    # =====================================================
    # DOCUMENTOS ANEXOS
    # =====================================================

    doc_registro_sanitario: bool = False
    doc_factura: bool = False
    doc_protocolo_mantenimiento: bool = False
    doc_permiso_comercializacion: bool = False
    doc_ingreso_almacen: bool = False
    doc_cronograma_garantia: bool = False
    doc_registro_importacion: bool = False
    doc_guia_rapida: bool = False


class HojaVidaCreate(HojaVidaBase):
    # Schema para crear hoja de vida técnica
    pass


class HojaVidaUpdate(BaseModel):
    # =====================================================
    # UPDATE PARCIAL
    # No obliga a enviar todos los campos
    # =====================================================

    adquisicion: Optional[str] = None
    costo: Optional[Decimal] = None
    fecha_compra: Optional[date] = None
    fecha_instalacion: Optional[date] = None
    proveedor: Optional[str] = None
    pais_fabricacion: Optional[str] = None
    fecha_fabricacion: Optional[date] = None
    vida_util: Optional[str] = None
    requiere_calibracion: Optional[bool] = None

    rango_voltaje: Optional[str] = None
    rango_presion: Optional[str] = None
    gas_refrigerante: Optional[str] = None
    capacidad: Optional[str] = None
    rango_corriente: Optional[str] = None
    rango_velocidad: Optional[str] = None
    rango_potencia: Optional[str] = None
    rango_temperatura: Optional[str] = None
    frecuencia: Optional[str] = None
    rango_humedad: Optional[str] = None
    otros: Optional[str] = None

    manual_operacion: Optional[bool] = None
    manual_mantenimiento: Optional[bool] = None
    manual_partes: Optional[bool] = None
    manual_despiece: Optional[bool] = None

    plano_electronico: Optional[bool] = None
    plano_electrico: Optional[bool] = None
    plano_neumatico: Optional[bool] = None
    plano_mecanico: Optional[bool] = None

    clasificacion_biomedica: Optional[str] = None
    clasificacion_riesgo: Optional[str] = None
    periodicidad_mantenimiento: Optional[str] = None
    periodo_calibracion: Optional[str] = None

    doc_registro_sanitario: Optional[bool] = None
    doc_factura: Optional[bool] = None
    doc_protocolo_mantenimiento: Optional[bool] = None
    doc_permiso_comercializacion: Optional[bool] = None
    doc_ingreso_almacen: Optional[bool] = None
    doc_cronograma_garantia: Optional[bool] = None
    doc_registro_importacion: Optional[bool] = None
    doc_guia_rapida: Optional[bool] = None


class HojaVidaOut(HojaVidaBase):
    # Respuesta completa de hoja de vida
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True