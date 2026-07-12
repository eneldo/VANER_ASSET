import unittest
from unittest.mock import patch

from app import main


class CorsConfigTests(unittest.TestCase):
    def test_normaliza_lista_de_dominios(self):
        with patch.object(main.settings, "APP_ENV", "production"), patch.object(
            main.settings,
            "BACKEND_CORS_ORIGINS",
            "https://uno.test/, https://dos.test",
        ):
            self.assertEqual(
                main._cors_origins(),
                ["https://uno.test", "https://dos.test"],
            )

    def test_produccion_rechaza_wildcard(self):
        with patch.object(main.settings, "APP_ENV", "production"), patch.object(
            main.settings, "BACKEND_CORS_ORIGINS", "*"
        ):
            with self.assertRaises(RuntimeError):
                main._cors_origins()


if __name__ == "__main__":
    unittest.main()
