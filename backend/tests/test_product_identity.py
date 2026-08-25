import json
import unittest
from pathlib import Path

from app.product import COMPANY_NAME, PRODUCT_DESCRIPTION, PRODUCT_MODULES, PRODUCT_NAME

ROOT = Path(__file__).resolve().parents[2]


class ProductIdentityTests(unittest.TestCase):
    def test_identidad_principal(self):
        self.assertEqual(COMPANY_NAME, "VANER SOFTWARE")
        self.assertEqual(PRODUCT_NAME, "VANER ASSET")
        self.assertIn("inventarios", PRODUCT_DESCRIPTION.lower())

    def test_catalogo_funcional_requerido(self):
        self.assertEqual(
            set(PRODUCT_MODULES),
            {
                "Inventarios",
                "Activos",
                "Mantenimiento",
                "Órdenes de trabajo",
                "Repuestos",
                "Técnicos",
                "Reportes",
                "Dashboard",
                "Administración",
            },
        )

    def test_estructura_inicial_de_clientes(self):
        clients_dir = ROOT / "config" / "vaner_asset" / "clients"
        expected = {
            "cliente-1.example.json",
            "cliente-2.example.json",
            "cliente-3.example.json",
            "vaner.example.json",
        }
        self.assertTrue(expected.issubset({path.name for path in clients_dir.glob("*.json")}))

        vaner = json.loads((clients_dir / "vaner.example.json").read_text(encoding="utf-8"))
        self.assertEqual(vaner["name"], "Cliente VANER")
        self.assertEqual(vaner["status"], "internal")


if __name__ == "__main__":
    unittest.main()
