import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import Response
from starlette.requests import Request

from app.config import settings
from app.routers import auth
from app.schemas.auth import RefreshRequest
from app.models.refresh_token import RefreshToken
from app.models.usuario import Usuario
from app.security import create_refresh_token, decode_token, hash_token


def _request_with_cookie(token: str) -> Request:
    cookie = f"{settings.REFRESH_COOKIE_NAME}={token}".encode("utf-8")
    return Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "https",
            "path": "/auth/refresh",
            "raw_path": b"/auth/refresh",
            "query_string": b"",
            "headers": [(b"cookie", cookie)],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 443),
        }
    )


class _FakeQuery:
    def __init__(self, value):
        self.value = value

    def filter(self, *_args, **_kwargs):
        return self

    def with_for_update(self):
        return self

    def first(self):
        return self.value


class _FakeSession:
    def __init__(self, refresh_session, user):
        self.refresh_session = refresh_session
        self.user = user
        self.added = []
        self.commits = 0

    def query(self, model):
        if model is RefreshToken:
            return _FakeQuery(self.refresh_session)
        if model is Usuario:
            return _FakeQuery(self.user)
        raise AssertionError(f"Modelo inesperado: {model}")

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.commits += 1


class _LoginAttemptSession:
    def __init__(self):
        self.params = None
        self.commits = 0

    def execute(self, _statement, params):
        self.params = params

    def commit(self):
        self.commits += 1


class AuthRefreshSecurityTests(unittest.TestCase):
    def test_refresh_token_tiene_tipo_y_jti_correctos(self):
        token, jti, _ = create_refresh_token({"sub": "usuario-1"})
        payload = decode_token(token)

        self.assertEqual(payload["type"], "refresh")
        self.assertEqual(payload["jti"], jti)

    def test_refresh_token_se_lee_desde_cookie_httponly(self):
        response = Response()

        with (
            patch.object(settings, "REFRESH_COOKIE_SECURE", True),
            patch.object(settings, "REFRESH_COOKIE_PATH", "/api/auth"),
        ):
            auth._set_refresh_cookie(response, "token-seguro")

        header = response.headers["set-cookie"]
        self.assertIn("HttpOnly", header)
        self.assertIn("Secure", header)
        self.assertIn("Path=/api/auth", header)
        self.assertNotIn("token-seguro", response.body.decode("utf-8"))

    def test_body_tiene_prioridad_sobre_cookie_legacy(self):
        request = _request_with_cookie("cookie-token")
        data = RefreshRequest(refresh_token="body-token")

        self.assertEqual(auth._refresh_token_from_request(data, request), "body-token")

    def test_refresh_rota_y_revoca_la_sesion_anterior(self):
        token, jti, expires_at = create_refresh_token({"sub": "usuario-1"})
        old_session = SimpleNamespace(
            token_hash=hash_token(token),
            jti=jti,
            expires_at=expires_at,
            revoked_at=None,
            replaced_by_jti=None,
        )
        user = SimpleNamespace(
            id="usuario-1",
            email="usuario@example.com",
            username="usuario",
            nombre_completo="Usuario Prueba",
            rol="ADMIN",
            empresa_id=None,
            activo=True,
        )
        db = _FakeSession(old_session, user)
        response = Response()

        result = auth.refresh_token(
            RefreshRequest(),
            _request_with_cookie(token),
            response,
            db,
        )

        self.assertIsNotNone(old_session.revoked_at)
        self.assertIsNotNone(old_session.replaced_by_jti)
        self.assertEqual(db.commits, 1)
        self.assertEqual(len(db.added), 1)
        self.assertEqual(decode_token(result["access_token"])["type"], "access")
        self.assertNotIn("refresh_token", {key for key, value in result.items() if value is not None})
        self.assertIn("HttpOnly", response.headers["set-cookie"])

    def test_router_expone_logout(self):
        paths = {route.path for route in auth.router.routes}
        self.assertIn("/auth/logout", paths)

    def test_intento_login_genera_uuid_explicito(self):
        db = _LoginAttemptSession()

        auth._registrar_intento_login(
            db,
            request=_request_with_cookie("token"),
            username="ADMIN",
            exitoso=True,
            motivo="LOGIN_OK",
        )

        self.assertIsNotNone(db.params["id"])
        self.assertEqual(db.params["username"], "admin")
        self.assertEqual(db.commits, 1)


if __name__ == "__main__":
    unittest.main()
