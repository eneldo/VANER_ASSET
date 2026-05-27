# ============================================================
# SCHEMAS - RECOVERY & RESTORE PRO
# ============================================================

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BackupResponse(BaseModel):
    nombre: str
    ruta: str
    tamaño_mb: float
    fecha: datetime


class RestoreRequest(BaseModel):
    archivo_backup: str


class SystemStatusResponse(BaseModel):
    postgres: bool
    backups_totales: int
    ultimo_backup: Optional[str]