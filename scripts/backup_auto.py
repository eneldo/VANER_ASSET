#!/usr/bin/env python3
"""
VANER ASSET — Backup Automatizado PostgreSQL
Ejecuta pg_dump con retención configurable.

Uso:
    python scripts/backup_auto.py                    # Backup completo
    python scripts/backup_auto.py --retention 30     # Retención 30 días
    python scripts/backup_auto.py --dry-run          # Solo muestra qué haría
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path

BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "backups"))
RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))


def get_db_config():
    """Obtiene configuración de BD desde variables de entorno."""
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "dbname": os.getenv("POSTGRES_DB", "vaner_asset"),
        "user": os.getenv("BACKUP_DATABASE_USER", os.getenv("POSTGRES_USER", "postgres")),
        "password": os.getenv("BACKUP_DATABASE_PASSWORD", os.getenv("POSTGRES_PASSWORD", "")),
    }


def ejecutar_backup(db_config: dict, backup_dir: Path, retention_days: int, dry_run: bool = False):
    """Ejecuta backup completo con pg_dump."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"vaner_asset_{timestamp}.sql.gz"

    print(f"[{datetime.now().isoformat()}] Iniciando backup automatizado...")
    print(f"  Base de datos: {db_config['dbname']}")
    print(f"  Servidor: {db_config['host']}:{db_config['port']}")
    print(f"  Archivo: {backup_file}")

    if dry_run:
        print("  [DRY-RUN] No se ejecuta pg_dump")
        return True

    backup_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PGPASSWORD"] = db_config["password"]

    cmd = [
        "pg_dump",
        f"--host={db_config['host']}",
        f"--port={db_config['port']}",
        f"--username={db_config['user']}",
        f"--dbname={db_config['dbname']}",
        "--format=custom",
        "--compress=9",
        "--verbose",
        f"--file={backup_file}",
    ]

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutos máximo
        )

        if result.returncode != 0:
            print(f"  ERROR: pg_dump falló con código {result.returncode}")
            print(f"  stderr: {result.stderr}")
            return False

        size_mb = backup_file.stat().st_size / (1024 * 1024)
        print(f"  Backup completado: {backup_file.name} ({size_mb:.2f} MB)")

    except FileNotFoundError:
        print("  ERROR: pg_dump no encontrado. Instalar PostgreSQL client tools.")
        return False
    except subprocess.TimeoutExpired:
        print("  ERROR: pg_dump excedió timeout de 10 minutos")
        return False

    # Limpiar backups antiguos
    limpiar_backups_antiguos(backup_dir, retention_days, dry_run)

    return True


def limpiar_backups_antiguos(backup_dir: Path, retention_days: int, dry_run: bool = False):
    """Elimina backups más antiguos que retention_days."""
    cutoff = datetime.now() - timedelta(days=retention_days)
    backups = sorted(backup_dir.glob("vaner_asset_*.sql.gz"))

    eliminados = 0
    for backup in backups:
        # Extraer timestamp del nombre del archivo
        try:
            ts_str = backup.stem.replace("vaner_asset_", "").replace(".sql", "")
            file_date = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
            if file_date < cutoff:
                if dry_run:
                    print(f"  [DRY-RUN] Se eliminaría: {backup.name}")
                else:
                    backup.unlink()
                    print(f"  Eliminado: {backup.name}")
                eliminados += 1
        except ValueError:
            continue

    if eliminados > 0:
        print(f"  Limpieza: {eliminados} backups eliminados (retención: {retention_days} días)")
    else:
        print(f"  Limpieza: sin backups antiguos (retención: {retention_days} días)")


def listar_backups(backup_dir: Path):
    """Lista todos los backups existentes."""
    backups = sorted(backup_dir.glob("vaner_asset_*.sql.gz"))
    if not backups:
        print("No hay backups encontrados.")
        return

    print(f"\nBackups en {backup_dir}:")
    print("-" * 60)
    total_size = 0
    for backup in backups:
        size_mb = backup.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"  {backup.name}  ({size_mb:.2f} MB)")
    print("-" * 60)
    print(f"Total: {len(backups)} backups, {total_size:.2f} MB")


def main():
    parser = argparse.ArgumentParser(description="VANER ASSET — Backup Automatizado")
    parser.add_argument("--retention", type=int, default=RETENTION_DAYS,
                        help=f"Días de retención (default: {RETENTION_DAYS})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Solo muestra qué haría, no ejecuta")
    parser.add_argument("--list", action="store_true",
                        help="Lista backups existentes")
    parser.add_argument("--dir", type=str, default=str(BACKUP_DIR),
                        help=f"Directorio de backups (default: {BACKUP_DIR})")
    args = parser.parse_args()

    backup_dir = Path(args.dir)

    if args.list:
        listar_backups(backup_dir)
        return

    db_config = get_db_config()
    success = ejecutar_backup(db_config, backup_dir, args.retention, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
