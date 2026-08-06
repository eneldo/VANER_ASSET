#!/bin/bash
# ============================================================
# SGA SaaS - Despliegue en VPS con Caddy
# Usa imágenes pre-built de Docker Hub (vanstralhen/sga-*)
# Ejecutar como root o usuario con acceso a docker
# ============================================================
set -euo pipefail

DOMAIN="sgaholding.online"
PROJECT_DIR="/opt/sga_saas"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"
ENV_FILE="$PROJECT_DIR/.env"

cd "$PROJECT_DIR"

echo "=============================================="
echo " SGA SaaS - Despliegue Producción con Caddy"
echo " Dominio: $DOMAIN"
echo " Imágenes: vanstralhen/sga-backend + sga-frontend"
echo "=============================================="

# --- 1. Requisitos ---
echo ""
echo "[1/6] Verificando requisitos..."
docker --version || { echo "ERROR: Docker no está instalado"; exit 1; }
docker compose version || { echo "ERROR: docker compose no disponible"; exit 1; }

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

if docker ps --format '{{.Names}}' | grep -q "^caddy$"; then
  echo "  Caddy ya está corriendo -> recargando..."
  docker exec caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
else
  echo "  Iniciando Caddy..."
  docker run -d \
    --name caddy \
    --restart always \
    --network caddy_net \
    -p 80:80 -p 443:443 \
    -v /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro \
    -v caddy_data:/data \
    -v caddy_config:/config \
    -v /var/log/caddy:/var/log/caddy \
    caddy:latest
fi

# --- 4. .env ---
echo "[4/6] Verificando .env..."
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: No se encontró $ENV_FILE"
  echo "Créalo desde .env.example, configura los secretos y vuelve a ejecutar."
  exit 1
fi

if grep -Eq '(^|=)CAMBIAR_' "$ENV_FILE"; then
  echo "ERROR: $ENV_FILE todavía contiene valores CAMBIAR_*"
  exit 1
fi

# --- 5. Pull + Deploy ---
echo "[5/6] Pull imágenes y desplegar..."
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d

# --- 6. Verificación ---
echo ""
echo "[6/6] Verificando servicios..."
sleep 5

echo ""
echo "Estado de contenedores:"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps

echo ""
echo "Logs recientes backend:"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=20 backend

echo ""
echo "=============================================="
echo "✅ Despliegue completado!"
echo "   https://$DOMAIN"
echo "=============================================="
echo ""
echo "Logs en vivo:  docker compose --env-file $ENV_FILE -f $COMPOSE_FILE logs -f"
echo "Reiniciar:     docker compose --env-file $ENV_FILE -f $COMPOSE_FILE up -d --force-recreate"
