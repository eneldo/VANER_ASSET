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
        "CLIENT_CODE": "empresa_xyz",
        "CLIENT_NAME": "Empresa XYZ S.A.S.",
        "APP_DOMAIN": "asset.empresaxyz.com",
        "DEBUG": False,
        "DATABASE_URL": "postgresql://app:password@postgres:5432/sga",
        "BACKUP_DATABASE_URL": "postgresql://vaner_backup:password@postgres:5432/sga",
        "SECRET_KEY": "s" * 64,
        "CONFIG_ENCRYPTION_KEY": Fernet.generate_key().decode("ascii"),
        "FRONTEND_URL": None,
        "REFRESH_COOKIE_SECURE": True,
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        "BACKEND_CORS_ORIGINS": "",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


class ProductionSecurityTests(unittest.TestCase):
    def test_rechaza_access_token_excesivo(self):
        with self.assertRaises(ValueError):
            production_settings(ACCESS_TOKEN_EXPIRE_MINUTES=480)

    def test_rechaza_frontend_sin_https(self):
        with self.assertRaises(ValueError):
            production_settings(FRONTEND_URL="http://asset.empresaxyz.com")

    def test_deriva_urls_desde_app_domain(self):
        configured = production_settings()
        self.assertEqual(configured.FRONTEND_URL, "https://asset.empresaxyz.com")
        self.assertEqual(
            configured.BACKEND_CORS_ORIGINS,
            "https://asset.empresaxyz.com",
        )

    def test_requiere_identidad_de_cliente_en_produccion(self):
        with self.assertRaises(ValueError):
            production_settings(CLIENT_CODE="local")
        with self.assertRaises(ValueError):
            production_settings(CLIENT_NAME="")
        with self.assertRaises(ValueError):
            production_settings(APP_DOMAIN="localhost")

    def test_requiere_rol_backup_dedicado(self):
        with self.assertRaises(ValueError):
            production_settings(BACKUP_DATABASE_URL=None)
        with self.assertRaises(ValueError):
            production_settings(
                BACKUP_DATABASE_URL="postgresql://app:otra-password@postgres:5432/sga"
            )
        with self.assertRaises(ValueError):
            production_settings(
                BACKUP_DATABASE_URL="postgresql://sga_owner:otra-password@postgres:5432/sga"
            )
        with self.assertRaises(ValueError):
            production_settings(
                BACKUP_DATABASE_URL="postgresql://sga_backup:otra-password@postgres:5432/sga"
            )

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
