# ============================================================
# SERVICIO RECOVERY PRO
# ============================================================

import os
from datetime import datetime

from app.utils.backup_utils import (
    generar_backup,
    restaurar_backup,
    BACKUP_DIR
)


class RecoveryService:

    @staticmethod
    def crear_backup():

        ruta = generar_backup()

        archivo = os.path.basename(ruta)

        tamaño = os.path.getsize(ruta) / (1024 * 1024)

        return {
            "nombre": archivo,
            "ruta": ruta,
            "tamaño_mb": round(tamaño, 2),
            "fecha": datetime.now()
        }

    @staticmethod
    def listar_backups():

        backups = []

        archivos = sorted(
            os.listdir(BACKUP_DIR),
            reverse=True
        )

        for archivo in archivos:

            ruta = os.path.join(BACKUP_DIR, archivo)

            if os.path.isfile(ruta):

                tamaño = os.path.getsize(ruta) / (1024 * 1024)

                fecha = datetime.fromtimestamp(
                    os.path.getmtime(ruta)
                )

                backups.append({
                    "nombre": archivo,
                    "ruta": ruta,
                    "tamaño_mb": round(tamaño, 2),
                    "fecha": fecha
                })

        return backups

    @staticmethod
    def ejecutar_restore(nombre_backup):

        restaurar_backup(nombre_backup)

        return {
            "success": True,
            "mensaje": "Backup restaurado correctamente"
        }

    @staticmethod
    def estado_sistema():

        backups = RecoveryService.listar_backups()

        ultimo = backups[0]["nombre"] if backups else None

        return {
            "postgres": True,
            "backups_totales": len(backups),
            "ultimo_backup": ultimo
        }