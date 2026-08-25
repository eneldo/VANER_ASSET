import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]


class AuthArchitectureTests(unittest.TestCase):
    def test_security_module_no_define_dependencia_http_legacy(self):
        source = (BACKEND_ROOT / "app" / "security.py").read_text(encoding="utf-8")

        self.assertNotIn("OAuth2PasswordBearer", source)
        self.assertNotIn("def get_current_user", source)
        self.assertNotIn("from fastapi", source)

    def test_router_cliente_seguro_huerfano_no_existe(self):
        router = BACKEND_ROOT / "app" / "routers" / "cliente_seguro.py"
        self.assertFalse(router.exists())


if __name__ == "__main__":
    unittest.main()
