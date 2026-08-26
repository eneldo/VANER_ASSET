import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


class PublicConfigTests(unittest.TestCase):
    def test_expone_identidad_no_sensible_del_despliegue(self):
        with (
            patch.object(settings, "APP_NAME", "VANER ASSET"),
            patch.object(settings, "CLIENT_CODE", "empresa_xyz"),
            patch.object(settings, "CLIENT_NAME", "Empresa XYZ S.A.S."),
            patch.object(settings, "APP_DOMAIN", "asset.empresaxyz.com"),
        ):
            response = TestClient(app).get("/public/config")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "appName": "VANER ASSET",
                "clientCode": "empresa_xyz",
                "clientName": "Empresa XYZ S.A.S.",
                "appDomain": "asset.empresaxyz.com",
                "coreCompanyName": "VANER SOFTWARE",
                "coreProductName": "VANER ASSET",
                "description": "Plataforma para la gestión de inventarios, activos y mantenimiento.",
            },
        )


if __name__ == "__main__":
    unittest.main()
