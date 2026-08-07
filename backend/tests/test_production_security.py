import unittest
from unittest.mock import patch

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from app.config import Settings, settings
from app.main import app
from app.services.secret_store import decrypt_secret, encrypt_secret, mask_secret


def production_settings(**overrides):
    values = {
        "APP_ENV": "production",
        "DEBUG": False,
        "DATABASE_URL": "postgresql://app:password@postgres:5432/sga",
        "SECRET_KEY": "s" * 64,
        "CONFIG_ENCRYPTION_KEY": Fernet.generate_key().decode("ascii"),
        "FRONTEND_URL": "https://sgaholding.online",
        "REFRESH_COOKIE_SECURE": True,
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        "BACKEND_CORS_ORIGINS": "https://sgaholding.online",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


class ProductionSecurityTests(unittest.TestCase):
    def test_rechaza_access_token_excesivo(self):
        with self.assertRaises(ValueError):
            production_settings(ACCESS_TOKEN_EXPIRE_MINUTES=480)

    def test_rechaza_frontend_sin_https(self):
        with self.assertRaises(ValueError):
            production_settings(FRONTEND_URL="http://sgaholding.online")

    def test_secretos_se_cifran_y_enmascaran(self):
        key = Fernet.generate_key().decode("ascii")
        with patch.object(settings, "CONFIG_ENCRYPTION_KEY", key):
            encrypted = encrypt_secret("smtp-password")
            self.assertNotIn("smtp-password", encrypted)
            self.assertEqual(decrypt_secret(encrypted), "smtp-password")
            self.assertEqual(mask_secret(encrypted), "********")

    def test_bootstrap_requiere_token(self):
        with patch.object(settings, "BOOTSTRAP_ADMIN_TOKEN", "bootstrap-token-seguro"):
            response = TestClient(app).post(
                "/usuarios/crear-admin-inicial",
                json={
                    "nombre_completo": "Administrador",
                    "username": "admin",
                    "email": "admin@example.com",
                    "password": "password-seguro-123",
                },
                headers={"X-Bootstrap-Token": "incorrecto"},
            )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
