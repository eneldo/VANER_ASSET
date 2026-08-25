#!/bin/sh
set -eu

if [ -z "${POSTGRES_APP_PASSWORD:-}" ]; then
    echo "POSTGRES_APP_PASSWORD es obligatoria" >&2
    exit 1
fi

if [ -z "${POSTGRES_BACKUP_PASSWORD:-}" ]; then
    echo "POSTGRES_BACKUP_PASSWORD es obligatoria" >&2
    exit 1
fi

psql -v ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --set=app_password="$POSTGRES_APP_PASSWORD" \
    --set=backup_password="$POSTGRES_BACKUP_PASSWORD" <<'SQL'
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
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM sga_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM sga_app;
SQL
