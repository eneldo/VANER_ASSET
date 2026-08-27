# =========================================================
# TESTS: Integración RLS Multi-Tenant
# Archivo: tests/test_rls_multitenant.py
#
# Verifica que el aislamiento RLS esté configurado correctamente.
# Estos tests verifican la estructura, no la ejecución en DB.
# =========================================================

import os
import re
import pytest


class TestRLSMigrationCoverage:
    """Tests para verificar cobertura de migraciones RLS."""

    def test_rls_migration_files_exist(self):
        """Verifica que existan archivos de migración RLS."""
        versions_dir = os.path.join(
            os.path.dirname(__file__), '..', 'alembic', 'versions'
        )

        rls_migrations = [
            'g37c5e080001_rls_multi_tenant.py',
            's01a2b3c40001_rls_completo_tenant_scoped.py',
        ]

        for migration in rls_migrations:
            path = os.path.join(versions_dir, migration)
            assert os.path.exists(path), f"Migración RLS no encontrada: {migration}"

    def test_rls_migration_covers_critical_tables(self):
        """Verifica que la migración RLS cubra todas las tablas críticas."""
        migration_path = os.path.join(
            os.path.dirname(__file__), '..', 'alembic', 'versions',
            's01a2b3c40001_rls_completo_tenant_scoped.py'
        )

        with open(migration_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Tables that must be in the migration
        required_tables = [
            'notificaciones',
            'categorias_repuestos',
            'repuestos',
            'bodegas',
            'existencias_repuestos',
            'movimientos_repuestos',
            'solicitudes_repuestos',
            'proveedores_repuestos',
            'repuesto_proveedor',
            'repuestos_compatibilidad',
        ]

        for table in required_tables:
            assert table in content, f"Tabla {table} no encontrada en migración RLS"

    def test_rls_base_migration_covers_core_tables(self):
        """Verifica que la migración base cubra las tablas core."""
        migration_path = os.path.join(
            os.path.dirname(__file__), '..', 'alembic', 'versions',
            'g37c5e080001_rls_multi_tenant.py'
        )

        with open(migration_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Core tables that must be in the base migration
        core_tables = [
            'empresas', 'sedes', 'equipos', 'mantenimientos',
            'solicitudes_correctivas', 'reportes_publicados', 'facturas',
            'ot_repuestos', 'ot_incidencias',
        ]

        for table in core_tables:
            assert table in content, f"Tabla core {table} no encontrada en migración base"

    def test_all_models_with_empresa_id_are_covered(self):
        """Verifica que todos los modelos con empresa_id estén cubiertos por RLS."""
        models_dir = os.path.join(
            os.path.dirname(__file__), '..', 'app', 'models'
        )

        # Find all models with empresa_id
        tables_with_empresa_id = set()
        for filename in os.listdir(models_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(models_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Find table names
                    table_matches = re.findall(
                        r'__tablename__\s*=\s*["\']([^"\']+)["\']', content
                    )
                    # Check if has empresa_id
                    if 'empresa_id' in content:
                        for table in table_matches:
                            tables_with_empresa_id.add(table)

        # Tables covered by RLS migrations
        covered_tables = {
            'empresas', 'sedes', 'equipos', 'mantenimientos',
            'solicitudes_correctivas', 'reportes_publicados', 'facturas',
            'ot_repuestos', 'ot_incidencias', 'notificaciones',
            'categorias_repuestos', 'repuestos', 'bodegas',
            'existencias_repuestos', 'movimientos_repuestos',
            'solicitudes_repuestos', 'proveedores_repuestos',
            'auditoria_eventos', 'auditoria_pro_eventos', 'seguridad_eventos',
            'plantillas_reporte',
        }

        # Tables that are covered indirectly (via foreign keys)
        indirectly_covered = {
            'tecnicos',  # via usuarios.empresa_id
            'equipo_hoja_vida',  # via equipos.empresa_id
            'evidencias',  # via mantenimientos.empresa_id
            'formatos_mantenimiento',  # via mantenimientos.empresa_id
            'hist_mantenimiento',  # via mantenimientos.empresa_id
            'historial_mantenimiento',  # via mantenimientos.empresa_id
            'bitacoras_dinamicas',  # via mantenimientos.empresa_id
            'bitacoras_respuestas',  # via bitacoras_dinamicas
            'repuesto_proveedor',  # via repuestos.empresa_id
            'repuestos_compatibilidad',  # via repuestos.empresa_id
            'usuarios',  # empresa_id is the tenant itself
        }

        all_covered = covered_tables | indirectly_covered
        uncovered = tables_with_empresa_id - all_covered

        # These tables are global catalogs or have nullable empresa_id
        acceptable_uncovered = {'password_history', 'unidades_medida'}
        truly_uncovered = uncovered - acceptable_uncovered

        assert not truly_uncovered, \
            f"Tablas con empresa_id sin cobertura RLS: {truly_uncovered}"


class TestMFAService:
    """Tests para el servicio MFA."""

    def test_mfa_secret_generation(self):
        """Verifica que se generen secretos MFA válidos."""
        from app.services.mfa_service import generate_mfa_secret, BASE32_CHARS

        secret = generate_mfa_secret()
        assert len(secret) > 0
        # Verify all chars are valid base32
        for char in secret:
            assert char in BASE32_CHARS or char == '='

    def test_mfa_uri_generation(self):
        """Verifica que se genere URI MFA válido."""
        from app.services.mfa_service import generate_mfa_secret, generate_mfa_uri

        secret = generate_mfa_secret()
        uri = generate_mfa_uri(secret, "test@vanerasset.com")

        assert uri.startswith("otpauth://totp/")
        assert "vanerasset.com" in uri
        assert secret in uri

    def test_totp_code_generation(self):
        """Verifica que se generen códigos TOTP de 6 dígitos."""
        from app.services.mfa_service import generate_mfa_secret, generate_totp_code

        secret = generate_mfa_secret()
        code = generate_totp_code(secret)

        assert len(code) == 6
        assert code.isdigit()

    def test_totp_code_verification(self):
        """Verifica que la verificación TOTP funcione."""
        from app.services.mfa_service import (
            generate_mfa_secret, generate_totp_code, verify_totp_code
        )

        secret = generate_mfa_secret()
        code = generate_totp_code(secret)

        # Should verify successfully
        assert verify_totp_code(secret, code) is True

        # Should fail with wrong code
        assert verify_totp_code(secret, "000000") is False

    def test_backup_codes_generation(self):
        """Verifica que se generen códigos de respaldo."""
        from app.services.mfa_service import generate_backup_codes

        codes = generate_backup_codes(8)
        assert len(codes) == 8
        for code in codes:
            assert len(code) == 9  # XXXX-XXXX format
            assert '-' in code
