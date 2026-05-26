# ============================================================
# SERVICIO: Logs de Automatización
# Archivo: backend/app/services/log_service.py
# ============================================================

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.automatizacion import AutomatizacionLog


def registrar_log_automatizacion(
    db: Session,
    modulo: str,
    evento: str,
    mensaje: str = "",
    nivel: str = "INFO",
    automatizacion_id=None,
    duracion_ms: Optional[int] = None,
    metadata_json: Optional[Dict[str, Any]] = None,
) -> AutomatizacionLog:
    """Registra un evento de automatización sin afectar otros módulos."""

    log = AutomatizacionLog(
        automatizacion_id=automatizacion_id,
        modulo=modulo,
        nivel=nivel,
        evento=evento,
        mensaje=mensaje,
        duracion_ms=duracion_ms,
        metadata_json=metadata_json or {},
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
