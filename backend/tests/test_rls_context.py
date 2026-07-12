import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.database import establecer_contexto_tenant


class RlsContextTests(unittest.TestCase):
    def _session_no_postgres(self):
        session = MagicMock()
        session.info = {}
        session.get_bind.return_value = SimpleNamespace(
            dialect=SimpleNamespace(name="sqlite")
        )
        return session

    def test_director_fija_su_tenant_sin_privilegio_global(self):
        session = self._session_no_postgres()
        usuario = SimpleNamespace(rol="EMPRESA", empresa_id="tenant-a")

        establecer_contexto_tenant(session, usuario)

        self.assertEqual(session.info["rls_tenant_id"], "tenant-a")
        self.assertFalse(session.info["rls_platform_admin"])
        session.execute.assert_not_called()

    def test_admin_activa_privilegio_global(self):
        session = self._session_no_postgres()
        usuario = SimpleNamespace(rol="ADMIN", empresa_id=None)

        establecer_contexto_tenant(session, usuario)

        self.assertEqual(session.info["rls_tenant_id"], "")
        self.assertTrue(session.info["rls_platform_admin"])


if __name__ == "__main__":
    unittest.main()
