"""
===========================================================
SCHEMA EVIDENCIA PRO
===========================================================
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EvidenciaResponse(BaseModel):

    id: str
    mantenimiento_id: str

    nombre_original: Optional[str]
    archivo_url: Optional[str]
    tipo: Optional[str]

    created_at: datetime

    class Config:
        from_attributes = True