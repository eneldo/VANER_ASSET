\set ON_ERROR_STOP on

-- Ejecutar como propietario de la base:
-- psql "$MIGRATION_DATABASE_URL" -v app_password="..." -v backup_password="..." -f sql/provision_app_role.sql

SELECT 'CREATE ROLE sga_app NOINHERIT LOGIN NOCREATEDB NOCREATEROLE NOSUPERUSER NOBYPASSRLS'
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sga_app')
\gexec

SELECT 'CREATE ROLE sga_backup INHERIT LOGIN NOCREATEDB NOCREATEROLE NOSUPERUSER BYPASSRLS CONNECTION LIMIT 2'
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sga_backup')
\gexec

ALTER ROLE sga_app PASSWORD :'app_password';
ALTER ROLE sga_app NOINHERIT NOCREATEDB NOCREATEROLE NOSUPERUSER NOBYPASSRLS NOREPLICATION;
ALTER ROLE sga_backup PASSWORD :'backup_password';
ALTER ROLE sga_backup INHERIT NOCREATEDB NOCREATEROLE NOSUPERUSER BYPASSRLS NOREPLICATION CONNECTION LIMIT 2;
ALTER ROLE sga_backup SET default_transaction_read_only = on;
SELECT format('GRANT CONNECT ON DATABASE %I TO sga_app', current_database())
\gexec
SELECT format('GRANT CONNECT ON DATABASE %I TO sga_backup', current_database())
\gexec
GRANT USAGE ON SCHEMA public TO sga_app;
GRANT pg_read_all_data TO sga_backup;
REVOKE CREATE ON SCHEMA public FROM sga_backup;

REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM sga_app;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM sga_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM sga_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM sga_app;

DO $$
DECLARE
    table_name text;
    app_tables text[] := ARRAY[
        'auditoria_eventos', 'auditoria_pro_eventos', 'auditoria_sistema',
        'automatizacion_logs', 'automatizaciones', 'backup_historial',
        'bitacoras_dinamicas', 'bitacoras_respuestas', 'categorias',
        'configuracion_saas', 'configuracion_sistema', 'usuario_empresas',
        'devops_eventos', 'empresas', 'equipo_hoja_vida', 'equipos',
        'evidencias', 'facturas', 'formatos_campos', 'formatos_mantenimiento',
        'hist_mantenimiento', 'historial_mantenimiento', 'login_intentos',
        'logs_sistema', 'mantenimientos', 'monitor_estado', 'notificaciones',
        'ot_incidencias', 'ot_repuestos', 'password_reset_tokens',
        'permisos_sistema', 'plantillas_reporte', 'refresh_tokens',
        'reportes_publicados', 'roles_permisos', 'roles_sistema',
        'scheduler_inteligente_logs', 'scheduler_reglas_mantenimiento',
        'scheduler_sugerencias_mantenimiento', 'sedes', 'seguridad_eventos',
        'smtp_logs', 'solicitudes_correctivas', 'tecnicos', 'tipos_formatos',
        'usuarios', 'usuarios_permisos'
    ];
BEGIN
    FOREACH table_name IN ARRAY app_tables LOOP
        IF to_regclass(format('public.%I', table_name)) IS NOT NULL THEN
            EXECUTE format(
                'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.%I TO sga_app',
                table_name
            );
        END IF;
    END LOOP;
END $$;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO sga_app;
