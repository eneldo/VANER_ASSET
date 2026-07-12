import unittest
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError

from app.routers.plantillas_reporte import PlantillaIn, _validar_tipo


class PlantillasReporteTests(unittest.TestCase):
    def test_tipos_permitidos(self):
        self.assertEqual(_validar_tipo("ot"), "OT")
        self.assertEqual(_validar_tipo("mensual"), "MENSUAL")
        self.assertEqual(_validar_tipo("ambos"), "AMBOS")
        with self.assertRaises(HTTPException):
            _validar_tipo("HTML_LIBRE")

    def test_color_hexadecimal_es_validado(self):
        item = PlantillaIn(nombre="Global", titulo="Reporte", color_primario="#1E3A8A")
        self.assertEqual(item.color_primario, "#1E3A8A")
        with self.assertRaises(ValidationError):
            PlantillaIn(nombre="Global", titulo="Reporte", color_primario="red;script")

    def test_plantilla_puede_tener_scope_empresa(self):
        empresa_id = uuid4()
        item = PlantillaIn(empresa_id=empresa_id, nombre="Cliente", titulo="Informe cliente")
        self.assertEqual(item.empresa_id, empresa_id)


if __name__ == "__main__":
    unittest.main()
