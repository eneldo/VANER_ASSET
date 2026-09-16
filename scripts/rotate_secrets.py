#!/usr/bin/env python3
"""
VANER ASSET — Rotación de Secrets para Producción
Genera claves criptográficamente seguras y actualiza .env.production
"""

import os
import secrets
import base64
from pathlib import Path
from cryptography.fernet import Fernet

ENV_PRODUCTION = Path(".env.production")
ENV_EXAMPLE = Path(".env.example")

def generate_secret_key(length: int = 64) -> str:
    """Genera SECRET_KEY aleatoria (mínimo 32 chars, recomendado 64)"""
    return secrets.token_urlsafe(length)

def generate_fernet_key() -> str:
    """Genera CONFIG_ENCRYPTION_KEY compatible con Fernet (base64url de 32 bytes)"""
    return Fernet.generate_key().decode()

def generate_password(length: int = 32) -> str:
    """Genera password segura para BD/Redis"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def read_env_example() -> dict:
    """Lee .env.example y extrae claves que necesitan valores"""
    keys = {}
    if ENV_EXAMPLE.exists():
        for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                if val.startswith("CAMBIAR_"):
                    keys[key] = val
    return keys

def create_env_production():
    """Crea .env.production con secrets rotados"""
    
    # Leer plantilla
    template_keys = read_env_example()
    
    # Generar nuevos valores
    new_values = {}
    
    # Secrets críticos - SIEMPRE rotar
    new_values["SECRET_KEY"] = generate_secret_key(64)
    new_values["CONFIG_ENCRYPTION_KEY"] = generate_fernet_key()
    
    # Passwords de base de datos
    new_values["POSTGRES_PASSWORD"] = generate_password(32)
    new_values["POSTGRES_APP_PASSWORD"] = generate_password(32)
    new_values["POSTGRES_BACKUP_PASSWORD"] = generate_password(32)
    
    # Redis
    new_values["REDIS_PASSWORD"] = generate_password(32)
    
    # Construir DATABASE_URL con nuevos passwords
    pg_user = "vaner_app"  # Usuario aplicación (no sga_app)
    pg_backup_user = "vaner_backup"
    db_name = "vaner_asset"
    
    new_values["DATABASE_URL"] = f"postgresql://{pg_user}:{new_values['POSTGRES_APP_PASSWORD']}@postgres:5432/{db_name}"
    new_values["MIGRATION_DATABASE_URL"] = f"postgresql://postgres:{new_values['POSTGRES_PASSWORD']}@postgres:5432/{db_name}"
    new_values["BACKUP_DATABASE_URL"] = f"postgresql://{pg_backup_user}:{new_values['POSTGRES_BACKUP_PASSWORD']}@postgres:5432/{db_name}"
    new_values["REDIS_URL"] = f"redis://:{new_values['REDIS_PASSWORD']}@redis:6379/0"
    
    # Configuración de producción
    new_values["APP_ENV"] = "production"
    new_values["DEBUG"] = "false"
    new_values["REFRESH_COOKIE_SECURE"] = "true"
    new_values["REFRESH_COOKIE_SAMESITE"] = "lax"
    new_values["RATE_LIMIT_REDIS_REQUIRED"] = "true"
    new_values["BACKUP_ENCRYPTION_REQUIRED"] = "true"
    new_values["RUN_MIGRATIONS"] = "false"
    new_values["RUN_SCHEDULER"] = "true"
    new_values["ALLOW_DATABASE_RESTORE"] = "false"
    
    # Valores que el usuario DEBE configurar (dominios, emails, etc.)
    required_manual = {
        "APP_DOMAIN": "TU_DOMINIO_PRODUCCION.COM",
        "CLIENT_CODE": "CODIGO_CLIENTE",
        "CLIENT_NAME": "NOMBRE_CLIENTE",
        "BACKEND_CORS_ORIGINS": "https://TU_DOMINIO_PRODUCCION.COM",
        "FRONTEND_URL": "https://TU_DOMINIO_PRODUCCION.COM",
        "BOOTSTRAP_ADMIN_TOKEN": "",  # Generar si se usa bootstrap
        "SENTRY_DSN": "",  # Opcional
        "S3_BACKUP_ENABLED": "false",
        "S3_BACKUP_ENDPOINT_URL": "",
        "S3_BACKUP_BUCKET": "",
        "S3_BACKUP_ACCESS_KEY_ID": "",
        "S3_BACKUP_SECRET_ACCESS_KEY": "",
    }
    
    # Leer .env.example completo para mantener estructura
    if ENV_EXAMPLE.exists():
        content = ENV_EXAMPLE.read_text(encoding="utf-8")
    else:
        content = ""
    
    # Reemplazar valores CAMBIAR_* y agregar nuevos
    lines = content.splitlines()
    output_lines = []
    seen_keys = set()
    
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=")[0]
            if key in new_values:
                output_lines.append(f"{key}={new_values[key]}")
                seen_keys.add(key)
            elif key in required_manual:
                output_lines.append(f"{key}={required_manual[key]}")
                seen_keys.add(key)
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)
    
    # Agregar claves faltantes al final
    for key, val in {**new_values, **required_manual}.items():
        if key not in seen_keys:
            output_lines.append(f"{key}={val}")
    
    final_content = "\n".join(output_lines) + "\n"
    ENV_PRODUCTION.write_text(final_content)
    
    print(f"[OK] Creado {ENV_PRODUCTION}")
    print("\n[SECRETS] SECRETS GENERADOS (guardar en vault/gestor de secrets):")
    print(f"   SECRET_KEY={new_values['SECRET_KEY']}")
    print(f"   CONFIG_ENCRYPTION_KEY={new_values['CONFIG_ENCRYPTION_KEY']}")
    print(f"   POSTGRES_PASSWORD={new_values['POSTGRES_PASSWORD']}")
    print(f"   POSTGRES_APP_PASSWORD={new_values['POSTGRES_APP_PASSWORD']}")
    print(f"   POSTGRES_BACKUP_PASSWORD={new_values['POSTGRES_BACKUP_PASSWORD']}")
    print(f"   REDIS_PASSWORD={new_values['REDIS_PASSWORD']}")
    print("\n[WARN] CONFIGURAR MANUALMENTE:")
    for key, val in required_manual.items():
        if val:
            print(f"   {key}={val}")
        else:
            print(f"   {key}=<REQUERIDO>")

def verify_env_production():
    """Verifica que .env.production no tenga placeholders"""
    if not ENV_PRODUCTION.exists():
        print("[ERROR] .env.production no existe")
        return False
    
    # Try UTF-8 first, fallback to latin-1
    try:
        content = ENV_PRODUCTION.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = ENV_PRODUCTION.read_text(encoding="latin-1")
    issues = []
    
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            if "CAMBIAR_" in val or "TU_DOMINIO" in val or "CODIGO_CLIENTE" in val or "NOMBRE_CLIENTE" in val:
                issues.append(f"{key}={val}")
    
    if issues:
        print("[ERROR] Placeholders pendientes en .env.production:")
        for issue in issues:
            print(f"   {issue}")
        return False
    
    # Verificar secrets críticos presentes
    critical = ["SECRET_KEY", "CONFIG_ENCRYPTION_KEY", "POSTGRES_PASSWORD", "POSTGRES_APP_PASSWORD", "POSTGRES_BACKUP_PASSWORD", "REDIS_PASSWORD"]
    missing = [k for k in critical if f"{k}=" not in content]
    if missing:
        print(f"[ERROR] Secrets críticos faltantes: {missing}")
        return False
    
    print("[OK] .env.production verificado - listo para produccion")
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Rotación de secrets para producción")
    parser.add_argument("--generate", action="store_true", help="Generar nuevo .env.production")
    parser.add_argument("--verify", action="store_true", help="Verificar .env.production existente")
    args = parser.parse_args()
    
    if args.generate:
        create_env_production()
    elif args.verify:
        verify_env_production()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()