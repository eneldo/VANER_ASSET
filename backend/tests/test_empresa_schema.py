import unittest

from pydantic import ValidationError

from app.schemas.empresa import EmpresaCreate, EmpresaUpdate


class EmpresaSchemaTests(unittest.TestCase):
    def test_creacion_convierte_campos_opcionales_vacios_en_none(self):
        empresa = EmpresaCreate(
            nombre="Empresa local",
            nit=" ",
            telefono="",
            direccion="  ",
            correo="",
            logo_url=" ",
        )

        self.assertIsNone(empresa.nit)
        self.assertIsNone(empresa.telefono)
        self.assertIsNone(empresa.direccion)
        self.assertIsNone(empresa.correo)
        self.assertIsNone(empresa.logo_url)

    def test_actualizacion_normaliza_y_valida_el_correo(self):
        empresa = EmpresaUpdate(correo=" contacto@empresa.com ")
        self.assertEqual(str(empresa.correo), "contacto@empresa.com")

        with self.assertRaises(ValidationError):
            EmpresaUpdate(correo="correo-invalido")


if __name__ == "__main__":
    unittest.main()
