import unittest
from decimal import Decimal

from fastapi import HTTPException

from app.routers.dashboard_tecnico import normalizar_incidencias, normalizar_repuestos


class DetallesOperativosOtTests(unittest.TestCase):
    def test_repuesto_valido_se_normaliza(self):
        items = normalizar_repuestos('[{"descripcion":"Filtro", "cantidad":"2.5", "unidad":"unidad", "costo_unitario":"10000"}]')
        self.assertEqual(items[0]["cantidad"], Decimal("2.5"))
        self.assertEqual(items[0]["unidad"], "UNIDAD")

    def test_repuesto_sin_cantidad_positiva_es_rechazado(self):
        with self.assertRaises(HTTPException):
            normalizar_repuestos('[{"descripcion":"Filtro", "cantidad":0}]')

    def test_incidencia_valida_se_normaliza(self):
        items = normalizar_incidencias('[{"tipo":"seguridad", "severidad":"alta", "descripcion":"Cable expuesto"}]')
        self.assertEqual(items[0]["tipo"], "SEGURIDAD")
        self.assertEqual(items[0]["severidad"], "ALTA")

    def test_severidad_arbitraria_es_rechazada(self):
        with self.assertRaises(HTTPException):
            normalizar_incidencias('[{"severidad":"EXTREMA", "descripcion":"Falla"}]')


if __name__ == "__main__":
    unittest.main()
