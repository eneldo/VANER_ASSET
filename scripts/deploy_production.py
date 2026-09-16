#!/usr/bin/env python3
"""
VANER ASSET — Deploy Orquestador a Producción
Ejecuta toda la secuencia de deploy de forma segura y ordenada
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"

class DeployOrchestrator:
    def __init__(self, env_file=".env.production", skip_steps=None, dry_run=False):
        self.env_file = ROOT / env_file
        self.skip_steps = set(skip_steps or [])
        self.dry_run = dry_run
        self.start_time = datetime.now()
        self.steps_log = []
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARN": "⚠️", "STEP": "🔄"}.get(level, "")
        print(f"[{timestamp}] {prefix} {message}")
    
    def run_script(self, script_name, args=None, description="", required=True) -> bool:
        """Ejecuta un script de la carpeta scripts"""
        if script_name in self.skip_steps:
            self.log(f"SKIP: {script_name} ({description})", "WARN")
            return True
        
        script_path = SCRIPTS / script_name
        if not script_path.exists():
            self.log(f"Script no encontrado: {script_path}", "ERROR")
            return not required
        
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        self.log(f"EJECUTANDO: {script_name} - {description}", "STEP")
        if self.dry_run:
            self.log(f"[DRY-RUN] {' '.join(cmd)}", "INFO")
            return True
        
        start = time.time()
        try:
            result = subprocess.run(cmd, cwd=ROOT, timeout=600)
            elapsed = time.time() - start
            
            if result.returncode == 0:
                self.log(f"COMPLETADO: {script_name} ({elapsed:.1f}s)", "SUCCESS")
                self.steps_log.append({"script": script_name, "status": "success", "time": elapsed})
                return True
            else:
                self.log(f"FALLÓ: {script_name} (exit code: {result.returncode})", "ERROR")
                self.steps_log.append({"script": script_name, "status": "failed", "time": elapsed})
                return False
        except subprocess.TimeoutExpired:
            self.log(f"TIMEOUT: {script_name} (>10 min)", "ERROR")
            return False
        except Exception as e:
            self.log(f"ERROR: {script_name} - {e}", "ERROR")
            return False
    
    def run_command(self, cmd, description="", cwd=None, required=True) -> bool:
        """Ejecuta comando directo"""
        if description in self.skip_steps:
            self.log(f"SKIP: {description}", "WARN")
            return True
        
        self.log(f"EJECUTANDO: {description}", "STEP")
        if self.dry_run:
            self.log(f"[DRY-RUN] {cmd}", "INFO")
            return True
        
        start = time.time()
        try:
            result = subprocess.run(cmd, cwd=cwd or ROOT, shell=isinstance(cmd, str), timeout=300)
            elapsed = time.time() - start
            
            if result.returncode == 0:
                self.log(f"COMPLETADO: {description} ({elapsed:.1f}s)", "SUCCESS")
                return True
            else:
                self.log(f"FALLÓ: {description} (exit code: {result.returncode})", "ERROR")
                return not required
        except Exception as e:
            self.log(f"ERROR: {description} - {e}", "ERROR")
            return not required
    
    def wait_for_service(self, url, name, timeout=60, interval=5):
        """Espera a que un servicio responda"""
        self.log(f"ESPERANDO {name} en {url}...", "STEP")
        if self.dry_run:
            return True
        
        import requests
        start = time.time()
        while time.time() - start < timeout:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    self.log(f"{name} DISPONIBLE", "SUCCESS")
                    return True
            except:
                pass
            time.sleep(interval)
        
        self.log(f"TIMEOUT esperando {name}", "ERROR")
        return False
    
    def deploy(self) -> bool:
        """Ejecuta secuencia completa de deploy"""
        print("=" * 70)
        print("VANER ASSET — DEPLOY A PRODUCCIÓN")
        print("=" * 70)
        print(f"Entorno: {self.env_file.name}")
        print(f"Dry-run: {self.dry_run}")
        print(f"Skip: {', '.join(self.skip_steps) if self.skip_steps else 'ninguno'}")
        print("=" * 70)
        
        # FASE 0: Validaciones previas
        if not self._phase_prechecks():
            return False
        
        # FASE 1: Infraestructura base
        if not self._phase_infrastructure():
            return False
        
        # FASE 2: Base de datos
        if not self._phase_database():
            return False
        
        # FASE 3: Redis
        if not self._phase_redis():
            return False
        
        # FASE 4: Deploy containers
        if not self._phase_containers():
            return False
        
        # FASE 5: Validación post-deploy
        if not self._phase_validation():
            return False
        
        # FASE 6: Usuarios y accesos
        if not self._phase_users():
            return False
        
        # Resumen
        self._print_summary()
        return True
    
    def _phase_prechecks(self) -> bool:
        self.log("FASE 0: PRE-CHECKS", "STEP")
        
        # Verificar .env.production
        if not self.env_file.exists():
            self.log("Generando .env.production...", "STEP")
            if not self.run_script("rotate_secrets.py", ["--generate"], "Generar secrets producción"):
                return False
        
        # Pre-deploy checklist
        if not self.run_script("predeploy_checklist.py", ["--env-file", self.env_file.name], 
                              "Checklist pre-deploy"):
            self.log("Pre-deploy checklist falló. ¿Continuar anyway? (s/N): ", "WARN")
            if not self.dry_run:
                resp = input().lower()
                if resp != 's':
                    return False
        
        return True
    
    def _phase_infrastructure(self) -> bool:
        self.log("FASE 1: INFRAESTRUCTURA BASE", "STEP")
        
        # Verificar Docker
        success, _ = subprocess.run(["docker", "version"], capture_output=True), ""
        if not success[0]:
            self.log("Docker no disponible", "ERROR")
            return False
        
        # Verificar docker-compose
        success, _ = subprocess.run(["docker", "compose", "version"], capture_output=True), ""
        if not success[0]:
            self.log("Docker Compose no disponible", "ERROR")
            return False
        
        # Verificar red externa caddy_net
        success, stdout = subprocess.run(["docker", "network", "ls"], capture_output=True, text=True)
        if "caddy_net" not in stdout:
            self.log("Creando red externa caddy_net...", "STEP")
            if not self.run_command("docker network create caddy_net", "Crear red caddy_net"):
                return False
        
        # Verificar directorios
        for dir_path in ["/opt/vaner_asset", "/opt/vaner_asset/uploads", "/opt/vaner_asset/backups"]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        self.log("Infraestructura base OK", "SUCCESS")
        return True
    
    def _phase_database(self) -> bool:
        self.log("FASE 2: BASE DE DATOS", "STEP")
        
        # Verificar PostgreSQL corriendo
        if not self.run_command("docker compose -f docker-compose.prod.yml up -d postgres", 
                               "Iniciar PostgreSQL"):
            return False
        
        # Esperar PostgreSQL
        time.sleep(10)
        
        # Ejecutar migraciones
        if not self.run_script("migrate_production.py", ["--env-file", self.env_file.name],
                              "Ejecutar migraciones productivas"):
            return False
        
        return True
    
    def _phase_redis(self) -> bool:
        self.log("FASE 3: REDIS", "STEP")
        
        if not self.run_command("docker compose -f docker-compose.prod.yml up -d redis",
                               "Iniciar Redis"):
            return False
        
        time.sleep(5)
        
        # Configurar Redis (password, persistencia, etc.)
        if not self.run_script("setup_redis.py", ["--env-file", self.env_file.name],
                              "Configurar Redis producción"):
            return False
        
        return True
    
    def _phase_containers(self) -> bool:
        self.log("FASE 4: DEPLOY CONTAINERS", "STEP")
        
        # Pull imágenes
        if not self.run_command("docker compose -f docker-compose.prod.yml pull",
                               "Pull imágenes Docker"):
            return False
        
        # Deploy backend + frontend
        if not self.run_command("docker compose -f docker-compose.prod.yml up -d backend frontend",
                               "Iniciar backend y frontend"):
            return False
        
        # Esperar health checks
        time.sleep(15)
        
        # Verificar backend health
        if not self.wait_for_service("http://localhost:8000/health/ready", "Backend /health/ready"):
            self.log("Backend no responde en /health/ready", "ERROR")
            return False
        
        # Verificar frontend
        if not self.wait_for_service("http://localhost:8080/", "Frontend"):
            self.log("Frontend no responde", "ERROR")
            return False
        
        return True
    
    def _phase_validation(self) -> bool:
        self.log("FASE 5: VALIDACIÓN POST-DEPLOY", "STEP")
        
        # Restore drill
        if not self.run_script("restore_drill_auto.py", ["--env-file", self.env_file.name],
                              "Restore drill automático"):
            self.log("Restore drill falló - backup puede no ser válido", "WARN")
        
        # Test E2E básico
        if not self.run_script("test_e2e.py", [], "Tests E2E básicos"):
            self.log("Tests E2E fallaron", "WARN")
        
        # Verificar métricas
        if not self.wait_for_service("http://localhost:8000/metrics", "Backend /metrics", timeout=10):
            self.log("/metrics no disponible", "WARN")
        
        return True
    
    def _phase_users(self) -> bool:
        self.log("FASE 6: USUARIOS Y ACCESOS", "STEP")
        
        # Migrar usuarios de dev si existen
        dev_env = ROOT / ".env"
        if dev_env.exists():
            self.log("Migrando usuarios dev → prod...", "STEP")
            if not self.run_script("migrate_users.py", 
                                  ["--dev-env", ".env", "--prod-env", self.env_file.name, "--non-interactive"],
                                  "Migrar usuarios desarrollo"):
                self.log("Migración usuarios falló - crear admin manual", "WARN")
        
        # Verificar/crear admin inicial
        if not self.run_script("migrate_users.py", 
                              ["--prod-env", self.env_file.name, "--create-admin", "--non-interactive"],
                              "Crear/verificar admin inicial"):
            return False
        
        return True
    
    def _print_summary(self):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "=" * 70)
        print("RESUMEN DEPLOY")
        print("=" * 70)
        print(f"Tiempo total: {elapsed:.1f}s")
        print(f"Pasos ejecutados: {len(self.steps_log)}")
        
        for step in self.steps_log:
            status = "✅" if step["status"] == "success" else "❌"
            print(f"  {status} {step['script']} ({step['time']:.1f}s)")
        
        failed = [s for s in self.steps_log if s["status"] == "failed"]
        if failed:
            print(f"\n{Colors.RED}⚠️  {len(failed)} pasos fallaron - revisar logs{Colors.END}")
        else:
            print(f"\n{Colors.GREEN}🎉 DEPLOY COMPLETADO EXITOSAMENTE{Colors.END}")
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("  1. Configurar DNS → APP_DOMAIN")
        print("  2. Configurar Caddy/SSL")
        print("  3. Probar login con credenciales generadas")
        print("  4. Configurar backups S3 (opcional)")
        print("  5. Configurar SENTRY_DSN (opcional)")
        print("  6. Programar pentest dinámico (2 semanas)")

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    END = '\033[0m'

def main():
    parser = argparse.ArgumentParser(description="Deploy orquestado a producción")
    parser.add_argument("--env-file", default=".env.production", help="Archivo entorno")
    parser.add_argument("--skip", nargs="+", help="Pasos a saltar")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar qué se ejecutaría")
    parser.add_argument("--phase", choices=["prechecks", "infra", "db", "redis", "containers", "validation", "users"],
                       help="Ejecutar solo una fase")
    args = parser.parse_args()
    
    orchestrator = DeployOrchestrator(args.env_file, args.skip, args.dry_run)
    
    if args.phase:
        phase_method = getattr(orchestrator, f"_phase_{args.phase}", None)
        if phase_method:
            success = phase_method()
        else:
            print(f"Fase desconocida: {args.phase}")
            success = False
    else:
        success = orchestrator.deploy()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()