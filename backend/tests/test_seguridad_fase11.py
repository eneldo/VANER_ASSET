import hashlib
import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from app.config import Settings
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_access_token_minutes,
    hash_password,
    hash_token,
    utc_now,
    verify_password,
)


class PasswordHashingTests(unittest.TestCase):
    def test_hash_y_verify_password(self):
        password = "MiPasswordSeguro123!"
        hashed = hash_password(password)
        self.assertNotEqual(hashed, password)
        self.assertTrue(verify_password(password, hashed))

    def test_hash_es_argon2id(self):
        hashed = hash_password("test")
        self.assertTrue(hashed.startswith("$argon2"))

    def test_password_diferentes_producen_hashes_distintos(self):
        h1 = hash_password("pass1")
        h2 = hash_password("pass2")
        self.assertNotEqual(h1, h2)


class AccessTokenTests(unittest.TestCase):
    def test_create_access_token_payload(self):
        payload = {"sub": "user-123", "email": "test@example.com"}
        token = create_access_token(payload)
        decoded = decode_token(token)
        self.assertEqual(decoded["sub"], "user-123")
        self.assertEqual(decoded["email"], "test@example.com")
        self.assertEqual(decoded["type"], "access")
        self.assertIn("jti", decoded)
        self.assertIn("exp", decoded)

    def test_create_access_token_con_expires_delta(self):
        payload = {"sub": "user-123"}
        token = create_access_token(payload, expires_delta=timedelta(minutes=1))
        decoded = decode_token(token)
        self.assertEqual(decoded["type"], "access")

    def test_access_token_expiracion_default(self):
        minutes = get_access_token_minutes()
        self.assertGreaterEqual(minutes, 10)
        self.assertLessEqual(minutes, 60)


class RefreshTokenTests(unittest.TestCase):
    def test_create_refresh_token_retorna_trio(self):
        payload = {"sub": "user-123"}
        token, jti, expires_at = create_refresh_token(payload)
        self.assertIsInstance(token, str)
        self.assertIsInstance(jti, str)
        self.assertGreater(len(jti), 0)

    def test_create_refresh_token_type(self):
        payload = {"sub": "user-123"}
        token, jti, expires_at = create_refresh_token(payload)
        decoded = decode_token(token)
        self.assertEqual(decoded["type"], "refresh")
        self.assertEqual(decoded["jti"], jti)


class TokenHashTests(unittest.TestCase):
    def test_hash_token_consistente(self):
        token = "eyJhbGciOiJIUzI1NiJ9.test"
        h1 = hash_token(token)
        h2 = hash_token(token)
        self.assertEqual(h1, h2)

    def test_hash_token_no_expone_original(self):
        token = "eyJhbGciOiJIUzI1NiJ9.test"
        h = hash_token(token)
        self.assertNotIn(token, h)

    def test_hash_token_es_sha256(self):
        token = "test-token"
        expected = hashlib.sha256(token.encode("utf-8")).hexdigest()
        self.assertEqual(hash_token(token), expected)


class HashTokenCompuestoTests(unittest.TestCase):
    def test_hash_diferentes_tokens_producen_diferentes_hashes(self):
        self.assertNotEqual(hash_token("a"), hash_token("b"))


class SecurityHeadersTests(unittest.TestCase):
    def _make_request_and_get_headers(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from app.middleware.security_headers import SecurityHeadersMiddleware

        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        def test_route():
            return {"ok": True}

        client = TestClient(app)
        resp = client.get("/test")
        return resp.headers

    def test_x_content_type_nosniff(self):
        headers = self._make_request_and_get_headers()
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")

    def test_x_frame_options_sameorigin(self):
        headers = self._make_request_and_get_headers()
        self.assertEqual(headers.get("X-Frame-Options"), "SAMEORIGIN")

    def test_referrer_policy(self):
        headers = self._make_request_and_get_headers()
        self.assertEqual(
            headers.get("Referrer-Policy"),
            "strict-origin-when-cross-origin",
        )

    def test_permissions_policy(self):
        headers = self._make_request_and_get_headers()
        pp = headers.get("Permissions-Policy", "")
        self.assertIn("camera=()", pp)
        self.assertIn("microphone=()", pp)
        self.assertIn("geolocation=()", pp)

    def test_csp_presente(self):
        headers = self._make_request_and_get_headers()
        self.assertIn("Content-Security-Policy", headers)


class AuditMiddlewareTests(unittest.TestCase):
    def setUp(self):
        from app.middleware.audit_middleware import AuditMiddleware

        self.middleware = AuditMiddleware(
            lambda _scope, _receive, _send: None
        )

    def test_should_skip_docs(self):
        self.assertTrue(self.middleware._should_skip("/docs"))
        self.assertTrue(self.middleware._should_skip("/redoc"))
        self.assertTrue(self.middleware._should_skip("/openapi.json"))
        self.assertTrue(self.middleware._should_skip("/uploads"))

    def test_should_not_skip_api(self):
        self.assertFalse(self.middleware._should_skip("/auth/login"))
        self.assertFalse(self.middleware._should_skip("/equipos"))

    def test_modulo_from_path(self):
        self.assertEqual(self.middleware._modulo_from_path("/auth/login"), "AUTH")
        self.assertEqual(self.middleware._modulo_from_path("/equipos"), "EQUIPOS")
        self.assertEqual(self.middleware._modulo_from_path("/"), "SISTEMA")

    def test_accion_from_method_create(self):
        self.assertEqual(
            self.middleware._accion_from_method("POST", 200), "CREATE_OR_ACTION"
        )
        self.assertEqual(
            self.middleware._accion_from_method("PUT", 200), "UPDATE"
        )
        self.assertEqual(
            self.middleware._accion_from_method("DELETE", 200), "DELETE"
        )

    def test_accion_from_method_error(self):
        self.assertEqual(
            self.middleware._accion_from_method("GET", 401), "ACCESS_DENIED"
        )
        self.assertEqual(
            self.middleware._accion_from_method("GET", 403), "ACCESS_DENIED"
        )
        self.assertEqual(
            self.middleware._accion_from_method("GET", 500), "ERROR_SERVER"
        )

    def test_severidad(self):
        self.assertEqual(self.middleware._severidad("DELETE", 200), "ALTA")
        self.assertEqual(self.middleware._severidad("POST", 200), "MEDIA")
        self.assertEqual(self.middleware._severidad("GET", 200), "INFO")
        self.assertEqual(self.middleware._severidad("GET", 500), "CRITICA")
        self.assertEqual(self.middleware._severidad("GET", 401), "ALTA")


class RateLimitKeyTests(unittest.TestCase):
    def setUp(self):
        from app.middleware.rate_limit import DistributedRateLimitMiddleware

        self.middleware = DistributedRateLimitMiddleware(
            lambda _scope, _receive, _send: None
        )

    def test_key_usa_prefijo_vaner(self):
        key = self.middleware._key("1.2.3.4", "/auth/login", 60, 1000.0)
        self.assertTrue(
            key.startswith("vaner:rate-limit:"),
            f"Se esperaba prefijo 'vaner:' pero se obtuvo: {key}",
        )

    def test_key_no_expone_ip(self):
        key = self.middleware._key("192.168.1.100", "/auth/login", 60, 1000.0)
        self.assertNotIn("192.168.1.100", key)

    def test_key_no_expone_ruta(self):
        key = self.middleware._key("1.2.3.4", "/auth/forgot-password", 900, 1000.0)
        self.assertNotIn("forgot-password", key)
        self.assertNotIn("auth", key)

    def test_rule_for_path_auth_login(self):
        self.assertEqual(self.middleware._rule_for_path("/auth/login"), (8, 60))

    def test_rule_for_path_forgot_password(self):
        self.assertEqual(
            self.middleware._rule_for_path("/auth/forgot-password"), (5, 900)
        )

    def test_rule_for_path_default(self):
        self.assertEqual(self.middleware._rule_for_path("/equipos"), (300, 60))


class SecurityEventLoggerTests(unittest.TestCase):
    def test_get_client_ip_from_forwarded(self):
        from app.services.security_logger import get_client_ip

        request = MagicMock()
        request.headers = {"X-Forwarded-For": "10.0.0.1, 10.0.0.2"}
        request.client.host = "127.0.0.1"
        self.assertEqual(get_client_ip(request), "10.0.0.1")

    def test_get_client_ip_direct(self):
        from app.services.security_logger import get_client_ip

        request = MagicMock()
        request.headers = {}
        request.client.host = "192.168.1.1"
        self.assertEqual(get_client_ip(request), "192.168.1.1")

    def test_get_client_ip_none_request(self):
        from app.services.security_logger import get_client_ip

        self.assertIsNone(get_client_ip(None))


class ConfigValidationTests(unittest.TestCase):
    def test_rechaza_secret_key_corta(self):
        with self.assertRaises(ValueError):
            Settings(
                _env_file=None,
                DATABASE_URL="postgresql://u:p@localhost:5432/db",
                SECRET_KEY="corto",
                APP_ENV="production",
                CLIENT_CODE="test",
                CLIENT_NAME="Test",
                APP_DOMAIN="test.com",
                DEBUG=False,
                REFRESH_COOKIE_SECURE=True,
                FRONTEND_URL="https://test.com",
                BACKUP_DATABASE_URL="postgresql://backup:x@localhost:5432/db",
                CONFIG_ENCRYPTION_KEY="dGVzdGtleWZvcmVuY3J5cHRpb24xMjM0NTY=",
            )

    def test_rechaza_secret_key_con_cambiar(self):
        with self.assertRaises(ValueError):
            Settings(
                _env_file=None,
                DATABASE_URL="postgresql://u:p@localhost:5432/db",
                SECRET_KEY="CAMBIAR_ESTA_CLAVE_SEGURA_12345678",
                APP_ENV="production",
                CLIENT_CODE="test",
                CLIENT_NAME="Test",
                APP_DOMAIN="test.com",
                DEBUG=False,
                REFRESH_COOKIE_SECURE=True,
                FRONTEND_URL="https://test.com",
                BACKUP_DATABASE_URL="postgresql://backup:x@localhost:5432/db",
                CONFIG_ENCRYPTION_KEY="dGVzdGtleWZvcmVuY3J5cHRpb24xMjM0NTY=",
            )

    def test_rechaza_debug_en_produccion(self):
        with self.assertRaises(ValueError):
            Settings(
                _env_file=None,
                DATABASE_URL="postgresql://u:p@localhost:5432/db",
                SECRET_KEY="s" * 64,
                APP_ENV="production",
                CLIENT_CODE="test",
                CLIENT_NAME="Test",
                APP_DOMAIN="test.com",
                DEBUG=True,
                REFRESH_COOKIE_SECURE=True,
                FRONTEND_URL="https://test.com",
                BACKUP_DATABASE_URL="postgresql://backup:x@localhost:5432/db",
                CONFIG_ENCRYPTION_KEY="dGVzdGtleWZvcmVuY3J5cHRpb24xMjM0NTY=",
            )

    def test_rechaza_client_code_default_en_produccion(self):
        with self.assertRaises(ValueError):
            Settings(
                _env_file=None,
                DATABASE_URL="postgresql://u:p@localhost:5432/db",
                SECRET_KEY="s" * 64,
                APP_ENV="production",
                CLIENT_CODE="local",
                CLIENT_NAME="Test",
                APP_DOMAIN="test.com",
                DEBUG=False,
                REFRESH_COOKIE_SECURE=True,
                FRONTEND_URL="https://test.com",
                BACKUP_DATABASE_URL="postgresql://backup:x@localhost:5432/db",
                CONFIG_ENCRYPTION_KEY="dGVzdGtleWZvcmVuY3J5cHRpb24xMjM0NTY=",
            )

    def test_rechaza_frontend_sin_https_en_produccion(self):
        with self.assertRaises(ValueError):
            Settings(
                _env_file=None,
                DATABASE_URL="postgresql://u:p@localhost:5432/db",
                SECRET_KEY="s" * 64,
                APP_ENV="production",
                CLIENT_CODE="test",
                CLIENT_NAME="Test",
                APP_DOMAIN="test.com",
                DEBUG=False,
                REFRESH_COOKIE_SECURE=True,
                FRONTEND_URL="http://test.com",
                BACKUP_DATABASE_URL="postgresql://backup:x@localhost:5432/db",
                CONFIG_ENCRYPTION_KEY="dGVzdGtleWZvcmVuY3J5cHRpb24xMjM0NTY=",
            )

    def test_rechaza_access_token_excesivo_en_produccion(self):
        with self.assertRaises(ValueError):
            Settings(
                _env_file=None,
                DATABASE_URL="postgresql://u:p@localhost:5432/db",
                SECRET_KEY="s" * 64,
                APP_ENV="production",
                CLIENT_CODE="test",
                CLIENT_NAME="Test",
                APP_DOMAIN="test.com",
                DEBUG=False,
                REFRESH_COOKIE_SECURE=True,
                FRONTEND_URL="https://test.com",
                ACCESS_TOKEN_EXPIRE_MINUTES=120,
                BACKUP_DATABASE_URL="postgresql://backup:x@localhost:5432/db",
                CONFIG_ENCRYPTION_KEY="dGVzdGtleWZvcmVuY3J5cHRpb24xMjM0NTY=",
            )

    def test_rechaza_domain_localhost_en_produccion(self):
        with self.assertRaises(ValueError):
            Settings(
                _env_file=None,
                DATABASE_URL="postgresql://u:p@localhost:5432/db",
                SECRET_KEY="s" * 64,
                APP_ENV="production",
                CLIENT_CODE="test",
                CLIENT_NAME="Test",
                APP_DOMAIN="localhost",
                DEBUG=False,
                REFRESH_COOKIE_SECURE=True,
                FRONTEND_URL="https://test.com",
                BACKUP_DATABASE_URL="postgresql://backup:x@localhost:5432/db",
                CONFIG_ENCRYPTION_KEY="dGVzdGtleWZvcmVuY3J5cHRpb24xMjM0NTY=",
            )

    def test_dev_acepta_configuracion_relajada(self):
        settings = Settings(
            _env_file=None,
            DATABASE_URL="postgresql://u:p@localhost:5432/db",
            SECRET_KEY="dev-secret-key-12345",
            APP_ENV="development",
        )
        self.assertEqual(settings.APP_ENV, "development")


class AuditProEventoModelTests(unittest.TestCase):
    def test_tabla_correcta(self):
        from app.models.auditoria_pro import AuditoriaProEvento

        self.assertEqual(AuditoriaProEvento.__tablename__, "auditoria_pro_eventos")

    def test_campos_requeridos(self):
        from app.models.auditoria_pro import AuditoriaProEvento

        required_fields = ["modulo", "accion", "severidad", "permitido"]
        for field in required_fields:
            self.assertIn(
                field, [c.name for c in AuditoriaProEvento.__table__.columns]
            )


class SecurityEventModelTests(unittest.TestCase):
    def test_tabla_correcta(self):
        from app.models.security_event import SecurityEvent

        self.assertEqual(SecurityEvent.__tablename__, "seguridad_eventos")

    def test_campos_basicos(self):
        from app.models.security_event import SecurityEvent

        required_fields = ["evento", "permitido", "creado_en"]
        for field in required_fields:
            self.assertIn(
                field, [c.name for c in SecurityEvent.__table__.columns]
            )


class SecurityEventServiceTests(unittest.TestCase):
    def test_registrar_evento_seguridad_no_rompe(self):
        from app.services.security_logger import registrar_evento_seguridad

        db_mock = MagicMock()
        db_mock.add = MagicMock()
        db_mock.commit = MagicMock(side_effect=Exception("DB error"))
        db_mock.rollback = MagicMock()

        registrar_evento_seguridad(
            db_mock,
            request=None,
            usuario_email="test@example.com",
            evento="LOGIN_FALLIDO",
            modulo="AUTH",
        )
        db_mock.rollback.assert_called_once()

    def test_registrar_evento_seguridad_exito(self):
        from app.services.security_logger import registrar_evento_seguridad

        db_mock = MagicMock()

        registrar_evento_seguridad(
            db_mock,
            request=None,
            usuario_email="test@example.com",
            evento="LOGIN_OK",
            modulo="AUTH",
            permitido=True,
        )
        db_mock.add.assert_called_once()
        db_mock.commit.assert_called_once()


class AuthRoleRequirementTests(unittest.TestCase):
    def test_require_roles_crea_dependencia(self):
        from app.core.auth_dependencies import require_roles

        dep = require_roles("ADMIN", "COORDINADOR")
        self.assertTrue(callable(dep))

    def test_require_roles_rechaza_rol_no_listado(self):
        from fastapi import HTTPException
        from app.core.auth_dependencies import require_roles

        dep = require_roles("ADMIN")
        mock_user = MagicMock()
        mock_user.rol = "TECNICO"

        with self.assertRaises(HTTPException) as ctx:
            dep(mock_user)
        self.assertEqual(ctx.exception.status_code, 403)

    def test_require_roles_acepta_rol_listado(self):
        from app.core.auth_dependencies import require_roles

        dep = require_roles("ADMIN", "COORDINADOR")
        mock_user = MagicMock()
        mock_user.rol = "ADMIN"

        result = dep(mock_user)
        self.assertEqual(result, mock_user)


class TokenJWTCrossValidationTests(unittest.TestCase):
    def test_access_token_no_valida_como_refresh(self):
        payload = {"sub": "user-123", "email": "test@test.com"}
        token = create_access_token(payload)
        decoded = decode_token(token)
        self.assertEqual(decoded["type"], "access")
        self.assertNotEqual(decoded["type"], "refresh")

    def test_refresh_token_no_valida_como_access(self):
        payload = {"sub": "user-123"}
        token, jti, _ = create_refresh_token(payload)
        decoded = decode_token(token)
        self.assertEqual(decoded["type"], "refresh")
        self.assertNotEqual(decoded["type"], "access")


if __name__ == "__main__":
    unittest.main()
