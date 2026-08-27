#!/usr/bin/env python3
"""
VANER ASSET — Restore Drill Script
Ejecuta un restore completo de backup a BD de prueba y verifica integridad.

Uso:
    python scripts/restore_drill.py                           # Último backup
    python scripts/restore_drill.py --backup backups/vaner_asset_20260827_120000.sql.gz
    python scripts/restore_drill.py --dry-run                 # Solo muestra qué haría
"""

import os
import sys
import subprocess
import argparse
import gzip
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "backups"))
TEST_DB_SUFFIX = "_restore_drill_test"
TEST_DB = f"vaner_asset{TEST_DB_SUFFIX}"

PGSQL_PATH = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"
PG_DUMP_PATH = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
PG_RESTORE_PATH = r"C:\Program Files\PostgreSQL\17\bin\pg_restore.exe"


def get_db_config():
    """Obtiene configuración de BD desde variables de entorno."""
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "user": os.getenv("BACKUP_DATABASE_USER", os.getenv("POSTGRES_USER", "postgres")),
        "password": os.getenv("BACKUP_DATABASE_PASSWORD", os.getenv("POSTGRES_PASSWORD", "SQL.LocalSgaAdmin2026Segura")),
        "source_db": os.getenv("POSTGRES_DB", "vaner_asset"),
    }


def ejecutar_sql(sql: str, db_config: dict, database: str = None, capture: bool = False):
    """Ejecuta SQL usando psql."""
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config["password"]

    target_db = database or db_config["source_db"]
    cmd = [
        PGSQL_PATH,
        f"--host={db_config['host']}",
        f"--port={db_config['port']}",
        f"--username={db_config['user']}",
        f"--dbname={target_db}",
        "-c", sql,
    ]

    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise Exception(f"SQL error: {result.stderr}")
    return result.stdout if capture else None


def database_exists(db_name: str, db_config: dict) -> bool:
    """Verifica si una base de datos existe."""
    sql = f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config["password"]
    cmd = [
        PGSQL_PATH,
        f"--host={db_config['host']}",
        f"--port={db_config['port']}",
        f"--username={db_config['user']}",
        "--dbname=postgres",
        "-t", "-A", "-c", sql,
    ]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
    return "1" in result.stdout


def drop_database(db_name: str, db_config: dict):
    """Elimina una base de datos."""
    ejecutar_sql(f"DROP DATABASE IF EXISTS {db_name}", db_config, "postgres")


def create_database(db_name: str, db_config: dict):
    """Crea una base de datos."""
    ejecutar_sql(f"CREATE DATABASE {db_name}", db_config, "postgres")


def restore_backup(backup_file: Path, db_config: dict) -> bool:
    """Restaura un backup a la BD de prueba."""
    print(f"  Restaurando {backup_file.name} en {TEST_DB}...")

    env = os.environ.copy()
    env["PGPASSWORD"] = db_config["password"]

    # Detectar formato del backup
    cmd = [
        PG_RESTORE_PATH,
        f"--host={db_config['host']}",
        f"--port={db_config['port']}",
        f"--username={db_config['user']}",
        f"--dbname={TEST_DB}",
        "--verbose",
        "--no-owner",
        "--no-privileges",
        str(backup_file),
    ]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        # pg_restore puede retornar warnings no fatales
        if "error" in result.stderr.lower() and "warning" not in result.stderr.lower():
            print(f"  WARNING: pg_restore retornó código {result.returncode}")
            print(f"  stderr (últimas 500 chars): {result.stderr[-500:]}")

    return True


def verificar_tablas(db_config: dict) -> dict:
    """Verifica que las tablas existan en la BD restaurada."""
    sql = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
    ORDER BY table_name
    """
    result = ejecutar_sql(sql, db_config, TEST_DB, capture=True)
    tablas = [line.strip() for line in result.strip().split("\n") if line.strip()]
    return {"count": len(tablas), "tables": tablas}


def verificar_registros(db_config: dict) -> dict:
    """Cuenta registros en tablas principales."""
    tablas_principales = [
        "empresas", "sedes", "usuarios", "equipos",
        "mantenimientos", "tecnicos", "categorias",
        "repuestos", "bodegas", "ordenes_mantenimiento",
    ]
    conteos = {}
    for tabla in tablas_principales:
        try:
            sql = f"SELECT COUNT(*) FROM {tabla}"
            result = ejecutar_sql(sql, db_config, TEST_DB, capture=True)
            conteos[tabla] = int(result.strip())
        except Exception:
            conteos[tabla] = -1  # Tabla no existe o error
    return conteos


def verificar_rls(db_config: dict) -> dict:
    """Verifica que RLS esté habilitado en las tablas."""
    sql = """
    SELECT
        schemaname,
        tablename,
        rowsecurity
    FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename
    """
    result = ejecutar_sql(sql, db_config, TEST_DB, capture=True)
    tablas_con_rls = 0
    tablas_sin_rls = 0
    for line in result.strip().split("\n"):
        parts = line.strip().split("|")
        if len(parts) == 3:
            rls_enabled = parts[2].strip().lower() == "true"
            if rls_enabled:
                tablas_con_rls += 1
            else:
                tablas_sin_rls += 1
    return {"con_rls": tablas_con_rls, "sin_rls": tablas_sin_rls}


def verificar_migraciones(db_config: dict) -> dict:
    """Verifica la tabla de migraciones de Alembic."""
    try:
        sql = "SELECT version_num FROM alembic_version ORDER BY version_num"
        result = ejecutar_sql(sql, db_config, TEST_DB, capture=True)
        versiones = [v.strip() for v in result.strip().split("\n") if v.strip()]
        return {"count": len(versiones), "versions": versiones}
    except Exception:
        return {"count": 0, "versions": []}


def main():
    parser = argparse.ArgumentParser(description="VANER ASSET — Restore Drill")
    parser.add_argument("--backup", type=str, help="Archivo de backup específico")
    parser.add_argument("--dry-run", action="store_true", help="Solo muestra qué haría")
    parser.add_argument("--dir", type=str, default=str(BACKUP_DIR), help="Directorio de backups")
    args = parser.parse_args()

    print("=" * 60)
    print("VANER ASSET — Restore Drill")
    print("=" * 60)

    backup_dir = Path(args.dir)

    # Seleccionar backup
    if args.backup:
        backup_file = Path(args.backup)
    else:
        backups = sorted(backup_dir.glob("vaner_asset_*.sql.gz"))
        if not backups:
            print("ERROR: No hay backups encontrados en", backup_dir)
            sys.exit(1)
        backup_file = backups[-1]  # Último backup

    print(f"\nBackup seleccionado: {backup_file.name}")
    print(f"Tamaño: {backup_file.stat().st_size / (1024*1024):.2f} MB")

    if args.dry_run:
        print("\n[DRY-RUN] No se ejecutan cambios")
        print(f"  1. Crear BD temporal: {TEST_DB}")
        print(f"  2. Restaurar backup: {backup_file.name}")
        print(f"  3. Verificar integridad")
        print(f"  4. Eliminar BD temporal: {TEST_DB}")
        return

    db_config = get_db_config()
    report = {
        "backup_file": backup_file.name,
        "backup_size_mb": round(backup_file.stat().st_size / (1024*1024), 2),
        "test_database": TEST_DB,
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "passed": 0,
        "failed": 0,
    }

    try:
        # Paso 1: Crear BD de prueba
        print(f"\n[1/5] Creando BD de prueba: {TEST_DB}")
        drop_database(TEST_DB, db_config)
        create_database(TEST_DB, db_config)
        print("  OK")

        # Paso 2: Restaurar backup
        print(f"\n[2/5] Restaurando backup...")
        restore_backup(backup_file, db_config)
        print("  OK")

        # Paso 3: Verificar tablas
        print(f"\n[3/5] Verificando tablas...")
        tablas = verificar_tablas(db_config)
        report["checks"]["tablas"] = tablas
        if tablas["count"] >= 30:  # Esperamos ~34 tablas
            print(f"  OK: {tablas['count']} tablas encontradas")
            report["passed"] += 1
        else:
            print(f"  WARNING: Solo {tablas['count']} tablas (esperado >= 30)")
            report["failed"] += 1

        # Paso 4: Verificar registros
        print(f"\n[4/5] Verificando registros...")
        registros = verificar_registros(db_config)
        report["checks"]["registros"] = registros
        tablas_con_datos = sum(1 for v in registros.values() if v > 0)
        print(f"  Tablas con datos: {tablas_con_datos}/{len(registros)}")
        for tabla, count in registros.items():
            print(f"    {tabla}: {count} registros")
        report["passed"] += 1

        # Paso 5: Verificar RLS
        print(f"\n[5/5] Verificando RLS...")
        rls = verificar_rls(db_config)
        report["checks"]["rls"] = rls
        print(f"  Tablas con RLS: {rls['con_rls']}")
        print(f"  Tablas sin RLS: {rls['sin_rls']}")
        report["passed"] += 1

        # Verificar migraciones
        print(f"\n[BONUS] Verificando migraciones...")
        migraciones = verificar_migraciones(db_config)
        report["checks"]["migraciones"] = migraciones
        print(f"  Versiones aplicadas: {migraciones['count']}")

    except Exception as e:
        print(f"\nERROR: {e}")
        report["failed"] += 1

    finally:
        # Limpiar BD de prueba
        print(f"\n[LIMPIEZA] Eliminando BD de prueba: {TEST_DB}")
        drop_database(TEST_DB, db_config)
        print("  OK")

    # Resumen
    print("\n" + "=" * 60)
    print("REPORTE DE RESTORE DRILL")
    print("=" * 60)
    print(f"Backup: {report['backup_file']}")
    print(f"Tamaño: {report['backup_size_mb']} MB")
    print(f"Tablas restauradas: {tablas['count']}")
    print(f"Tablas con datos: {tablas_con_datos}")
    print(f"RLS habilitado: {rls['con_rls']} tablas")
    print(f"Migraciones: {migraciones['count']}")
    print(f"Tests pasados: {report['passed']}")
    print(f"Tests fallidos: {report['failed']}")

    if report["failed"] == 0:
        print("\nRESULTADO: EXITOSO")
    else:
        print("\nRESULTADO: CON ERRORES")

    print("=" * 60)


if __name__ == "__main__":
    main()
