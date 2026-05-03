# =========================================================
# SCHEMAS EVIDENCIA
# Validan la salida de evidencias
# =========================================================

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class EvidenciaOut(BaseModel):
    # Identificador de la evidencia
    id: UUID

    # Mantenimiento asociado
    mantenimiento_id: UUID

    # Tipo: ANTES, DURANTE, DESPUES
    tipo: str

    # Ruta pública del archivo
    archivo_url: str

    # Nombre original
    nombre_original: Optional[str] = None

    # Descripción
    descripcion: Optional[str] = None

    # Fecha de carga
    created_at: datetime

    class Config:
        from_attributes = True