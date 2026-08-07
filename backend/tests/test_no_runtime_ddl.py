import unittest
from pathlib import Path


class NoRuntimeDdlTests(unittest.TestCase):
    def test_aplicacion_no_ejecuta_ddl(self):
        app_dir = Path(__file__).resolve().parents[1] / "app"
        hallazgos = []
        for archivo in app_dir.rglob("*.py"):
            source = archivo.read_text(encoding="utf-8")
            if "create_all" in source or ".__table__.create" in source:
                hallazgos.append(str(archivo.relative_to(app_dir)))
        self.assertEqual(
            hallazgos,
            [],
            f"El DDL de runtime debe trasladarse a Alembic: {hallazgos}",
        )


if __name__ == "__main__":
    unittest.main()
