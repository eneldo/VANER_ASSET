# ============================================================
# UTILIDADES BACKUP PRO
# ============================================================

import os
import subprocess
from datetime import datetime

BACKUP_DIR = "app/backups/postgres"

os.makedirs(BACKUP_DIR, exist_ok=True)


def generar_backup():
    """
    Genera backup PostgreSQL usando pg_dump
    """

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    archivo = f"sga_backup_{fecha}.sql"

    ruta = os.path.join(BACKUP_DIR, archivo)

    db_name = os.getenv("POSTGRES_DB", "sga_pro")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("POSTGRES_HOST", "localhost")

    comando = [
        "pg_dump",
        "-h",
        db_host,
        "-U",
        db_user,
        "-F",
        "p",
        "-f",
        ruta,
        db_name
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    subprocess.run(
        comando,
        env=env,
        check=True
    )

    return ruta


def restaurar_backup(archivo_backup):
    """
    Restaura backup PostgreSQL
    """

    db_name = os.getenv("POSTGRES_DB", "sga_pro")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("POSTGRES_HOST", "localhost")

    ruta = os.path.join(BACKUP_DIR, archivo_backup)

    if not os.path.exists(ruta):
        raise Exception("Backup no encontrado")

    comando = [
        "psql",
        "-h",
        db_host,
        "-U",
        db_user,
        "-d",
        db_name,
        "-f",
        ruta
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    subprocess.run(
        comando,
        env=env,
        check=True
    )

    return True