# ============================================================
# SERVICIO: Backups configurables
# Archivo: backend/app/services/backup_service.py
# Fase 34.1 - Configuración Inteligente SaaS PRO
# ============================================================

from datetime import datetime
from pathlib import Path
from typing import Dict
import json


def create_backup_marker(backup_config: Dict) -> Dict:
    """
    Crea un archivo marcador de backup.

    Nota profesional:
    - Este servicio deja lista la estructura para backups automáticos reales.
    - En producción se recomienda conectar pg_dump desde Docker/Cron o Celery Beat.
    - Por seguridad no ejecutamos comandos del sistema aquí sin validar rutas/credenciales.
    """

    backup_dir = Path(backup_config.get("ruta_destino") or "app/exports/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    marker_file = backup_dir / f"backup_configurado_{timestamp}.json"

    payload = {
        "timestamp": timestamp,
        "estado": "CONFIGURADO",
        "mensaje": "Backup automático configurado. Conectar pg_dump/Cron/Celery para ejecución real en servidor.",
        "configuracion": backup_config,
    }

    marker_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "archivo": str(marker_file),
        "timestamp": timestamp,
    }
