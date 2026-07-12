import base64
import unittest

from pydantic import ValidationError

from app.schemas.formato_mantenimiento_schema import FormatoMantenimientoCreate, validar_firma_png


def firma_png_prueba():
    contenido = b"\x89PNG\r\n\x1a\n" + (b"0" * 120)
    return "data:image/png;base64," + base64.b64encode(contenido).decode()


class FirmaDigitalTests(unittest.TestCase):
    def test_acepta_png_base64(self):
        self.assertEqual(validar_firma_png(firma_png_prueba()), firma_png_prueba())

    def test_rechaza_texto_como_firma(self):
        with self.assertRaises(ValueError):
            validar_firma_png("Juan Pérez")

    def test_schema_aplica_validacion(self):
        with self.assertRaises(ValidationError):
            FormatoMantenimientoCreate(mantenimiento_id="00000000-0000-0000-0000-000000000001", firma_operario="texto")


if __name__ == "__main__":
    unittest.main()
