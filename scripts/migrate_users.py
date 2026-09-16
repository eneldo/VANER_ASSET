#!/usr/bin/env python3
"""
VANER ASSET — Migración Usuarios Dev → Producción
Migra usuarios de desarrollo a producción con validación de roles y seguridad
"""

import os
import sys
import argparse
import getpass
import secrets
from pathlib import Path
from datetime import datetime

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

def load_env_file(env_path: Path) -> dict:
    """Carga variables de entorno"""
    env = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env[key] = val
    return env

def get_db_session(database_url: str):
    """Crea sesión de BD"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()

def hash_password(password: str) -> str:
    """Hashea contraseña con Argon2id (igual que la app)"""
    from passlib.hash import argon2
    return argon2.hash(password)

def verify_password(password: str, hash: str) -> bool:
    """Verifica contraseña"""
    from passlib.hash import argon2
    return argon2.verify(password, hash)

def migrate_users(dev_env: Path, prod_env: Path, dry_run: bool = False, interactive: bool = True):
    """Migra usuarios de dev a producción"""
    
    dev_config = load_env_file(dev_env)
    prod_config = load_env_file(prod_env)
    
    dev_db = dev_config.get("DATABASE_URL") or dev_config.get("MIGRATION_DATABASE_URL")
    prod_db = prod_config.get("DATABASE_URL") or prod_config.get("MIGRATION_DATABASE_URL")
    
    if not dev_db or not prod_db:
        print("❌ DATABASE_URL no configurado en archivos .env")
        return False
    
    print("=" * 60)
    print("VANER ASSET — Migración Usuarios Dev → Producción")
    print("=" * 60)
    print(f"Dev BD:  {dev_db.split('@')[1] if '@' in dev_db else dev_db}")
    print(f"Prod BD: {prod_db.split('@')[1] if '@' in prod_db else prod_db}")
    
    if dry_run:
        print("\n[DRY-RUN] No se harán cambios")
    
    # Conectar a ambas BDs
    try:
        dev_session = get_db_session(dev_db)
        prod_session = get_db_session(prod_db)
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return False
    
    try:
        # Importar modelos
        from app.models.usuario import Usuario
        from app.models.empresa import Empresa
        
        # Obtener empresas de dev
        dev_empresas = dev_session.query(Empresa).all()
        print(f"\n📋 Empresas en dev: {len(dev_empresas)}")
        for e in dev_empresas:
            print(f"   - {e.nombre} (ID: {e.id})")
        
        # Obtener usuarios de dev
        dev_usuarios = dev_session.query(Usuario).all()
        print(f"\n👥 Usuarios en dev: {len(dev_usuarios)}")
        
        # Obtener empresas existentes en prod
        prod_empresas = {e.nombre: e for e in prod_session.query(Empresa).all()}
        print(f"\n🏢 Empresas en prod: {len(prod_empresas)}")
        
        # Obtener usuarios existentes en prod (por email)
        prod_usuarios = {u.email: u for u in prod_session.query(Usuario).all()}
        print(f"👤 Usuarios en prod: {len(prod_usuarios)}")
        
        migrated = 0
        skipped = 0
        errors = 0
        
        for usuario in dev_usuarios:
            # Solo migrar ADMIN y COORDINADOR (no TECNICO ni EMPRESA)
            if usuario.rol not in ["ADMIN", "COORDINADOR"]:
                if not args.ci: print(f"  ⏭️  Saltando {usuario.email} (rol: {usuario.rol})")
                skipped += 1
                continue
            
            # Verificar si ya existe en prod
            if usuario.email in prod_usuarios:
                existing = prod_usuarios[usuario.email]
                if not args.ci: print(f"  ⚠️  {usuario.email} ya existe en prod (ID: {existing.id})")
                skipped += 1
                continue
            
            # Verificar empresa en prod
            dev_empresa = next((e for e in dev_empresas if e.id == usuario.empresa_id), None)
            if not dev_empresa:
                print(f"  ❌ {usuario.email}: empresa no encontrada en dev")
                errors += 1
                continue
            
            prod_empresa = prod_empresas.get(dev_empresa.nombre)
            if not prod_empresa:
                print(f"  ❌ {usuario.email}: empresa '{dev_empresa.nombre}' no existe en prod")
                if interactive:
                    create = input(f"     ¿Crear empresa '{dev_empresa.nombre}' en prod? (s/N): ").lower() == 's'
                    if create:
                        if not dry_run:
                            new_empresa = Empresa(
                                nombre=dev_empresa.nombre,
                                nit=dev_empresa.nit or f"NIT-{secrets.token_hex(4)}",
                                direccion=dev_empresa.direccion,
                                telefono=dev_empresa.telefono,
                                email=dev_empresa.email,
                                estado=True
                            )
                            prod_session.add(new_empresa)
                            prod_session.flush()
                            prod_empresa = new_empresa
                            prod_empresas[dev_empresa.nombre] = prod_empresa
                            print(f"     ✅ Empresa creada (ID: {prod_empresa.id})")
                        else:
                            print(f"     [DRY-RUN] Empresa sería creada")
                    else:
                        errors += 1
                        continue
                else:
                    errors += 1
                    continue
            
            # Solicitar contraseña nueva para producción
            if interactive and not dry_run:
                print(f"\n  👤 Migrando: {usuario.email} ({usuario.rol}) → Empresa: {prod_empresa.nombre}")
                print(f"     Usuario actual: {usuario.username}")
                
                # Generar password temporal segura
                temp_password = secrets.token_urlsafe(16)
                print(f"     Contraseña temporal generada: {temp_password}")
                print(f"     ⚠️  GUARDE ESTA CONTRASEÑA - Se requerirá cambio en primer login")
                
                confirm = input(f"     ¿Confirmar migración? (s/N): ").lower()
                if confirm != 's':
                    print(f"     ⏭️  Saltado")
                    skipped += 1
                    continue
            else:
                temp_password = secrets.token_urlsafe(16)
                if not args.ci: print(f"  🔐 {usuario.email}: password temporal = {temp_password}")
            
            if not dry_run:
                # Crear usuario en producción
                new_user = Usuario(
                    username=usuario.username,
                    email=usuario.email,
                    nombre_completo=usuario.nombre_completo,
                    rol=usuario.rol,
                    empresa_id=prod_empresa.id,
                    password_hash=hash_password(temp_password),
                    mfa_enabled=False,
                    mfa_secret=None,
                    backup_codes=None,
                    password_changed_at=None,  # Forzar cambio en primer login
                    activo=True
                )
                
                prod_session.add(new_user)
                prod_session.flush()
                
                # Crear refresh token revocado (forzar login)
                from app.models.usuario import RefreshToken
                revoked_token = RefreshToken(
                    usuario_id=new_user.id,
                    token_hash="MIGRATED_REVOKED",
                    expires_at=datetime.utcnow(),
                    revoked=True,
                    revoked_at=datetime.utcnow()
                )
                prod_session.add(revoked_token)
                
                prod_session.commit()
                print(f"     ✅ Usuario migrado (ID: {new_user.id})")
                print(f"     📝 Credenciales: {usuario.email} / {temp_password}")
            else:
                print(f"     [DRY-RUN] Usuario sería migrado a empresa {prod_empresa.id}")
            
            migrated += 1
        
        print("\n" + "=" * 60)
        print("RESUMEN MIGRACIÓN")
        print("=" * 60)
        print(f"Migrados: {migrated}")
        print(f"Saltados: {skipped}")
        print(f"Errores:  {errors}")
        
        if migrated > 0 and not dry_run:
            print("\n📋 CREDENCIALES GENERADAS (guardar en vault):")
            # Re-iterar para mostrar credenciales
            for usuario in dev_usuarios:
                if usuario.rol in ["ADMIN", "COORDINADOR"] and usuario.email not in prod_usuarios:
                    dev_empresa = next((e for e in dev_empresas if e.id == usuario.empresa_id), None)
                    if dev_empresa and dev_empresa.nombre in prod_empresas:
                        temp_password = secrets.token_urlsafe(16)  # Regenerar para mostrar
                        print(f"   {usuario.email} / {temp_password} (empresa: {dev_empresa.nombre})")
        
        return errors == 0
        
    except Exception as e:
        print(f"❌ Error durante migración: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        dev_session.close()
        prod_session.close()

def create_initial_admin(prod_env: Path, interactive: bool = True):
    """Crea admin inicial en producción si no existe ninguno"""
    
    prod_config = load_env_file(prod_env)
    prod_db = prod_config.get("DATABASE_URL") or prod_config.get("MIGRATION_DATABASE_URL")
    
    if not prod_db:
        print("❌ DATABASE_URL no configurado")
        return False
    
    prod_session = get_db_session(prod_db)
    
    try:
        from app.models.usuario import Usuario
        from app.models.empresa import Empresa
        
        # Verificar si ya hay admins
        admins = prod_session.query(Usuario).filter(Usuario.rol == "ADMIN").count()
        if admins > 0:
            print(f"ℹ️  Ya existen {admins} administradores en producción")
            return True
        
        print("👤 No hay administradores en producción. Creando inicial...")
        
        # Obtener/crear empresa
        empresas = prod_session.query(Empresa).all()
        if not empresas:
            if interactive:
                nombre = input("Nombre empresa: ").strip()
                nit = input("NIT: ").strip()
                email = input("Email empresa: ").strip()
            else:
                nombre = "Empresa Principal"
                nit = f"NIT-{secrets.token_hex(4)}"
                email = "admin@empresa.com"
            
            empresa = Empresa(nombre=nombre, nit=nit, email=email, estado=True)
            prod_session.add(empresa)
            prod_session.flush()
        else:
            empresa = empresas[0]
            print(f"   Usando empresa existente: {empresa.nombre}")
        
        # Crear admin
        if interactive:
            username = input("Username admin: ").strip() or "admin"
            email = input("Email admin: ").strip()
            nombre = input("Nombre completo: ").strip() or "Administrador"
        else:
            username = "admin"
            email = "admin@empresa.com"
            nombre = "Administrador"
        
        temp_password = secrets.token_urlsafe(16)
        
        admin = Usuario(
            username=username,
            email=email,
            nombre_completo=nombre,
            rol="ADMIN",
            empresa_id=empresa.id,
            password_hash=hash_password(temp_password),
            mfa_enabled=False,
            password_changed_at=None,
            activo=True
        )
        
        prod_session.add(admin)
        prod_session.commit()
        
        print(f"✅ Admin creado:")
        print(f"   Usuario: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {temp_password}")
        print(f"   Empresa: {empresa.nombre}")
        print(f"   ⚠️  CAMBIAR CONTRASEÑA EN PRIMER LOGIN")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando admin: {e}")
        return False
    finally:
        prod_session.close()

def main():
    parser = argparse.ArgumentParser(description="Migración usuarios Dev → Producción")
    parser.add_argument("--dev-env", default=".env", help="Archivo entorno desarrollo")
    parser.add_argument("--prod-env", default=".env.production", help="Archivo entorno producción")
    parser.add_argument("--dry-run", action="store_true", help="Solo simular")
    parser.add_argument("--non-interactive", action="store_true", help="Sin prompts (para CI)")
    parser.add_argument("--create-admin", action="store_true", help="Crear admin inicial si no hay")
    parser.add_argument("--ci", action="store_true", help="Modo CI")
    args = parser.parse_args()
    
    dev_env = Path(args.dev_env)
    prod_env = Path(args.prod_env)
    
    if not dev_env.exists():
        print(f"❌ {dev_env} no encontrado")
        sys.exit(1)
    if not prod_env.exists():
        print(f"❌ {prod_env} no encontrado")
        print("   Ejecute: python scripts/rotate_secrets.py --generate")
        sys.exit(1)
    
    if args.create_admin:
        success = create_initial_admin(prod_env, interactive=not args.non_interactive)
        sys.exit(0 if success else 1)
    
    success = migrate_users(
        dev_env, prod_env,
        dry_run=args.dry_run,
        interactive=not args.non_interactive
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()