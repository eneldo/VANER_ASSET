import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.utils import backup_utils


class BackupPathSecurityTests(unittest.TestCase):
    def test_rechaza_path_traversal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(backup_utils, "BACKUP_DIR", Path(temp_dir).resolve()):
                with self.assertRaises(ValueError):
                    backup_utils._safe_backup_path("../secreto.sql")

    def test_acepta_solo_sql_dentro_del_directorio(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir).resolve()
            with patch.object(backup_utils, "BACKUP_DIR", backup_dir):
                self.assertEqual(
                    backup_utils._safe_backup_path("backup_valido.sql"),
                    backup_dir / "backup_valido.sql",
                )
                with self.assertRaises(ValueError):
                    backup_utils._safe_backup_path("backup.zip")

    def test_restore_permanece_deshabilitado_por_defecto(self):
        with patch.dict(os.environ, {"ALLOW_DATABASE_RESTORE": "false"}, clear=False):
            with self.assertRaises(PermissionError):
                backup_utils.restaurar_backup("backup.sql")


if __name__ == "__main__":
    unittest.main()
