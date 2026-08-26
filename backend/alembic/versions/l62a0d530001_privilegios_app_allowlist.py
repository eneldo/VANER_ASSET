"""Privilegios explícitos para el rol de aplicación.

Revision ID: l62a0d530001
Revises: k61f9c420001
"""

from alembic import op


revision = "l62a0d530001"
down_revision = "k61f9c420001"
branch_labels = None
depends_on = None


APP_TABLES = (
    "auditoria_eventos",
    "auditoria_pro_eventos",
    "auditoria_sistema",
    "automatizacion_logs",
    "automatizaciones",
    "backup_historial",
    "bitacoras_dinamicas",
    "bitacoras_respuestas",
    "categorias",
    "configuracion_saas",
    "configuracion_sistema",
    "usuario_empresas",
    "devops_eventos",
    "empresas",
    "equipo_hoja_vida",
    "equipos",
    "evidencias",
    "facturas",
    "formatos_campos",
    "formatos_mantenimiento",
    "hist_mantenimiento",
    "historial_mantenimiento",
    "login_intentos",
    "logs_sistema",
    "mantenimientos",
    "monitor_estado",
    "notificaciones",
    "ot_incidencias",
    "ot_repuestos",
    "password_history",
    "password_reset_tokens",
    "permisos_sistema",
    "plantillas_reporte",
    "refresh_tokens",
    "reportes_publicados",
    "roles_permisos",
    "roles_sistema",
    "scheduler_inteligente_logs",
    "scheduler_reglas_mantenimiento",
    "scheduler_sugerencias_mantenimiento",
    "sedes",
    "seguridad_eventos",
    "smtp_logs",
    "solicitudes_correctivas",
    "tecnicos",
    "tipos_formatos",
    "usuarios",
    "usuarios_permisos",
)


def upgrade() -> None:
    tables = ", ".join(f"'{table}'" for table in APP_TABLES)
    op.execute(
        f"""
        DO $$
        DECLARE
            table_name text;
            app_tables text[] := ARRAY[{tables}];
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sga_app') THEN
                REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM sga_app;
                REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM sga_app;
                ALTER DEFAULT PRIVILEGES IN SCHEMA public
                    REVOKE ALL ON TABLES FROM sga_app;
                ALTER DEFAULT PRIVILEGES IN SCHEMA public
                    REVOKE ALL ON SEQUENCES FROM sga_app;

                FOREACH table_name IN ARRAY app_tables LOOP
                    IF to_regclass(format('public.%I', table_name)) IS NOT NULL THEN
                        EXECUTE format(
                            'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.%I TO sga_app',
                            table_name
                        );
                    END IF;
                END LOOP;

                GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sga_app;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    pass
