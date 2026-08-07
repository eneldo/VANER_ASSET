import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.config import settings
from app.services.smart_backup_service import SmartBackupService


class SmartBackupSecurityTests(unittest.TestCase):
    def test_dump_usa_rol_backup_dedicado(self):
        completed = SimpleNamespace(returncode=0, stderr=b"")

        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "backup.sql"
            with (
                patch.object(
                    settings,
                    "BACKUP_DATABASE_URL",
                    "postgresql://sga_backup:backup-secret@postgres:5432/sga_db",
                ),
                patch.object(settings, "DATABASE_URL", "postgresql://sga_app:app-secret@postgres:5432/sga_db"),
                patch("app.services.smart_backup_service.subprocess.run", return_value=completed) as run,
            ):
                SmartBackupService(db=None)._dump_postgres(destination)

        command = run.call_args.args[0]
        environment = run.call_args.kwargs["env"]
        self.assertEqual(command[command.index("-U") + 1], "sga_backup")
        self.assertEqual(environment["PGPASSWORD"], "backup-secret")
        self.assertNotIn("app-secret", environment.values())

    def test_produccion_no_reutiliza_database_url(self):
        with (
            patch.object(settings, "APP_ENV", "production"),
            patch.object(settings, "BACKUP_DATABASE_URL", None),
        ):
            with self.assertRaisesRegex(RuntimeError, "BACKUP_DATABASE_URL"):
                SmartBackupService(db=None)._dump_postgres(Path("backup.sql"))


if __name__ == "__main__":
    unittest.main()
