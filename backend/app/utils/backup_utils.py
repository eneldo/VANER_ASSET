# ============================================================
# UTILIDADES BACKUP PRO
# ============================================================

import os
import subprocess
from datetime import datetime
from pathlib import Path
from sqlalchemy.engine import make_url

BACKUP_DIR = (Path(os.getenv("BACKUP_DIR") or "app/backups").resolve() / "postgres")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def _required_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise RuntimeError(f"Falta la variable obligatoria {name}")
    return value


def _database_settings(url_env: str) -> tuple[str, str, str, str, str]:
    url = make_url(_required_env(url_env))
    if not all((url.database, url.username, url.password, url.host)):
        raise RuntimeError(f"{url_env} does not contain a complete PostgreSQL URL")
    return url.database, url.username, url.password, url.host, str(url.port or 5432)

def _backup_database_settings() -> tuple[str, str, str, str, str]:
    if (os.getenv("BACKUP_DATABASE_URL") or "").strip():
        return _database_settings("BACKUP_DATABASE_URL")
    if (os.getenv("APP_ENV") or "development").lower() == "production":
        raise RuntimeError("Falta la variable obligatoria BACKUP_DATABASE_URL")
    return _database_settings("DATABASE_URL")


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

    db_name, db_user, db_password, db_host, db_port = _backup_database_settings()

    comando = [
        "pg_dump",
        "-h",
        db_host,
        "-p",
        db_port,
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

    db_name, db_user, db_password, db_host, db_port = _database_settings(
        "MIGRATION_DATABASE_URL"
    )
    ruta = _safe_backup_path(archivo_backup)

    if not ruta.is_file():
        raise Exception("Backup no encontrado")

    comando = [
        "psql",
        "-h",
        db_host,
        "-p",
        db_port,
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
