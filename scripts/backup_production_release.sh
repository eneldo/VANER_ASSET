#!/bin/bash
set -euo pipefail
umask 077

PROJECT_DIR="${PROJECT_DIR:-/opt/sga_saas}"
COMPOSE_FILE="${COMPOSE_FILE:-$PROJECT_DIR/docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env}"
RELEASE_ID="${1:-sga-release-$(date +%Y%m%d-%H%M%S)}"
DESTINATION_ROOT="${DESTINATION_ROOT:-/opt/sga_backups/releases}"
DESTINATION="$DESTINATION_ROOT/$RELEASE_ID"

cd "$PROJECT_DIR"

test -f "$COMPOSE_FILE" || { echo "No existe $COMPOSE_FILE" >&2; exit 1; }
test -f "$ENV_FILE" || { echo "No existe $ENV_FILE" >&2; exit 1; }
command -v docker >/dev/null || { echo "Docker no esta disponible" >&2; exit 1; }
command -v openssl >/dev/null || { echo "OpenSSL no esta disponible" >&2; exit 1; }

mkdir -p "$DESTINATION"
chmod 700 "$DESTINATION"

set -a
. "$ENV_FILE"
set +a

: "${POSTGRES_USER:?POSTGRES_USER es obligatorio}"
: "${POSTGRES_DB:?POSTGRES_DB es obligatorio}"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config --quiet
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps --format json > "$DESTINATION/compose-status.json"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" images --format json > "$DESTINATION/compose-images.json"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
    pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl \
    > "$DESTINATION/database.dump"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T postgres \
    pg_restore --list < "$DESTINATION/database.dump" \
    > "$DESTINATION/database.catalog.txt"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T backend \
    tar -C /app -czf - uploads > "$DESTINATION/uploads.tar.gz"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T backend \
    tar -C /app -czf - backups > "$DESTINATION/application-backups.tar.gz"

cp "$COMPOSE_FILE" "$DESTINATION/docker-compose.prod.yml"
cp "$PROJECT_DIR/Caddyfile" "$DESTINATION/Caddyfile"
cp "$PROJECT_DIR/deploy.sh" "$DESTINATION/deploy.sh"
cp "$PROJECT_DIR/.env.example" "$DESTINATION/.env.example"

read -r -s -p "Contrasena para cifrar la copia de .env: " ENV_BACKUP_PASSPHRASE
echo
test -n "$ENV_BACKUP_PASSPHRASE" || { echo "La contrasena no puede estar vacia" >&2; exit 1; }
printf '%s' "$ENV_BACKUP_PASSPHRASE" | openssl enc -aes-256-cbc -pbkdf2 -salt \
    -in "$ENV_FILE" -out "$DESTINATION/environment.env.enc" -pass stdin
unset ENV_BACKUP_PASSPHRASE

if test -d "$PROJECT_DIR/.git"; then
    git -C "$PROJECT_DIR" rev-parse HEAD > "$DESTINATION/git-head.txt"
    git -C "$PROJECT_DIR" describe --tags --always --dirty > "$DESTINATION/git-version.txt"
fi

find "$DESTINATION" -maxdepth 1 -type f ! -name SHA256SUMS -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    > "$DESTINATION/SHA256SUMS"

chmod 600 "$DESTINATION"/*
echo "Respaldo creado en $DESTINATION"
echo "Copie este directorio a almacenamiento externo antes de modificar produccion."
