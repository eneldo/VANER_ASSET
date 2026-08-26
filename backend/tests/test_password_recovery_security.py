import unittest
from types import SimpleNamespace
from unittest.mock import patch

from starlette.requests import Request

from app.middleware.audit_middleware import AuditMiddleware
from app.routers import password_recovery
from app.services.password_reset_service import construir_reset_url


def _request(query_string: bytes = b"") -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "https",
            "path": "/auth/reset-password/validate",
            "raw_path": b"/auth/reset-password/validate",
            "query_string": query_string,
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 443),
        }
    )


class _QueryChain:
    def __init__(self, result=None):
        self._result = result

    def order_by(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def all(self):
        return self._result or []

    def first(self):
        return self._result[0] if self._result else None


class _UserQuery:
    def __init__(self, user):
        self.user = user

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.user

    def order_by(self, *_args, **_kwargs):
        return _QueryChain([])

    def limit(self, *_args, **_kwargs):
        return _QueryChain([])

    def all(self):
        return []


class _Session:
    def __init__(self, user):
        self.user = user
        self.commits = 0

    def query(self, _model):
        return _UserQuery(self.user)

    def commit(self):
        self.commits += 1

    def add(self, _value):
        return None

    def rollback(self):
        return None


class PasswordRecoverySecurityTests(unittest.TestCase):
    def test_reset_url_usa_fragmento_y_no_query(self):
        url = construir_reset_url("token-seguro")
        self.assertIn("#token=token-seguro", url)
        self.assertNotIn("?token=", url)

    def test_validacion_solo_expone_post(self):
        routes = [
            route
            for route in password_recovery.router.routes
            if route.path == "/auth/reset-password/validate"
        ]
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].methods, {"POST"})

    def test_auditoria_no_conserva_valores_sensibles(self):
        middleware = AuditMiddleware(lambda _scope, _receive, _send: None)
        metadata = middleware._query_metadata(
            _request(b"token=secreto-plano&pagina=2")
        )
        self.assertEqual(metadata["query_parameters"], ["pagina", "token"])
        self.assertEqual(metadata["sensitive_parameters_redacted"], ["token"])
        self.assertNotIn("secreto-plano", str(metadata))

    def test_reset_revoca_sesiones_y_tokens_restantes(self):
        registro = SimpleNamespace(usuario_id="usuario-1")
        usuario = SimpleNamespace(
            id="usuario-1",
            username="usuario",
            email="usuario@example.com",
            rol="ADMIN",
            empresa_id=None,
            password_hash="anterior",
        )
        db = _Session(usuario)

        with (
            patch.object(password_recovery, "buscar_token_valido", return_value=registro),
            patch.object(password_recovery, "hash_password", return_value="nuevo-hash"),
            patch.object(password_recovery, "marcar_token_usado") as marcar,
            patch.object(password_recovery, "revocar_sesiones_usuario") as revocar,
            patch.object(password_recovery, "invalidar_tokens_recuperacion_usuario") as invalidar,
            patch.object(password_recovery, "registrar_evento_seguridad"),
        ):
            password_recovery.reset_password(
                password_recovery.ResetPasswordRequest(
                    token="t" * 40,
                    new_password="Clave-Segura-2026",
                ),
                _request(),
                db,
            )

        self.assertEqual(usuario.password_hash, "nuevo-hash")
        marcar.assert_called_once_with(db, registro, commit=False)
        revocar.assert_called_once_with(db, usuario.id)
        invalidar.assert_called_once_with(db, usuario.id)
        self.assertEqual(db.commits, 1)


if __name__ == "__main__":
    unittest.main()
