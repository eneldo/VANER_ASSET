import unittest
from uuid import uuid4

from pydantic import ValidationError

from app.models.categoria import CATEGORIA_CODES
from app.schemas.equipo import EquipoCreate


class CategoriasCanonicasTests(unittest.TestCase):
    def test_existen_exactamente_las_cuatro_familias_requeridas(self):
        self.assertEqual(CATEGORIA_CODES, {
            "EQUIPOS_INDUSTRIALES",
            "AIRES_ACONDICIONADOS",
            "CAMARAS_SEGURIDAD",
            "PROTECCION_CONTRA_INCENDIOS",
        })

    def test_equipo_nuevo_requiere_categoria(self):
        with self.assertRaises(ValidationError):
            EquipoCreate(empresa_id=uuid4(), sede_id=uuid4(), nombre="Equipo sin categoría")

    def test_equipo_acepta_categoria_explicita(self):
        data = EquipoCreate(
            empresa_id=uuid4(), sede_id=uuid4(), categoria_id=uuid4(), nombre="Bomba"
        )
        self.assertIsNotNone(data.categoria_id)


if __name__ == "__main__":
    unittest.main()
