#!/usr/bin/env python3
"""
VANER ASSET — Migración Productiva PostgreSQL
Ejecuta migraciones Alembic en producción con validaciones de seguridad
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

BACKEND_DIR = Path("backend")
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"
MIGRATIONS_DIR = BACKEND_DIR / "alembic" / "versions"

def load_env_file(env_path: Path) -> dict:
    """Carga variables de entorno desde archivo .env"""
    env = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env[key] = val
    return env

def check_database_connection(database_url: str) -> bool:
    """Verifica conexión a PostgreSQL"""
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return False

def get_current_revision(database_url: str) -> str:
    """Obtiene revisión actual de Alembic en la BD"""
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        cur.execute("SELECT version_num FROM alembic_version LIMIT 1")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else "BASE"
    except Exception:
        return "BASE"

def get_head_revision() -> str:
    """Obtiene revisión head del código"""
    try:
        result = subprocess.run(
            ["alembic", "heads"],
            cwd=BACKEND_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip().split()[0]
    except Exception:
        pass
    return "UNKNOWN"

def run_migrations(database_url: str, env: dict) -> bool:
    """Ejecuta alembic upgrade head"""
    env = {**os.environ, **env}
    
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=BACKEND_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print("✅ Migraciones aplicadas exitosamente")
            print(result.stdout)
            return True
        else:
            print("❌ Error en migraciones:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout en migraciones (>5 min)")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando migraciones: {e}")
        return False

def verify_rls_enabled(database_url: str) -> bool:
    """Verifica que RLS esté habilitado en tablas tenant-scoped"""
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Tablas que DEBEN tener RLS (tenant-scoped)
        tenant_tables = [
            "empresas", "sedes", "equipos", "mantenimientos",
            "tecnicos", "usuarios", "categorias", "repuestos",
            "bodegas", "existencias_repuestos", "movimientos_repuestos",
            "solicitudes_repuestos", "proveedores_repuestos",
            "ordenes_mantenimiento", "ot_repuestos", "ot_incidencias",
            "solicitudes_correctivas", "reportes_publicados", "facturas",
            "plantillas_reporte", "notificaciones", "auditoria_eventos",
            "auditoria_pro_eventos", "seguridad_eventos",
            "equipo_hoja_vida", "evidencias", "formatos_mantenimiento",
            "hist_mantenimiento", "historial_mantenimiento",
            "bitacoras_dinamicas", "bitacoras_respuestas",
            "repuesto_proveedor", "repuestos_compatibilidad",
            "categorias_repuestos", "unidades_medida"
        ]
        
        cur.execute("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename = ANY(%s)
            ORDER BY tablename
        """, (tenant_tables,))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        rls_enabled = 0
        rls_disabled = 0
        missing = 0
        
        for table, rowsecurity in results:
            if rowsecurity:
                rls_enabled += 1
            else:
                rls_disabled += 1
                print(f"  ⚠️  SIN RLS: {table}")
        
        expected = len(tenant_tables)
        found = len(results)
        missing = expected - found
        
        print(f"\n📊 RLS Status: {rls_enabled}/{found} habilitadas, {rls_disabled} deshabilitadas, {missing} tablas faltantes")
        
        if rls_disabled > 0:
            print("❌ ALERTA: Tablas tenant-scoped sin RLS")
            return False
        
        if missing > 5:  # Permitir algunas faltantes por versiones
            print(f"⚠️  ADVERTENCIA: {missing} tablas esperadas no existen en BD")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando RLS: {e}")
        return False

def verify_migration_history(database_url: str) -> bool:
    """Verifica que la historia de migraciones sea consistente"""
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        cur.execute("SELECT version_num FROM alembic_version ORDER BY version_num")
        versions = [row[0] for row in cur.fetchall()]
        
        cur.close()
        conn.close()
        
        print(f"📋 Migraciones aplicadas: {len(versions)}")
        for v in versions:
            print(f"   - {v}")
        
        # Verificar migraciones críticas presentes
        critical_migrations = [
            "g37c5e080001",  # RLS core
            "s01a2b3c40001",  # RLS completo tenant-scoped
            "t01a2b3c40001",  # MFA
            "c93e1a640001",  # Categorías canónicas
        ]
        
        missing_critical = [m for m in critical_migrations if not any(m in v for v in versions)]
        if missing_critical:
            print(f"❌ Migraciones críticas faltantes: {missing_critical}")
            return False
        
        print("✅ Historia de migraciones consistente")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando historia: {e}")
        return False

def create_rls_context_function(database_url: str) -> bool:
    """Crea/actualiza función helper para contexto RLS"""
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Función para establecer contexto de empresa
        cur.execute("""
            CREATE OR REPLACE FUNCTION set_empresa_context(p_empresa_id UUID)
            RETURNS VOID AS $$
            BEGIN
                PERFORM set_config('app.current_empresa_id', p_empresa_id::text, FALSE);
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER;
        """)
        
        # Función para obtener contexto actual
        cur.execute("""
            CREATE OR REPLACE FUNCTION get_empresa_context()
            RETURNS UUID AS $$
            BEGIN
                RETURN COALESCE(NULLIF(current_setting('app.current_empresa_id', TRUE), ''), '00000000-0000-0000-0000-000000000000')::UUID;
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER;
        """)
        
        cur.close()
        conn.close()
        print("✅ Funciones RLS context creadas/actualizadas")
        return True
        
    except Exception as e:
        print(f"❌ Error creando funciones RLS: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Migración productiva PostgreSQL")
    parser.add_argument("--env-file", default=".env.production", help="Archivo de entorno")
    parser.add_argument("--dry-run", action="store_true", help="Solo verificar, no ejecutar")
    parser.add_argument("--force", action="store_true", help="Forzar migración aunque haya warnings")
    args = parser.parse_args()
    
    print("=" * 60)
    print("VANER ASSET — Migración Productiva PostgreSQL")
    print("=" * 60)
    
    # Cargar entorno
    env_file = Path(args.env_file)
    if not env_file.exists():
        print(f"❌ Archivo {env_file} no encontrado")
        print("   Ejecuta primero: python scripts/rotate_secrets.py --generate")
        sys.exit(1)
    
    env = load_env_file(env_file)
    
    # Validar variables críticas
    required_vars = [
        "DATABASE_URL", "MIGRATION_DATABASE_URL", "SECRET_KEY",
        "CONFIG_ENCRYPTION_KEY", "POSTGRES_PASSWORD"
    ]
    missing = [v for v in required_vars if v not in env or not env[v]]
    if missing:
        print(f"❌ Variables críticas faltantes en {env_file}: {missing}")
        sys.exit(1)
    
    database_url = env["DATABASE_URL"]
    migration_url = env["MIGRATION_DATABASE_URL"]
    
    print(f"\n🔗 Conectando a: {database_url.split('@')[1] if '@' in database_url else 'BD'}")
    
    # Verificar conexión
    if not check_database_connection(migration_url):
        print("❌ No se puede conectar a PostgreSQL con MIGRATION_DATABASE_URL")
        sys.exit(1)
    
    print("✅ Conexión a BD exitosa")
    
    # Estado actual
    current_rev = get_current_revision(database_url)
    head_rev = get_head_revision()
    
    print(f"\n📍 Revisión actual en BD: {current_rev}")
    print(f"📍 Revisión head en código: {head_rev}")
    
    if current_rev == head_rev and current_rev != "BASE":
        print("✅ BD ya está en la revisión más reciente")
    else:
        print("🔄 Migraciones pendientes")
    
    if args.dry_run:
        print("\n[DRY-RUN] No se ejecutan migraciones")
        verify_rls_enabled(database_url)
        verify_migration_history(database_url)
        return
    
    # Ejecutar migraciones
    print("\n🚀 Ejecutando migraciones...")
    if not run_migrations(migration_url, env):
        sys.exit(1)
    
    # Verificaciones post-migración
    print("\n🔍 Verificando estado post-migración...")
    
    if not verify_migration_history(database_url):
        if not args.force:
            print("❌ Verificación fallida. Use --force para continuar anyway.")
            sys.exit(1)
    
    if not verify_rls_enabled(database_url):
        if not args.force:
            print("❌ RLS incompleto. Use --force para continuar anyway.")
            sys.exit(1)
    
    # Crear funciones helper RLS
    create_rls_context_function(database_url)
    
    print("\n" + "=" * 60)
    print("✅ MIGRACIÓN PRODUCTIVA COMPLETADA")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("  1. Verificar salud: curl https://TU_DOMINIO/health/ready")
    print("  2. Ejecutar restore drill: python scripts/restore_drill.py")
    print("  3. Configurar Redis: python scripts/setup_redis.py")

if __name__ == "__main__":
    main()