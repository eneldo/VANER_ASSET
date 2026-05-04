# =========================================================
# SCHEMAS: EQUIPO HOJA DE VIDA TÉCNICA
# Todos los campos opcionales deben tener = None
# para evitar errores 422 en FastAPI / Pydantic
# =========================================================

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal


class HojaVidaBase(BaseModel):
    equipo_id: UUID

    adquisicion: Optional[str] = None
    costo: Optional[Decimal] = None
    fecha_compra: Optional[date] = None
    fecha_instalacion: Optional[date] = None
    proveedor: Optional[str] = None
    pais_fabricacion: Optional[str] = None
    fecha_fabricacion: Optional[date] = None
    vida_util: Optional[str] = None
    requiere_calibracion: bool = False

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

    manual_operacion: bool = False
    manual_mantenimiento: bool = False
    manual_partes: bool = False
    manual_despiece: bool = False

    plano_electronico: bool = False
    plano_electrico: bool = False
    plano_neumatico: bool = False
    plano_mecanico: bool = False

    clase_diagnostico: bool = False
    clase_prevencion: bool = False
    clase_rehabilitacion: bool = False
    clase_analisis: bool = False

    riesgo_bajo: bool = False
    riesgo_moderado: bool = False
    riesgo_alto: bool = False
    riesgo_elevado: bool = False


class HojaVidaCreate(HojaVidaBase):
    pass


class HojaVidaUpdate(BaseModel):
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

    clase_diagnostico: Optional[bool] = None
    clase_prevencion: Optional[bool] = None
    clase_rehabilitacion: Optional[bool] = None
    clase_analisis: Optional[bool] = None

    riesgo_bajo: Optional[bool] = None
    riesgo_moderado: Optional[bool] = None
    riesgo_alto: Optional[bool] = None
    riesgo_elevado: Optional[bool] = None


class HojaVidaOut(HojaVidaBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True