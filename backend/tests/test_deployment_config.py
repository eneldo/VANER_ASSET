import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DeploymentConfigTests(unittest.TestCase):
    def test_compose_usa_volumenes_persistentes_y_healthchecks(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("uploads_data:/app/uploads", compose)
        self.assertIn("backups_data:/app/backups", compose)
        self.assertIn("MIGRATION_DATABASE_URL", compose)
        self.assertIn("migrate:", compose)
        self.assertIn('entrypoint: ["alembic"]', compose)
        self.assertIn("BACKEND_CORS_ORIGINS", compose)
        self.assertGreaterEqual(compose.count("healthcheck:"), 3)

        backend = compose.split("  backend:", 1)[1].split("  frontend:", 1)[0]
        self.assertNotIn("MIGRATION_DATABASE_URL", backend)
        self.assertNotIn("POSTGRES_PASSWORD", backend)

    def test_backend_arranca_migraciones_sin_root(self):
        dockerfile = (ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
        entrypoint = (ROOT / "backend" / "entrypoint.sh").read_text(encoding="utf-8")

        self.assertIn("USER appuser", dockerfile)
        self.assertIn("ENTRYPOINT", dockerfile)
        self.assertIn("qpdf", dockerfile)
        self.assertNotIn("alembic upgrade head", entrypoint)
        self.assertIn('exec "$@"', entrypoint)

    def test_backend_usa_pg_dump_compatible_con_postgres_16(self):
        dockerfile = (ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
        compose = (ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8")

        self.assertIn("postgresql-client-16", dockerfile)
        self.assertIn("apt.postgresql.org/pub/repos/apt bookworm-pgdg main", dockerfile)
        self.assertIn("postgres:16-bookworm", compose)

    def test_compose_produccion_fuerza_entorno_seguro(self):
        compose = (ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8")
        backend = compose.split("  backend:", 1)[1].split("  frontend:", 1)[0]

        self.assertIn("APP_ENV: production", backend)
        self.assertIn('DEBUG: "false"', backend)
        self.assertIn("APP_NAME: ${APP_NAME:-SGAHolding}", backend)
        self.assertIn("ALGORITHM: ${ALGORITHM:-HS256}", backend)

    def test_frontend_no_conserva_backend_local_hardcodeado(self):
        source_root = ROOT / "frontend" / "src"
        offenders = []

        for path in source_root.rglob("*"):
            if path.suffix not in {".js", ".jsx"}:
                continue
            if "http://127.0.0.1:8000" in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(ROOT)))

        self.assertEqual(offenders, [])


    def test_frontend_declara_imagenes_antes_del_primer_from(self):
        dockerfile = (ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")
        first_from = dockerfile.index("FROM ")

        self.assertLess(dockerfile.index("ARG NODE_IMAGE="), first_from)
        self.assertLess(dockerfile.index("ARG NGINX_IMAGE="), first_from)

    def test_imagenes_actualizan_paquetes_del_sistema(self):
        backend = (ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
        frontend = (ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")

        self.assertIn("apt-get upgrade -y", backend)
        self.assertIn("--no-install-recommends", backend)
        self.assertNotIn("    gcc \\n", backend)
        self.assertNotIn("    libpq-dev \\n", backend)
        self.assertIn("apk upgrade --no-cache", frontend)

    def test_requisitos_incluyen_versiones_corregidas(self):
        requirements = (ROOT / "backend" / "requirements.txt").read_text(encoding="utf-8")

        for requirement in (
            "cryptography==50.0.0",
            "pillow==12.3.0",
            "pyasn1==0.6.4",
            "python-multipart==0.0.32",
            "starlette==1.3.1",
        ):
            self.assertIn(requirement, requirements)

if __name__ == "__main__":
    unittest.main()
