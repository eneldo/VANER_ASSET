import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.routers.equipos import (
    normalizar_numero_inventario,
    validar_numero_inventario,
)


class EquiposInventarioTests(unittest.TestCase):
    def test_normaliza_espacios_y_valores_vacios(self):
        self.assertEqual(normalizar_numero_inventario("  INV-001  "), "INV-001")
        self.assertIsNone(normalizar_numero_inventario("   "))
        self.assertIsNone(normalizar_numero_inventario(None))

    def test_rechaza_numero_de_inventario_existente(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
            inventario="INV-001"
        )

        with self.assertRaises(HTTPException) as context:
            validar_numero_inventario(db, " inv-001 ")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Equipo ya existe", context.exception.detail)

    def test_acepta_numero_de_inventario_disponible(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        numero = validar_numero_inventario(db, "  INV-002  ")

        self.assertEqual(numero, "INV-002")


if __name__ == "__main__":
    unittest.main()
