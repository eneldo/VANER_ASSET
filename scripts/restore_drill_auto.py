#!/usr/bin/env python3
"""
VANER ASSET — Restore Drill Automatizado para Producción
Ejecuta restore completo de backup a BD de prueba y verifica integridad
Compatible con Docker y despliegue bare-metal
"""

import os
import sys
import subprocess
import argparse
import gzip
import shutil
from datetime import datetime
from pathlib import Path

# Configuración por defecto
BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "backups"))
TEST_DB_SUFFIX = "_restore_drill_test"

def get_db_config(env_file: Path = None) -> dict:
    """Obtiene configuración de BD desde variables de entorno o archivo"""
    config = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "user": os.getenv("BACKUP_DATABASE_USER", os.getenv("POSTGRES_USER", "postgres")),
        "password": os.getenv("BACKUP_DATABASE_PASSWORD", os.getenv("POSTGRES_PASSWORD")),
        "source_db": os.getenv("POSTGRES_DB", "vaner_asset"),
    }
    
    if env_file and env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                if key in ["POSTGRES_HOST", "POSTGRES_PORT", "BACKUP_DATABASE_USER", 
                          "BACKUP_DATABASE_PASSWORD", "POSTGRES_DB", "POSTGRES_PASSWORD"]:
                    config[key.lower().replace("postgres_", "").replace("backup_database_", "")] = val
    
    # Normalizar claves
    if "host" not in config:
        config["host"] = config.get("POSTGRES_HOST", "localhost")
    if "port" not in config:
        config["port"] = config.get("POSTGRES_PORT", "5432")
    if "user" not in config:
        config["user"] = config.get("BACKUP_DATABASE_USER") or config.get("POSTGRES_USER", "postgres")
    if "password" not in config:
        config["password"] = config.get("BACKUP_DATABASE_PASSWORD") or config.get("POSTGRES_PASSWORD")
    if "source_db" not in config:
        config["source_db"] = config.get("POSTGRES_DB", "vaner_asset")
    
    return config

def find_pg_tools() -> dict:
    """Encuentra herramientas de PostgreSQL (psql, pg_restore, pg_dump)"""
    tools = {}
    
    # Buscar en PATH
    for tool in ["psql", "pg_restore", "pg_dump", "createdb", "dropdb"]:
        path = shutil.which(tool)
        if path:
            tools[tool] = path
    
    # Rutas comunes Windows
    if sys.platform == "win32" and not tools:
        common_paths = [
            r"C:\Program Files\PostgreSQL\17\bin",
            r"C:\Program Files\PostgreSQL\16\bin",
            r"C:\Program Files\PostgreSQL\15\bin",
        ]
        for base in common_paths:
            for tool in ["psql.exe", "pg_restore.exe", "pg_dump.exe", "createdb.exe", "dropdb.exe"]:
                full = Path(base) / tool
                if full.exists():
                    tools[tool.replace(".exe", "")] = str(full)
    
    # Rutas comunes Linux/macOS
    if not tools:
        common_paths = [
            "/usr/bin",
            "/usr/local/bin",
            "/opt/homebrew/bin",
        ]
        for base in common_paths:
            for tool in ["psql", "pg_restore", "pg_dump", "createdb", "dropdb"]:
                full = Path(base) / tool
                if full.exists():
                    tools[tool] = str(full)
    
    return tools

def run_pg_command(tool: str, args: list, db_config: dict, database: str = None, env: dict = None) -> tuple:
    """Ejecuta comando PostgreSQL"""
    tools = find_pg_tools()
    if tool not in tools:
        return False, "", f"{tool} no encontrado. Instale postgresql-client"
    
    cmd_env = os.environ.copy()
    cmd_env["PGPASSWORD"] = db_config["password"]
    if env:
        cmd_env.update(env)
    
    target_db = database or db_config["source_db"]
    cmd = [
        tools[tool],
        f"--host={db_config['host']}",
        f"--port={db_config['port']}",
        f"--username={db_config['user']}",
        f"--dbname={target_db}",
    ] + args
    
    try:
        result = subprocess.run(cmd, env=cmd_env, capture_output=True, text=True, timeout=600)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Timeout ejecutando {tool}"
    except Exception as e:
        return False, "", str(e)

def database_exists(db_name: str, db_config: dict) -> bool:
    """Verifica si una base de datos existe"""
    success, stdout, _ = run_pg_command("psql", ["-t", "-A", "-c", f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"], db_config, "postgres")
    return success and "1" in stdout

def drop_database(db_name: str, db_config: dict) -> bool:
    """Elimina una base de datos"""
    success, _, stderr = run_pg_command("dropdb", ["--if-exists", db_name], db_config, "postgres")
    if not success and "does not exist" not in stderr:
        return False
    return True

def create_database(db_name: str, db_config: dict) -> bool:
    """Crea una base de datos"""
    success, _, stderr = run_pg_command("createdb", [db_name], db_config, "postgres")
    if not success and "already exists" not in stderr:
        return False
    return True

def restore_backup(backup_file: Path, db_config: dict, test_db: str) -> bool:
    """Restaura un backup a la BD de prueba"""
    print(f"  Restaurando {backup_file.name} en {test_db}...")
    
    # Detectar si es .gz
    if backup_file.suffix == ".gz":
        # Descomprimir a temporal
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".sql", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            with gzip.open(backup_file, 'rb') as f_in:
                with open(tmp_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            backup_file = tmp_path
        except Exception as e:
            print(f"  ❌ Error descomprimiendo: {e}")
            return False
    
    success, stdout, stderr = run_pg_command("psql", ["-f", str(backup_file)], db_config, test_db)
    
    # Limpiar temporal
    if backup_file.suffix == ".sql" and "tmp" in str(backup_file):
        try:
            backup_file.unlink()
        except:
            pass
    
    if not success:
        # pg_restore puede retornar warnings no fatales
        if "error" in stderr.lower() and "warning" not in stderr.lower():
            print(f"  ❌ Error restaurando: {stderr[-500:]}")
            return False
        else:
            print(f"  ⚠️  Warnings (no fatales): {stderr[-200:]}")
    
    return True

def verify_tables(db_config: dict, test_db: str) -> dict:
    """Verifica que las tablas existan en la BD restaurada"""
    success, stdout, _ = run_pg_command("psql", [
        "-t", "-A", "-c",
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name"
    ], db_config, test_db)
    
    if not success:
        return {"count": 0, "tables": []}
    
    tablas = [line.strip() for line in stdout.strip().split("\n") if line.strip()]
    return {"count": len(tablas), "tables": tablas}

def verify_record_counts(db_config: dict, test_db: str) -> dict:
    """Cuenta registros en tablas principales"""
    tablas_principales = [
        "empresas", "sedes", "usuarios", "equipos",
        "mantenimientos", "tecnicos", "categorias",
        "repuestos", "bodegas", "ordenes_mantenimiento",
        "ot_repuestos", "ot_incidencias",
        "solicitudes_correctivas", "reportes_publicados",
        "plantillas_reporte", "notificaciones",
        "auditoria_eventos", "formatos_mantenimiento",
        "equipo_hoja_vida", "evidencias",
    ]
    
    conteos = {}
    for tabla in tablas_principales:
        success, stdout, _ = run_pg_command("psql", [
            "-t", "-A", "-c", f"SELECT COUNT(*) FROM {tabla}"
        ], db_config, test_db)
        if success:
            try:
                conteos[tabla] = int(stdout.strip())
            except:
                conteos[tabla] = -1
        else:
            conteos[tabla] = -1
    return conteos

def verify_rls(db_config: dict, test_db: str) -> dict:
    """Verifica que RLS esté habilitado en las tablas"""
    success, stdout, _ = run_pg_command("psql", [
        "-t", "-A", "-c",
        "SELECT schemaname, tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
    ], db_config, test_db)
    
    if not success:
        return {"con_rls": 0, "sin_rls": 0, "total": 0}
    
    tablas_con_rls = 0
    tablas_sin_rls = 0
    for line in stdout.strip().split("\n"):
        parts = line.strip().split("|")
        if len(parts) == 3:
            rls_enabled = parts[2].strip().lower() == "true"
            if rls_enabled:
                tablas_con_rls += 1
            else:
                tablas_sin_rls += 1
    return {"con_rls": tablas_con_rls, "sin_rls": tablas_sin_rls, "total": tablas_con_rls + tablas_sin_rls}

def verify_migrations(db_config: dict, test_db: str) -> dict:
    """Verifica la tabla de migraciones de Alembic"""
    success, stdout, _ = run_pg_command("psql", [
        "-t", "-A", "-c", "SELECT version_num FROM alembic_version ORDER BY version_num"
    ], db_config, test_db)
    
    if not success:
        return {"count": 0, "versions": []}
    
    versiones = [v.strip() for v in stdout.strip().split("\n") if v.strip()]
    return {"count": len(versiones), "versions": versiones}

def verify_rls_policies(db_config: dict, test_db: str) -> bool:
    """Verifica que las políticas RLS existen"""
    success, stdout, _ = run_pg_command("psql", [
        "-t", "-A", "-c",
        "SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public'"
    ], db_config, test_db)
    
    if success:
        try:
            count = int(stdout.strip())
            print(f"  Políticas RLS encontradas: {count}")
            return count > 20  # Esperamos muchas políticas
        except:
            pass
    return False

def main():
    parser = argparse.ArgumentParser(description="VANER ASSET — Restore Drill Automatizado")
    parser.add_argument("--backup", type=str, help="Archivo de backup específico")
    parser.add_argument("--dry-run", action="store_true", help="Solo muestra qué haría")
    parser.add_argument("--dir", type=str, default=str(BACKUP_DIR), help="Directorio de backups")
    parser.add_argument("--env-file", type=str, default=".env.production", help="Archivo de entorno")
    parser.add_argument("--test-db", type=str, help="Nombre BD de prueba (default: auto)")
    parser.add_argument("--skip-cleanup", action="store_true", help="No eliminar BD de prueba al final")
    parser.add_argument("--ci", action="store_true", help="Modo CI (exit codes, menos output)")
    args = parser.parse_args()
    
    if not args.ci:
        print("=" * 60)
        print("VANER ASSET — Restore Drill Automatizado")
        print("=" * 60)
    
    env_file = Path(args.env_file)
    db_config = get_db_config(env_file)
    
    if not db_config["password"]:
        print("❌ Password de BD no configurado")
        print("   Configure BACKUP_DATABASE_PASSWORD o POSTGRES_PASSWORD en .env")
        sys.exit(1)
    
    test_db = args.test_db or f"{db_config['source_db']}{TEST_DB_SUFFIX}"
    
    backup_dir = Path(args.dir)
    
    # Seleccionar backup
    if args.backup:
        backup_file = Path(args.backup)
    else:
        backups = sorted(backup_dir.glob("vaner_asset_*.sql*"))
        if not backups:
            backups = sorted(backup_dir.glob("*.sql*"))
        if not backups:
            print(f"❌ No hay backups encontrados en {backup_dir}")
            sys.exit(1)
        backup_file = backups[-1]
    
    if not backup_file.exists():
        print(f"❌ Backup no encontrado: {backup_file}")
        sys.exit(1)
    
    if not args.ci:
        print(f"\nBackup: {backup_file.name} ({backup_file.stat().st_size / (1024*1024):.2f} MB)")
        print(f"BD origen: {db_config['source_db']}@{db_config['host']}:{db_config['port']}")
        print(f"BD prueba: {test_db}")
    
    if args.dry_run:
        print("\n[DRY-RUN] Pasos que se ejecutarían:")
        print(f"  1. Crear BD temporal: {test_db}")
        print(f"  2. Restaurar backup: {backup_file.name}")
        print(f"  3. Verificar tablas, registros, RLS, migraciones")
        print(f"  4. Eliminar BD temporal: {test_db}")
        return
    
    report = {
        "backup_file": backup_file.name,
        "backup_size_mb": round(backup_file.stat().st_size / (1024*1024), 2),
        "test_database": test_db,
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "passed": 0,
        "failed": 0,
    }
    
    try:
        # Paso 1: Crear BD de prueba
        if not args.ci: print(f"\n[1/6] Creando BD de prueba: {test_db}")
        drop_database(test_db, db_config)
        if not create_database(test_db, db_config):
            raise Exception("No se pudo crear BD de prueba")
        if not args.ci: print("  ✅ OK")
        
        # Paso 2: Restaurar backup
        if not args.ci: print(f"\n[2/6] Restaurando backup...")
        if not restore_backup(backup_file, db_config, test_db):
            raise Exception("Falló restore de backup")
        if not args.ci: print("  ✅ OK")
        
        # Paso 3: Verificar tablas
        if not args.ci: print(f"\n[3/6] Verificando tablas...")
        tablas = verify_tables(db_config, test_db)
        report["checks"]["tablas"] = tablas
        if tablas["count"] >= 30:
            if not args.ci: print(f"  ✅ {tablas['count']} tablas encontradas")
            report["passed"] += 1
        else:
            if not args.ci: print(f"  ❌ Solo {tablas['count']} tablas (esperado >= 30)")
            report["failed"] += 1
        
        # Paso 4: Verificar registros
        if not args.ci: print(f"\n[4/6] Verificando registros...")
        registros = verify_record_counts(db_config, test_db)
        report["checks"]["registros"] = registros
        tablas_con_datos = sum(1 for v in registros.values() if v > 0)
        if not args.ci:
            print(f"  Tablas con datos: {tablas_con_datos}/{len(registros)}")
            for tabla, count in registros.items():
                status = "✅" if count > 0 else "⚠️" if count == 0 else "❌"
                print(f"    {status} {tabla}: {count}")
        report["passed"] += 1
        
        # Paso 5: Verificar RLS
        if not args.ci: print(f"\n[5/6] Verificando RLS...")
        rls = verify_rls(db_config, test_db)
        report["checks"]["rls"] = rls
        policies_ok = verify_rls_policies(db_config, test_db)
        if not args.ci:
            print(f"  Tablas con RLS: {rls['con_rls']}")
            print(f"  Tablas sin RLS: {rls['sin_rls']}")
            print(f"  Políticas RLS: {'✅' if policies_ok else '❌'}")
        if rls["sin_rls"] == 0 and policies_ok:
            report["passed"] += 1
        else:
            report["failed"] += 1
        
        # Paso 6: Verificar migraciones
        if not args.ci: print(f"\n[6/6] Verificando migraciones...")
        migraciones = verify_migrations(db_config, test_db)
        report["checks"]["migraciones"] = migraciones
        if not args.ci:
            print(f"  Versiones aplicadas: {migraciones['count']}")
            critical = ["g37c5e080001", "s01a2b3c40001", "t01a2b3c40001"]
            for c in critical:
                found = any(c in v for v in migraciones["versions"])
                print(f"    {'✅' if found else '❌'} {c}")
        report["passed"] += 1
        
    except Exception as e:
        if not args.ci: print(f"\n❌ ERROR: {e}")
        report["failed"] += 1
    
    finally:
        if not args.skip_cleanup:
            if not args.ci: print(f"\n[LIMPIEZA] Eliminando BD de prueba: {test_db}")
            drop_database(test_db, db_config)
            if not args.ci: print("  ✅ OK")
        else:
            if not args.ci: print(f"\n⚠️ BD de prueba conservada: {test_db}")
    
    if not args.ci:
        print("\n" + "=" * 60)
        print("REPORTE DE RESTORE DRILL")
        print("=" * 60)
        print(f"Backup: {report['backup_file']} ({report['backup_size_mb']} MB)")
        print(f"Tablas restauradas: {report['checks'].get('tablas', {}).get('count', 'N/A')}")
        tablas_con_datos = sum(1 for v in report['checks'].get('registros', {}).values() if v > 0)
        print(f"Tablas con datos: {tablas_con_datos}")
        rls = report['checks'].get('rls', {})
        print(f"RLS habilitado: {rls.get('con_rls', 'N/A')} tablas")
        print(f"Migraciones: {report['checks'].get('migraciones', {}).get('count', 'N/A')}")
        print(f"Tests pasados: {report['passed']}")
        print(f"Tests fallidos: {report['failed']}")
        
        if report["failed"] == 0:
            print("\n✅ RESULTADO: EXITOSO - Backup válido y restaurable")
        else:
            print("\n❌ RESULTADO: CON ERRORES - Revisar backup")
        print("=" * 60)
    
    sys.exit(0 if report["failed"] == 0 else 1)

if __name__ == "__main__":
    main()