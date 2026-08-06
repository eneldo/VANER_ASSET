#!/bin/bash
# ============================================================
# SGA SaaS - Script de despliegue en VPS con Caddy
# Ejecutar como root o usuario con acceso a docker
# ============================================================
set -euo pipefail

DOMAIN="sgaholding.online"
PROJECT_DIR="/opt/sga_saas"          # <-- Ajusta si es distinto
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"

echo "=============================================="
echo " SGA SaaS - Despliegue con Caddy"
echo " Dominio: $DOMAIN"
echo "=============================================="

# --- 1. Requisitos ---
echo ""
echo "[1/6] Verificando Docker..."
docker --version || { echo "Docker no está instalado"; exit 1; }
docker compose version || { echo "docker compose no disponible"; exit 1; }

echo "[2/6] Creando red de Caddy si no existe..."
docker network inspect caddy_net >/dev/null 2>&1 \
  || docker network create caddy_net

# --- 2. Copiar Caddyfile y recargar Caddy ---
echo "[3/6] Configurando Caddy..."
mkdir -p /etc/caddy
cp "$PROJECT_DIR/Caddyfile" /etc/caddy/Caddyfile

# Verificar si Caddy está corriendo, si no, levantarlo
if docker ps --format '{{.Names}}' | grep -q "^caddy$"; then
  echo "  -> Caddy corriendo, recargando configuración..."
  docker exec caddy caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
else
  echo "  -> Iniciando Caddy por primera vez..."
  docker run -d \
    --name caddy \
    --restart always \
    --network caddy_net \
    -p 80:80 -p 443:443 \
    -v /etc/caddy/Caddyfile:/etc/caddy/Caddyfile:ro \
    -v /etc/caddy/data:/data \
    -v /etc/caddy/config:/config \
    -v /var/log/caddy:/var/log/caddy \
    caddy:latest
fi

# --- 3. .env de producción ---
echo "[4/6] Verificando .env de producción..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "  -> Generando .env desde .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"

    # Abrir para que el usuario edite manualmente las contraseñas y SECRET_KEY
    echo ""
    echo ">>> ATENCIÓN: Edita $PROJECT_DIR/.env antes de continuar"
    echo "    Cambia: POSTGRES_PASSWORD, POSTGRES_APP_PASSWORD, SECRET_KEY"
    echo "    Verifica: BACKEND_CORS_ORIGINS = https://$DOMAIN"
    read -r -p "Presiona ENTER cuando hayas editado el .env..."
fi

# --- 5. Build y Deploy ---
echo "[5/6] Construyendo y desplegando contenedores..."

# Pasar VITE_API_URL al build del frontend
export VITE_API_URL="/api"

docker compose -f "$COMPOSE_FILE" build --no-cache
docker compose -f "$COMPOSE_FILE" up -d

# --- 6. Verificación ---
echo ""
echo "[6/6] Verificando estado..."
sleep 5

echo ""
echo "Contenedores:"
echo "-------------"
docker compose -f "$COMPOSE_FILE" ps

echo ""
echo "Logs recientes del backend (últimas 15 líneas):"
echo "-----------------------------------------------"
docker compose -f "$COMPOSE_FILE" logs --tail=15 backend

echo ""
echo "=============================================="
echo " Despliegue completado!!"
echo " URL: https://$DOMAIN"
echo " API: https://$DOMAIN/api"
echo "=============================================="
echo ""
echo "Para ver logs en vivo:"
echo "  docker compose -f $COMPOSE_FILE logs -f"
echo ""
echo "Para reiniciar:"
echo "  docker compose -f $COMPOSE_FILE up -d --force-recreate"
