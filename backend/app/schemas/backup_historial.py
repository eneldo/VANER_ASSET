# ============================================================
# SCHEMAS: Backups Inteligentes
# Archivo: backend/app/schemas/backup_historial.py
# ============================================================

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class BackupConfig(BaseModel):
    activo: bool = False
    frecuencia_minutos: int = Field(default=1440, ge=15, le=10080)
    hora: str = "02:00"
    retencion_dias: int = Field(default=15, ge=1, le=365)
    incluir_db: bool = True
    incluir_uploads: bool = True
    incluir_codigo: bool = False


class BackupEjecutarRequest(BaseModel):
    tipo: str = "MANUAL"
    incluir_db: bool = True
    incluir_uploads: bool = True
    incluir_codigo: bool = False
    creado_por: Optional[str] = "admin"


class BackupHistorialOut(BaseModel):
    id: UUID
    tipo: str
    estado: str
    nombre_archivo: Optional[str] = None
    ruta_archivo: Optional[str] = None
    tamano_bytes: int = 0
    mensaje: Optional[str] = None
    incluye_db: bool
    incluye_uploads: bool
    incluye_codigo: bool
    iniciado_en: Optional[datetime] = None
    finalizado_en: Optional[datetime] = None
    creado_por: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class BackupStatusOut(BaseModel):
    ok: bool
    backups_dir: str
    total_backups: int
    total_bytes: int
    ultimo_backup: Optional[BackupHistorialOut] = None
    mensaje: str
