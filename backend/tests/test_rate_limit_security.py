import unittest

from app.middleware.rate_limit import DistributedRateLimitMiddleware


class RateLimitSecurityTests(unittest.TestCase):
    def setUp(self):
        self.middleware = DistributedRateLimitMiddleware(
            lambda _scope, _receive, _send: None
        )

    def test_recuperacion_tiene_limite_especifico(self):
        self.assertEqual(
            self.middleware._rule_for_path("/auth/forgot-password"),
            (5, 900),
        )

    def test_clave_no_expone_ip_ni_ruta(self):
        key = self.middleware._key(
            "203.0.113.10",
            "/auth/forgot-password",
            900,
            1000.0,
        )
        self.assertNotIn("203.0.113.10", key)
        self.assertNotIn("forgot-password", key)
        self.assertTrue(key.startswith("sga:rate-limit:"))


if __name__ == "__main__":
    unittest.main()
