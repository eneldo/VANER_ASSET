import unittest

from fastapi.testclient import TestClient

from app.main import app


class AdminRoutesProtectedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_recursos_administrativos_requieren_token(self):
        for path in ("/empresas/", "/sedes/", "/tecnicos/", "/mantenimientos/", "/facturacion/resumen"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 401)

    def test_infraestructura_requiere_token(self):
        for path in ("/bi-ejecutivo/resumen", "/backups-inteligentes/", "/monitor-vps/estado"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertIn(response.status_code, {401, 404})


if __name__ == "__main__":
    unittest.main()
