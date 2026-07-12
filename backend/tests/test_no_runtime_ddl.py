import unittest
from pathlib import Path


class NoRuntimeDdlTests(unittest.TestCase):
    def test_aplicacion_no_ejecuta_create_all(self):
        app_dir = Path(__file__).resolve().parents[1] / "app"
        hallazgos = []
        for archivo in app_dir.rglob("*.py"):
            if "create_all" in archivo.read_text(encoding="utf-8"):
                hallazgos.append(str(archivo.relative_to(app_dir)))
        self.assertEqual(
            hallazgos,
            [],
            f"El DDL de runtime debe trasladarse a Alembic: {hallazgos}",
        )


if __name__ == "__main__":
    unittest.main()
