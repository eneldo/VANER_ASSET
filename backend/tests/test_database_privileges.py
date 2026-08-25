import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "backend" / "alembic" / "versions" / "l62a0d530001_privilegios_app_allowlist.py"


class DatabasePrivilegesTests(unittest.TestCase):
    def test_no_hay_privilegios_dml_por_defecto(self):
        for relative_path in (
            "backend/sql/provision_app_role.sql",
            "backend/docker/init-app-role.sh",
        ):
            source = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertNotIn("GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES", source)
            self.assertIn("REVOKE ALL ON TABLES FROM sga_app", source)

    def test_allowlist_cubre_tablas_modeladas_y_asociaciones(self):
        module = ast.parse(MIGRATION.read_text(encoding="utf-8"))
        assignment = next(
            node
            for node in module.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "APP_TABLES" for target in node.targets)
        )
        allowlist = set(ast.literal_eval(assignment.value))

        modeled = set()
        association_tables = set()
        for path in (ROOT / "backend" / "app" / "models").glob("*.py"):
            source = path.read_text(encoding="utf-8")
            modeled.update(re.findall(r'__tablename__\s*=\s*["\']([^"\']+)', source))
            association_tables.update(
                re.findall(r'Table\(\s*["\']([^"\']+)', source)
            )

        expected = modeled | association_tables
        self.assertEqual(allowlist, expected)


if __name__ == "__main__":
    unittest.main()
