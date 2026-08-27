#!/usr/bin/env python3
"""
VANER ASSET — Inicializar automatización de backups
Crea o actualiza el registro de automatización para backups
con frecuencia diaria (1440 minutos).

Uso:
    python scripts/init_backup_automation.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal
from app.models.automatizacion import Automatizacion


def init_backup_automation():
    db = SessionLocal()
    try:
        # Buscar o crear automatización de backups
        auto = db.query(Automatizacion).filter(
            Automatizacion.modulo == "backups"
        ).first()

        if auto:
            auto.activo = True
            auto.frecuencia_minutos = 1440  # 24 horas
            auto.nombre = "Backup Automático"
            print(f"Actualizando automatización de backups existente: {auto.id}")
        else:
            auto = Automatizacion(
                modulo="backups",
                nombre="Backup Automático",
                activo=True,
                frecuencia_minutos=1440,
                config_json={
                    "incluir_db": True,
                    "incluir_uploads": True,
                    "incluir_codigo": False,
                    "retention_days": 30,
                },
            )
            db.add(auto)
            print("Creando nueva automatización de backups")

        db.commit()
        print("✓ Automatización de backups inicializada (frecuencia: 24h)")
        print("  El scheduler ejecutará backups automáticos al iniciar el backend")

    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    init_backup_automation()
