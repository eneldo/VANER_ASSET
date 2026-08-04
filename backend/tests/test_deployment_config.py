import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DeploymentConfigTests(unittest.TestCase):
    def test_compose_usa_volumenes_persistentes_y_healthchecks(self):
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("uploads_data:/app/uploads", compose)
        self.assertIn("backups_data:/app/backups", compose)
        self.assertIn("MIGRATION_DATABASE_URL", compose)
        self.assertIn("BACKEND_CORS_ORIGINS", compose)
        self.assertGreaterEqual(compose.count("healthcheck:"), 3)

    def test_backend_arranca_migraciones_sin_root(self):
        dockerfile = (ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
        entrypoint = (ROOT / "backend" / "entrypoint.sh").read_text(encoding="utf-8")

        self.assertIn("USER appuser", dockerfile)
        self.assertIn("ENTRYPOINT", dockerfile)
        self.assertIn("qpdf", dockerfile)
        self.assertIn("alembic upgrade head", entrypoint)

    def test_frontend_no_conserva_backend_local_hardcodeado(self):
        source_root = ROOT / "frontend" / "src"
        offenders = []

        for path in source_root.rglob("*"):
            if path.suffix not in {".js", ".jsx"}:
                continue
            if "http://127.0.0.1:8000" in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(ROOT)))

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
