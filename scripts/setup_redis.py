#!/usr/bin/env python3
"""
VANER ASSET — Setup y Configuración Redis para Producción
Instala Redis, configura persistencia, seguridad y valida rate limiting
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

def run_command(cmd: list, capture: bool = True, timeout: int = 60) -> tuple:
    """Ejecuta comando y retorna (success, stdout, stderr)"""
    try:
        result = subprocess.run(cmd, capture_output=capture, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Timeout (> {timeout}s)"
    except Exception as e:
        return False, "", str(e)

def check_redis_installed() -> bool:
    """Verifica si Redis está instalado"""
    success, stdout, _ = run_command(["redis-server", "--version"])
    if success:
        print(f"✅ Redis instalado: {stdout.strip()}")
        return True
    print("❌ Redis no instalado")
    return False

def install_redis_ubuntu() -> bool:
    """Instala Redis en Ubuntu/Debian"""
    print("📦 Instalando Redis...")
    
    commands = [
        ["apt-get", "update"],
        ["apt-get", "install", "-y", "redis-server"],
    ]
    
    for cmd in commands:
        success, stdout, stderr = run_command(cmd, timeout=300)
        if not success:
            print(f"❌ Error: {' '.join(cmd)}")
            print(stderr)
            return False
    
    print("✅ Redis instalado")
    return True

def install_redis_centos() -> bool:
    """Instala Redis en CentOS/RHEL/Rocky"""
    print("📦 Instalando Redis (CentOS/RHEL)...")
    
    commands = [
        ["dnf", "install", "-y", "redis"],
    ]
    
    for cmd in commands:
        success, stdout, stderr = run_command(cmd, timeout=300)
        if not success:
            print(f"❌ Error: {' '.join(cmd)}")
            print(stderr)
            return False
    
    print("✅ Redis instalado")
    return True

def configure_redis(redis_password: str, bind_address: str = "127.0.0.1") -> bool:
    """Configura redis.conf para producción"""
    config_paths = [
        "/etc/redis/redis.conf",
        "/etc/redis.conf",
    ]
    
    config_file = None
    for path in config_paths:
        if Path(path).exists():
            config_file = Path(path)
            break
    
    if not config_file:
        print("❌ No se encontró redis.conf")
        return False
    
    print(f"⚙️  Configurando {config_file}...")
    
    # Backup original
    backup = config_file.with_suffix(".conf.backup")
    if not backup.exists():
        import shutil
        shutil.copy2(config_file, backup)
        print(f"   Backup: {backup}")
    
    # Leer config actual
    content = config_file.read_text()
    
    # Configuraciones de producción
    settings = {
        "bind": f"bind {bind_address}",
        "port": "port 6379",
        "requirepass": f"requirepass {redis_password}",
        "maxmemory": "maxmemory 256mb",
        "maxmemory-policy": "maxmemory-policy allkeys-lru",
        "appendonly": "appendonly yes",
        "appendfilename": 'appendfilename "redis.aof"',
        "appendfsync": "appendfsync everysec",
        "save": 'save 900 1\nsave 300 10\nsave 60 10000',
        "tcp-keepalive": "tcp-keepalive 60",
        "timeout": "timeout 300",
        "databases": "databases 16",
        "loglevel": "loglevel notice",
        "supervised": "supervised systemd",
    }
    
    lines = content.splitlines()
    new_lines = []
    seen_keys = set()
    
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            key = stripped.split()[0] if stripped.split() else ""
            if key in settings:
                new_lines.append(settings[key])
                seen_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Agregar settings faltantes
    for key, val in settings.items():
        if key not in seen_keys:
            new_lines.append(val)
    
    config_file.write_text("\n".join(new_lines) + "\n")
    print("✅ Configuración aplicada")
    return True

def start_redis_service() -> bool:
    """Inicia y habilita servicio Redis"""
    print("🚀 Iniciando servicio Redis...")
    
    commands = [
        ["systemctl", "daemon-reload"],
        ["systemctl", "enable", "redis-server"],
        ["systemctl", "restart", "redis-server"],
    ]
    
    for cmd in commands:
        success, stdout, stderr = run_command(cmd, timeout=30)
        if not success:
            print(f"❌ Error: {' '.join(cmd)}")
            print(stderr)
            return False
    
    # Esperar a que esté listo
    for i in range(10):
        time.sleep(1)
        success, _, _ = run_command(["redis-cli", "ping"])
        if success:
            print("✅ Redis service activo")
            return True
    
    print("❌ Redis no responde después de iniciar")
    return False

def test_redis_connection(redis_url: str) -> bool:
    """Prueba conexión a Redis con URL"""
    try:
        import redis
        r = redis.from_url(redis_url, socket_timeout=5, socket_connect_timeout=5)
        r.ping()
        info = r.info()
        print(f"✅ Conectado a Redis {info.get('redis_version', 'unknown')}")
        print(f"   Memoria: {info.get('used_memory_human', 'N/A')}")
        print(f"   Clientes: {info.get('connected_clients', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Error conectando a Redis: {e}")
        return False

def test_rate_limiting(redis_url: str) -> bool:
    """Prueba rate limiting distribuido con Redis"""
    try:
        import redis
        r = redis.from_url(redis_url)
        
        # Simular rate limit: 10 req/min por key
        key = "ratelimit:test:192.168.1.1"
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        results = pipe.execute()
        
        count = results[0]
        print(f"✅ Rate limiting funcional (request #{count})")
        
        # Limpiar
        r.delete(key)
        return True
    except Exception as e:
        print(f"❌ Error en rate limiting: {e}")
        return False

def update_env_file(env_file: Path, redis_password: str) -> bool:
    """Actualiza .env.production con Redis configurado"""
    if not env_file.exists():
        print(f"❌ {env_file} no existe")
        return False
    
    content = env_file.read_text()
    lines = content.splitlines()
    new_lines = []
    
    for line in lines:
        if line.startswith("REDIS_PASSWORD="):
            new_lines.append(f"REDIS_PASSWORD={redis_password}")
        elif line.startswith("REDIS_URL="):
            new_lines.append(f"REDIS_URL=redis://:{redis_password}@redis:6379/0")
        elif line.startswith("RATE_LIMIT_REDIS_REQUIRED="):
            new_lines.append("RATE_LIMIT_REDIS_REQUIRED=true")
        else:
            new_lines.append(line)
    
    env_file.write_text("\n".join(new_lines) + "\n")
    print(f"✅ Actualizado {env_file}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Setup Redis para producción")
    parser.add_argument("--env-file", default=".env.production", help="Archivo de entorno")
    parser.add_argument("--password", help="Password Redis (se genera si no se da)")
    parser.add_argument("--bind", default="127.0.0.1", help="Dirección bind")
    parser.add_argument("--skip-install", action="store_true", help="Solo configurar, no instalar")
    parser.add_argument("--test-only", action="store_true", help="Solo probar conexión")
    args = parser.parse_args()
    
    print("=" * 60)
    print("VANER ASSET — Setup Redis Producción")
    print("=" * 60)
    
    env_file = Path(args.env_file)
    env = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env[key] = val
    
    redis_password = args.password or env.get("REDIS_PASSWORD")
    if not redis_password:
        import secrets
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        redis_password = ''.join(secrets.choice(alphabet) for _ in range(32))
        print(f"🔐 Password Redis generado: {redis_password}")
    
    if args.test_only:
        redis_url = f"redis://:{redis_password}@localhost:6379/0"
        test_redis_connection(redis_url)
        test_rate_limiting(redis_url)
        return
    
    # Detectar OS
    is_ubuntu = Path("/etc/os-release").exists() and "ubuntu" in Path("/etc/os-release").read_text().lower()
    is_centos = Path("/etc/os-release").exists() and any(x in Path("/etc/os-release").read_text().lower() for x in ["centos", "rhel", "rocky", "almalinux"])
    
    if not args.skip_install:
        if not check_redis_installed():
            if is_ubuntu:
                if not install_redis_ubuntu():
                    sys.exit(1)
            elif is_centos:
                if not install_redis_centos():
                    sys.exit(1)
            else:
                print("❌ OS no soportado para auto-instalación. Instale Redis manualmente.")
                sys.exit(1)
    
    # Configurar
    if not configure_redis(redis_password, args.bind):
        sys.exit(1)
    
    # Iniciar servicio
    if not start_redis_service():
        sys.exit(1)
    
    # Probar
    redis_url = f"redis://:{redis_password}@localhost:6379/0"
    if not test_redis_connection(redis_url):
        sys.exit(1)
    
    if not test_rate_limiting(redis_url):
        sys.exit(1)
    
    # Actualizar .env
    if not update_env_file(env_file, redis_password):
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ REDIS CONFIGURADO PARA PRODUCCIÓN")
    print("=" * 60)
    print(f"\nVariables actualizadas en {env_file}:")
    print(f"   REDIS_PASSWORD={redis_password}")
    print(f"   REDIS_URL=redis://:{redis_password}@redis:6379/0")
    print(f"   RATE_LIMIT_REDIS_REQUIRED=true")
    print("\n⚠️  Reiniciar backend para aplicar cambios")

if __name__ == "__main__":
    main()