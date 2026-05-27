# ============================================================
# SCHEMAS MONITOR VPS + POSTGRESQL PRO
# Archivo: backend/app/schemas/monitor_vps.py
# ============================================================

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class MonitorResponse(BaseModel):
    ok: bool = True
    timestamp: Optional[str] = None
    data: Dict[str, Any] | None = None


class MonitorResumenResponse(BaseModel):
    ok: bool = True
    timestamp: str | None = None
    estado_general: str | None = None
    alertas: List[str] = []
    vps: Dict[str, Any] = {}
    postgresql: Dict[str, Any] = {}
    docker: Dict[str, Any] = {}
