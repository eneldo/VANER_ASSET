import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cryptography.fernet import Fernet

from app.config import settings
from app.services.backup_crypto import decrypt_backup_file, encrypt_backup_file
from app.services.smart_backup_service import SmartBackupService


class SmartBackupSecurityTests(unittest.TestCase):
    def test_cifrado_backup_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "backup.zip"
            encrypted = Path(temp_dir) / "backup.zip.sgaenc"
            restored = Path(temp_dir) / "restored.zip"
            source.write_bytes(b"backup-sensible" * 1000)

            with patch.object(
                settings,
                "CONFIG_ENCRYPTION_KEY",
                Fernet.generate_key().decode("ascii"),
            ):
                encrypt_backup_file(source, encrypted)
                decrypt_backup_file(encrypted, restored)

            self.assertNotIn(b"backup-sensible", encrypted.read_bytes())
            self.assertEqual(restored.read_bytes(), source.read_bytes())

    def test_elimina_objeto_remoto_usando_metadata(self):
        client = SimpleNamespace(delete_object=lambda **_kwargs: None)
        item = SimpleNamespace(metadata_json={"remote_key": "sga/backup.sgaenc"})
        service = SmartBackupService(db=None)

        with (
            patch.object(settings, "S3_BACKUP_ENABLED", True),
            patch.object(settings, "S3_BACKUP_BUCKET", "bucket-pruebas"),
            patch.object(service, "_s3_client", return_value=client) as factory,
            patch.object(client, "delete_object", wraps=client.delete_object) as delete,
        ):
            service._delete_remote_backup(item)

        factory.assert_called_once_with()
        delete.assert_called_once_with(
            Bucket="bucket-pruebas",
            Key="sga/backup.sgaenc",
        )

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
