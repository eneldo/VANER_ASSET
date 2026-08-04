#!/bin/sh
set -eu

if [ -z "${POSTGRES_APP_PASSWORD:-}" ]; then
    echo "POSTGRES_APP_PASSWORD es obligatoria" >&2
    exit 1
fi

psql -v ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --set=app_password="$POSTGRES_APP_PASSWORD" <<'SQL'
SELECT 'CREATE ROLE sga_app NOINHERIT LOGIN NOCREATEDB NOCREATEROLE NOSUPERUSER NOBYPASSRLS'
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sga_app')
\gexec

ALTER ROLE sga_app PASSWORD :'app_password';
SELECT format('GRANT CONNECT ON DATABASE %I TO sga_app', current_database())
\gexec
GRANT USAGE ON SCHEMA public TO sga_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sga_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO sga_app;
SQL
