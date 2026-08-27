#!/usr/bin/env python3
"""
VANER ASSET — Redis Setup Script
Inicia Redis usando Docker o proporciona instrucciones de instalación.

Uso:
    python scripts/setup_redis.py          # Intenta iniciar Redis
    python scripts/setup_redis.py --check  # Solo verifica estado
"""

import os
import sys
import subprocess
import argparse

REDIS_CONTAINER = "vaner_asset_redis"
REDIS_PORT = 6379
REDIS_PASSWORD = "vaner_redis_2026"


def check_redis_running():
    """Verifica si Redis ya está corriendo."""
    try:
        result = subprocess.run(
            ["redis-cli", "-p", str(REDIS_PORT), "ping"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() == "PONG"
    except FileNotFoundError:
        return False
    except Exception:
        return False


def check_docker_available():
    """Verifica si Docker está disponible."""
    try:
        result = subprocess.run(
            ["docker", "version"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def start_redis_docker():
    """Inicia Redis usando Docker."""
    print("Iniciando Redis con Docker...")

    # Verificar si el contenedor ya existe
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={REDIS_CONTAINER}", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )

    if REDIS_CONTAINER in result.stdout:
        # Contenedor existe, iniciarlo
        subprocess.run(["docker", "start", REDIS_CONTAINER], check=True)
        print(f"  Contenedor {REDIS_CONTAINER} iniciado")
    else:
        # Crear nuevo contenedor
        subprocess.run([
            "docker", "run", "-d",
            "--name", REDIS_CONTAINER,
            "-p", f"{REDIS_PORT}:6379",
            "-e", f"REDIS_PASSWORD={REDIS_PASSWORD}",
            "redis:7.4-alpine",
            "redis-server",
            "--requirepass", REDIS_PASSWORD,
        ], check=True)
        print(f"  Contenedor {REDIS_CONTAINER} creado")

    # Verificar que Redis esté respondiendo
    import time
    time.sleep(2)

    try:
        result = subprocess.run(
            ["docker", "exec", REDIS_CONTAINER, "redis-cli", "-a", REDIS_PASSWORD, "ping"],
            capture_output=True, text=True
        )
        if "PONG" in result.stdout:
            print("  Redis está funcionando correctamente")
            return True
    except Exception as e:
        print(f"  Error verificando Redis: {e}")

    return False


def print_windows_instructions():
    """Imprime instrucciones para instalar Redis en Windows."""
    print("""
============================================================
           INSTALACION DE REDIS EN WINDOWS
============================================================

Opcion 1: Memurai Developer (Recomendado)
  1. Descargar: https://www.memurai.com/download
  2. Instalar con valores por defecto
  3. Ejecutar: memurai-cli ping
  4. Respuesta esperada: PONG

Opcion 2: Docker Desktop
  1. Abrir Docker Desktop
  2. Ejecutar: python scripts/setup_redis.py

Opcion 3: WSL (Windows Subsystem for Linux)
  1. wsl --install -d Ubuntu
  2. sudo apt update && sudo apt install redis-server
  3. sudo service redis-server start
  4. redis-cli ping

============================================================
    """)


def create_env_config():
    """Crea configuración para .env."""
    env_content = f"""
# =====================================================
# REDIS CONFIGURATION
# =====================================================
# Para desarrollo local con Docker:
REDIS_URL=redis://:{REDIS_PASSWORD}@localhost:{REDIS_PORT}/0
RATE_LIMIT_REDIS_REQUIRED=false

# Para producción (descomentar):
# RATE_LIMIT_REDIS_REQUIRED=true
"""
    print("\nConfiguración para .env:")
    print(env_content)
    print("Copia estas líneas a tu archivo .env")


def main():
    parser = argparse.ArgumentParser(description="VANER ASSET — Redis Setup")
    parser.add_argument("--check", action="store_true", help="Solo verifica estado")
    parser.add_argument("--install-instructions", action="store_true", help="Muestra instrucciones")
    args = parser.parse_args()

    print("=" * 60)
    print("VANER ASSET — Redis Setup")
    print("=" * 60)

    if args.install_instructions:
        print_windows_instructions()
        return

    # Verificar si Redis ya está corriendo
    print("\n[1/3] Verificando Redis...")
    if check_redis_running():
        print("  Redis ya está corriendo en puerto", REDIS_PORT)
        create_env_config()
        return

    # Verificar Docker
    print("\n[2/3] Verificando Docker...")
    if check_docker_available():
        print("  Docker disponible")
        if args.check:
            print("  Redis no está corriendo")
            return

        if start_redis_docker():
            create_env_config()
            return
    else:
        print("  Docker no disponible")

    # Instrucciones manuales
    print("\n[3/3] Redis no disponible")
    print_windows_instructions()
    print("\nAlternativa: Configurar RATE_LIMIT_REDIS_REQUIRED=false en .env")
    print("El sistema usará rate limiting in-memory (aceptable para desarrollo)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
