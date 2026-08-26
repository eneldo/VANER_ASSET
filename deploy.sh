#!/bin/bash
# ============================================================
# VANER ASSET - Despliegue en VPS con Caddy
# Usa imagenes pre-built de Docker Hub (vanstralhen/vaner-asset-*)
# Ejecutar como root o usuario con acceso a docker
# ============================================================
set -euo pipefail
umask 077

PROJECT_DIR="${PROJECT_DIR:-/opt/vaner_asset}"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"
ENV_FILE="$PROJECT_DIR/.env"

cd "$PROJECT_DIR"

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: No se encontró $ENV_FILE"
  echo "Créalo desde .env.example, configura los secretos y vuelve a ejecutar."
  exit 1
fi

if grep -Eq '(^|=)CAMBIAR_' "$ENV_FILE"; then
  echo "ERROR: $ENV_FILE todavía contiene valores CAMBIAR_*"
  exit 1
fi

chmod 600 "$ENV_FILE"
set -a
. "$ENV_FILE"
set +a
CADDY_IMAGE="${CADDY_IMAGE:-caddy:2.10.0-alpine}"
APP_DOMAIN="${APP_DOMAIN:-${DOMAIN:-}}"
APP_DOMAIN="${APP_DOMAIN:?APP_DOMAIN es obligatorio}"
BACKEND_IMAGE="${BACKEND_IMAGE:-vanstralhen/vaner-asset-backend}"
FRONTEND_IMAGE="${FRONTEND_IMAGE:-vanstralhen/vaner-asset-frontend}"

on_error() {
  echo "ERROR: el despliegue no terminó correctamente"
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps || true
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=100 || true
}
trap on_error ERR

echo "=============================================="
echo " VANER ASSET - Despliegue Produccion con Caddy"
echo " Dominio: $APP_DOMAIN"
echo " Imagenes: $BACKEND_IMAGE + $FRONTEND_IMAGE"
echo "=============================================="

# --- 1. Requisitos ---
echo ""
echo "[1/6] Verificando requisitos..."
docker --version || { echo "ERROR: Docker no está instalado"; exit 1; }
docker compose version || { echo "ERROR: docker compose no disponible"; exit 1; }
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config --quiet

# --- 2. Red de Caddy ---
echo "[2/6] Preparando red caddy_net..."
docker network inspect caddy_net >/dev/null 2>&1 && echo "  -> caddy_net ya existe" || {
  echo "  -> Creando caddy_net..."
  docker network create caddy_net
}

# --- 3. Caddy ---
echo "[3/6] Configurando Caddy..."
mkdir -p /etc/caddy /var/log/caddy

if [ ! -f "$PROJECT_DIR/Caddyfile" ]; then
  echo "ERROR: No se encontró $PROJECT_DIR/Caddyfile"
  exit 1
fi
cp "$PROJECT_DIR/Caddyfile" /etc/caddy/Caddyfile

docker pull "$CADDY_IMAGE"
docker rm -f vaner_asset_caddy >/dev/null 2>&1 || true
docker run -d \
  --name vaner_asset_caddy \
  -e APP_DOMAIN="$APP_DOMAIN" \
  --restart always \
  --security-opt no-new-privileges \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  --pids-limit 200 \
  --memory 256m \
  --cpus 0.50 \
  --network caddy_net \
  -p 80:80 -p 443:443 \
  -v /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro \
  -v caddy_data:/data \
  -v caddy_config:/config \
  -v /var/log/caddy:/var/log/caddy \
  "$CADDY_IMAGE"

# --- 4. .env ---
echo "[4/6] Variables y permisos de .env verificados"

# --- 5. Pull + Deploy ---
echo "[5/6] Pull imágenes y desplegar..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --remove-orphans --wait --wait-timeout 180

# --- 6. Verificación ---
echo ""
echo "[6/6] Verificando servicios..."
echo ""
echo "Estado de contenedores:"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps

echo ""
echo "Logs recientes backend:"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=20 backend

curl --fail --silent --show-error --retry 8 --retry-delay 3 \
  "https://$APP_DOMAIN/health/ready" >/dev/null

trap - ERR

echo ""
echo "=============================================="
echo "✅ Despliegue completado!"
echo "   https://$APP_DOMAIN"
echo "=============================================="
echo ""
echo "Logs en vivo:  docker compose --env-file $ENV_FILE -f $COMPOSE_FILE logs -f"
echo "Reiniciar:     docker compose --env-file $ENV_FILE -f $COMPOSE_FILE up -d --force-recreate"
