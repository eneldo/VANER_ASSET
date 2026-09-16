#!/usr/bin/env python3
"""
VANER ASSET — Checklist Pre-Deploy Ejecutable
Valida todo lo necesario antes de desplegar a producción
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_check(name, passed, details=""):
    status = f"{Colors.GREEN}[OK] PASS{Colors.END}" if passed else f"{Colors.RED}[FAIL] FAIL{Colors.END}"
    print(f"  {status} {name}")
    if details and not passed:
        print(f"       {Colors.YELLOW}{details}{Colors.END}")

def run_cmd(cmd, cwd=None, capture=True, timeout=60):
    """Ejecuta comando y retorna (success, output)"""
    try:
        result = subprocess.run(
            cmd, cwd=cwd or ROOT, capture_output=capture, text=True, timeout=timeout,
            shell=isinstance(cmd, str)
        )
        return result.returncode == 0, result.stdout if capture else ""
    except subprocess.TimeoutExpired:
        return False, f"Timeout ({timeout}s)"
    except Exception as e:
        return False, str(e)

class PreDeployChecklist:
    def __init__(self, env_file=".env.production", ci_mode=False):
        self.env_file = ROOT / env_file
        self.ci_mode = ci_mode
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "passed": 0,
            "failed": 0,
            "warnings": 0,
        }
    
    def check(self, name, condition, details="", warning=False):
        """Registra un check"""
        passed = bool(condition)
        self.results["checks"][name] = {
            "passed": passed,
            "details": details,
            "warning": warning
        }
        if passed:
            self.results["passed"] += 1
        elif warning:
            self.results["warnings"] += 1
        else:
            self.results["failed"] += 1
        
        if not self.ci_mode:
            print_check(name, passed, details)
        return passed
    
    def run_all(self):
        """Ejecuta todos los checks"""
        if not self.ci_mode:
            print_header("VANER ASSET — PRE-DEPLOY CHECKLIST")
            print(f"Entorno: {self.env_file.name}")
            print(f"Timestamp: {self.results['timestamp']}")
        
        # 1. Archivos de entorno
        self._check_env_files()
        
        # 2. Secrets rotados
        self._check_secrets()
        
        # 3. Configuración Docker
        self._check_docker_config()
        
        # 4. Backend: tests, lint, migraciones
        self._check_backend()
        
        # 5. Frontend: build, lint
        self._check_frontend()
        
        # 6. Scripts de producción
        self._check_production_scripts()
        
        # 7. Seguridad
        self._check_security()
        
        # 8. CI/CD
        self._check_cicd()
        
        # Resumen
        self._print_summary()
        
        return self.results["failed"] == 0
    
    def _check_env_files(self):
        print_header("1. ARCHIVOS DE ENTORNO")
        
        self.check(
            "EXISTE .env.production",
            self.env_file.exists(),
            f"Ejecute: python scripts/rotate_secrets.py --generate"
        )
        
        self.check(
            "EXISTE .env.example",
            (ROOT / ".env.example").exists(),
            "Plantilla de referencia faltante"
        )
        
        self.check(
            "NO EXISTE .env con secrets reales en repo",
            not (ROOT / ".env").exists() or self._env_has_no_real_secrets(ROOT / ".env"),
            "Archivo .env con secrets reales detectado en repo"
        )
        
        self.check(
            "NO EXISTE backend/.env en repo",
            not (ROOT / "backend" / ".env").exists(),
            "backend/.env no debería estar en repo"
        )
    
    def _env_has_no_real_secrets(self, env_path):
        """Verifica que .env no tenga secrets reales"""
        try:
            content = env_path.read_text()
            # Buscar patrones de secrets reales (no placeholders)
            import re
            patterns = [
                r'SECRET_KEY=[^C][^A][^M]',  # No CAMBIAR
                r'CONFIG_ENCRYPTION_KEY=[^C][^A][^M]',
                r'POSTGRES_PASSWORD=[^C][^A][^M]',
                r'POSTGRES_APP_PASSWORD=[^C][^A][^M]',
                r'REDIS_PASSWORD=[^C][^A][^M]',
            ]
            for pattern in patterns:
                if re.search(pattern, content):
                    return False
            return True
        except:
            return True
    
    def _check_secrets(self):
        print_header("2. SECRETS ROTADOS")
        
        if not self.env_file.exists():
            for name in ["SECRET_KEY", "CONFIG_ENCRYPTION_KEY", "POSTGRES_PASSWORD", 
                        "POSTGRES_APP_PASSWORD", "POSTGRES_BACKUP_PASSWORD", "REDIS_PASSWORD"]:
                self.check(f"SECRET {name}", False, "Archivo .env.production no existe")
            return
        
        content = self.env_file.read_text()
        
        critical_secrets = {
            "SECRET_KEY": "SECRET_KEY=",
            "CONFIG_ENCRYPTION_KEY": "CONFIG_ENCRYPTION_KEY=",
            "POSTGRES_PASSWORD": "POSTGRES_PASSWORD=",
            "POSTGRES_APP_PASSWORD": "POSTGRES_APP_PASSWORD=",
            "POSTGRES_BACKUP_PASSWORD": "POSTGRES_BACKUP_PASSWORD=",
            "REDIS_PASSWORD": "REDIS_PASSWORD=",
        }
        
        for name, prefix in critical_secrets.items():
            found = False
            for line in content.splitlines():
                if line.startswith(prefix):
                    val = line.split("=", 1)[1]
                    if val and not val.startswith("CAMBIAR_") and len(val) >= 16:
                        found = True
                        break
            self.check(f"SECRET {name} rotado", found, f"{prefix} falta o es placeholder")
        
        # Verificar que no sean los mismos que desarrollo
        dev_env = ROOT / ".env"
        if dev_env.exists():
            dev_content = dev_env.read_text()
            for name, prefix in critical_secrets.items():
                dev_val = None
                prod_val = None
                for line in dev_content.splitlines():
                    if line.startswith(prefix):
                        dev_val = line.split("=", 1)[1]
                        break
                for line in content.splitlines():
                    if line.startswith(prefix):
                        prod_val = line.split("=", 1)[1]
                        break
                if dev_val and prod_val and dev_val == prod_val:
                    self.check(f"SECRET {name} != dev", False, 
                              f"Secret idéntico en dev y prod - ROTAR EN PRODUCCIÓN", warning=True)
    
    def _check_docker_config(self):
        print_header("3. CONFIGURACIÓN DOCKER")
        
        prod_compose = ROOT / "docker-compose.prod.yml"
        self.check("EXISTE docker-compose.prod.yml", prod_compose.exists())
        
        if prod_compose.exists():
            content = prod_compose.read_text()
            
            # Verificar imágenes usan variables (formato ${VAR:-default} o ${VAR:?error})
            import re
            backend_var = re.search(r'\$\{BACKEND_IMAGE[:\?]', content)
            frontend_var = re.search(r'\$\{FRONTEND_IMAGE[:\?]', content)
            self.check("IMÁGENES usan variables", bool(backend_var and frontend_var),
                      "Imágenes hardcodeadas")
            self.check("HEALTHCHECKS configurados", "healthcheck:" in content)
            self.check("READ_ONLY containers", "read_only: true" in content)
            self.check("CAP_DROP ALL", "cap_drop:" in content and "ALL" in content)
            self.check("NO-NEW-PRIVILEGES", "no-new-privileges:true" in content)
            self.check("PIDS_LIMIT", "pids_limit:" in content)
            self.check("TMPFS configurado", "tmpfs:" in content)
            self.check("RESTART always", "restart: always" in content)
            
            # Verificar variables obligatorias (formato ${VAR:-default} o ${VAR:?error})
            required_vars = [
                "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD",
                "POSTGRES_APP_PASSWORD", "POSTGRES_BACKUP_PASSWORD",
                "REDIS_PASSWORD", "DATABASE_URL", "MIGRATION_DATABASE_URL",
                "BACKUP_DATABASE_URL", "SECRET_KEY", "CONFIG_ENCRYPTION_KEY",
                "CLIENT_CODE", "CLIENT_NAME", "APP_DOMAIN", "IMAGE_TAG"
            ]
            
            for var in required_vars:
                pattern = rf'\$\{{{var}[:\?]'
                self.check(f"VARIABLE {var} requerida", bool(re.search(pattern, content)),
                          f"Variable {var} no referenciada en compose")
    
    def _check_backend(self):
        print_header("4. BACKEND")
        
        backend_dir = ROOT / "backend"
        
        # Requirements
        req_file = backend_dir / "requirements.txt"
        self.check("EXISTE requirements.txt", req_file.exists())
        
        req_dev = backend_dir / "requirements-dev.txt"
        self.check("EXISTE requirements-dev.txt", req_dev.exists())
        
        # Tests
        tests_dir = backend_dir / "tests"
        test_files = list(tests_dir.glob("test_*.py"))
        self.check(f"TESTS backend ({len(test_files)} archivos)", len(test_files) >= 40,
                  f"Solo {len(test_files)} tests encontrados")
        
        # Verificar tests críticos
        critical_tests = [
            "test_rls_multitenant.py",
            "test_password_policy.py",
            "test_auth_refresh_security.py",
            "test_production_security.py",
        ]
        for test in critical_tests:
            self.check(f"TEST crítico {test}", (tests_dir / test).exists(),
                      "Test crítico faltante")
        
        # Migraciones
        migrations_dir = backend_dir / "alembic" / "versions"
        migration_files = list(migrations_dir.glob("*.py"))
        self.check(f"MIGRACIONES ({len(migration_files)} archivos)", len(migration_files) >= 15)
        
        # Lint local (si ruff instalado)
        if not self.ci_mode:
            success, _ = run_cmd(["ruff", "check", ".", "--select", "E9,F63,F7,F82"], 
                                cwd=backend_dir, timeout=30)
            self.check("RUFF lint (errores críticos)", success, "Ejecute: ruff check backend/")
        
        # Configuración
        config_file = backend_dir / "app" / "config.py"
        self.check("EXISTE app/config.py", config_file.exists())
        
        monitoring_file = backend_dir / "app" / "monitoring.py"
        self.check("EXISTE app/monitoring.py (health/metrics)", monitoring_file.exists())
        
        mfa_service = backend_dir / "app" / "services" / "mfa_service.py"
        self.check("EXISTE MFA service", mfa_service.exists())
    
    def _check_frontend(self):
        print_header("5. FRONTEND")
        
        frontend_dir = ROOT / "frontend"
        
        package_json = frontend_dir / "package.json"
        self.check("EXISTE package.json", package_json.exists())
        
        if package_json.exists():
            import json
            pkg = json.loads(package_json.read_text())
            scripts = pkg.get("scripts", {})
            self.check("SCRIPT build", "build" in scripts)
            self.check("SCRIPT lint", "lint" in scripts)
            self.check("SCRIPT test", "test" in scripts)
        
        # Build test (solo si no CI y node_modules existe)
        if not self.ci_mode and (frontend_dir / "node_modules").exists():
            success, _ = run_cmd("npm run build", cwd=frontend_dir, timeout=120)
            self.check("BUILD frontend exitoso", success, "Ejecute: npm run build en frontend/")
        
        # Lint
        if not self.ci_mode and (frontend_dir / "node_modules").exists():
            success, _ = run_cmd("npm run lint", cwd=frontend_dir, timeout=60)
            self.check("ESLINT frontend", success, "Ejecute: npm run lint en frontend/")
        
        # Archivos críticos
        critical_files = [
            "src/main.jsx",
            "src/App.jsx",
            "src/config/product.js",
            "public/vaner-asset-logo.svg",
            "index.html",
        ]
        for f in critical_files:
            self.check(f"EXISTE {f}", (frontend_dir / f).exists())
        
        # Verificar que no hay referencias SGA visibles en UI (no comentarios)
        src_dir = frontend_dir / "src"
        if src_dir.exists():
            sga_refs = 0
            for jsx_file in src_dir.rglob("*.jsx"):
                try:
                    content = jsx_file.read_text()
                    # Buscar SGA en strings JSX (no en comentarios // o /* */)
                    # Excluir comentarios de una línea
                    lines = content.splitlines()
                    for line in lines:
                        stripped = line.strip()
                        # Saltar comentarios
                        if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                            continue
                        # Buscar SGA en strings JSX (entre comillas o en JSX text)
                        if "SGA" in line and "VANER" not in line:
                            # Verificar que no sea solo en comentario
                            if '"SGA' in line or "'SGA" in line or '>SGA' in line or 'SGA<' in line:
                                sga_refs += 1
                                break
                except:
                    pass
            self.check("SIN referencias SGA visibles en src/", sga_refs == 0,
                      f"{sga_refs} archivos con 'SGA' visible en UI", warning=True)
    
    def _check_production_scripts(self):
        print_header("6. SCRIPTS DE PRODUCCIÓN")
        
        scripts_dir = ROOT / "scripts"
        required_scripts = [
            "rotate_secrets.py",
            "migrate_production.py",
            "setup_redis.py",
            "restore_drill_auto.py",
            "migrate_users.py",
            "backup_auto.py",
            "init_backup_automation.py",
        ]
        
        for script in required_scripts:
            self.check(f"EXISTE scripts/{script}", (scripts_dir / script).exists())
        
        # Verificar que son ejecutables (en Unix)
        if sys.platform != "win32":
            for script in required_scripts:
                path = scripts_dir / script
                if path.exists():
                    self.check(f"EXECUTABLE {script}", os.access(path, os.X_OK),
                              f"chmod +x scripts/{script}")
    
    def _check_security(self):
        print_header("7. SEGURIDAD")
        
        # TruffleHog scan (si disponible)
        if not self.ci_mode:
            success, output = run_cmd("trufflehog --only-verified .", timeout=60)
            if ("not found" in output.lower() or 
                "not recognized" in output.lower() or 
                "command not found" in output.lower() or
                "no se reconoce" in output.lower() or
                "no se encuentra" in output.lower()):
                self.check("TRUFFLEHOG (sin secretos)", True, "trufflehog no instalado - saltando", warning=True)
            else:
                self.check("TRUFFLEHOG (sin secretos)", success, 
                          "Secretos detectados - revisar antes de deploy", warning=True)
        
        # Verificar .gitignore
        gitignore = ROOT / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            patterns = [".env", "*.key", "*.pem", "*.crt", "backups/", "*.sql", "*.dump"]
            for pattern in patterns:
                self.check(f".gitignore incluye {pattern}", pattern in content, warning=True)
        
        # CORS configurado para producción
        if self.env_file.exists():
            content = self.env_file.read_text()
            self.check("BACKEND_CORS_ORIGINS != *", "*" not in content or "BACKEND_CORS_ORIGINS=*" not in content,
                      "CORS permite * en producción")
            self.check("REFRESH_COOKIE_SECURE=true", "REFRESH_COOKIE_SECURE=true" in content)
            self.check("RATE_LIMIT_REDIS_REQUIRED=true", "RATE_LIMIT_REDIS_REQUIRED=true" in content)
            self.check("BACKUP_ENCRYPTION_REQUIRED=true", "BACKUP_ENCRYPTION_REQUIRED=true" in content)
    
    def _check_cicd(self):
        print_header("8. CI/CD")
        
        workflows = ROOT / ".github" / "workflows"
        self.check("EXISTE .github/workflows/", workflows.exists())
        
        required_workflows = ["ci.yml", "deploy.yml"]
        for wf in required_workflows:
            self.check(f"EXISTE {wf}", (workflows / wf).exists())
        
        if (workflows / "ci.yml").exists():
            content = (workflows / "ci.yml").read_text()
            required_jobs = ["lint", "test-backend", "build-frontend", "validate-migrations", "security"]
            for job in required_jobs:
                self.check(f"CI JOB {job}", f"name: {job}" in content or f"{job}:" in content, warning=True)
    
    def _print_summary(self):
        if not self.ci_mode:
            print_header("RESUMEN PRE-DEPLOY")
            
            print(f"\n{Colors.BOLD}Total checks: {len(self.results['checks'])}{Colors.END}")
            print(f"{Colors.GREEN}[OK] Pasados: {self.results['passed']}{Colors.END}")
            print(f"{Colors.RED}[FAIL] Fallados: {self.results['failed']}{Colors.END}")
            print(f"{Colors.YELLOW}[WARN] Warnings: {self.results['warnings']}{Colors.END}")
            
            if self.results["failed"] == 0:
                print(f"\n{Colors.GREEN}{Colors.BOLD}[OK] LISTO PARA DEPLOY{Colors.END}")
            else:
                print(f"\n{Colors.RED}{Colors.BOLD}[FAIL] NO LISTO - CORREGIR ERRORES ANTES DE DEPLOY{Colors.END}")
                print(f"\nChecks fallados:")
                for name, result in self.results["checks"].items():
                    if not result["passed"] and not result["warning"]:
                        print(f"  - {name}: {result['details']}")
        
        # Guardar reporte JSON
        report_file = ROOT / f"predeploy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.write_text(json.dumps(self.results, indent=2))
        if not self.ci_mode:
            print(f"\n[REPORT] Reporte guardado: {report_file}")

def main():
    parser = argparse.ArgumentParser(description="Pre-deploy checklist VANER ASSET")
    parser.add_argument("--env-file", default=".env.production", help="Archivo entorno producción")
    parser.add_argument("--ci", action="store_true", help="Modo CI (salida JSON, exit code)")
    parser.add_argument("--fix", action="store_true", help="Intentar corregir issues automáticos")
    args = parser.parse_args()
    
    checklist = PreDeployChecklist(args.env_file, ci_mode=args.ci)
    success = checklist.run_all()
    
    if args.ci:
        # Output JSON para CI
        print(json.dumps(checklist.results, indent=2))
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()