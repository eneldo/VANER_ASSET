# ============================================================
# UTILIDADES BACKUP PRO
# ============================================================

import os
import subprocess
from datetime import datetime
from pathlib import Path

BACKUP_DIR = (Path(os.getenv("BACKUP_DIR") or "app/backups").resolve() / "postgres")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def _required_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise RuntimeError(f"Falta la variable obligatoria {name}")
    return value


def _database_settings() -> tuple[str, str, str, str]:
    return (
        _required_env("POSTGRES_DB"),
        _required_env("POSTGRES_USER"),
        _required_env("POSTGRES_PASSWORD"),
        _required_env("POSTGRES_HOST"),
    )


def _safe_backup_path(filename: str) -> Path:
    safe_name = Path(filename or "").name
    if safe_name != filename or not safe_name.lower().endswith(".sql"):
        raise ValueError("Nombre de backup inválido")

    path = (BACKUP_DIR / safe_name).resolve()
    if path.parent != BACKUP_DIR:
        raise ValueError("Ruta de backup inválida")
    return path


def generar_backup():
    """
    Genera backup PostgreSQL usando pg_dump
    """

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    archivo = f"sga_backup_{fecha}.sql"

    ruta = BACKUP_DIR / archivo

    db_name, db_user, db_password, db_host = _database_settings()

    comando = [
        "pg_dump",
        "-h",
        db_host,
        "-U",
        db_user,
        "-F",
        "p",
        "-f",
        str(ruta),
        db_name
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    subprocess.run(
        comando,
        env=env,
        check=True,
        timeout=300,
    )

    return ruta


def restaurar_backup(archivo_backup):
    """
    Restaura backup PostgreSQL
    """

    if (os.getenv("ALLOW_DATABASE_RESTORE") or "false").lower() != "true":
        raise PermissionError("La restauración de base de datos está deshabilitada")

    db_name, db_user, db_password, db_host = _database_settings()
    ruta = _safe_backup_path(archivo_backup)

    if not ruta.is_file():
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
        str(ruta)
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    subprocess.run(
        comando,
        env=env,
        check=True,
        timeout=900,
    )

    return True
