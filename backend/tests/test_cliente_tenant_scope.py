import unittest
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.routers.cliente import validar_acceso_empresa


class ClienteTenantScopeTests(unittest.TestCase):
    def test_director_solo_accede_a_su_empresa(self):
        empresa_id = uuid4()
        usuario = SimpleNamespace(rol="EMPRESA", empresa_id=empresa_id)

        validar_acceso_empresa(empresa_id, usuario)

        with self.assertRaises(HTTPException) as error:
            validar_acceso_empresa(uuid4(), usuario)
        self.assertEqual(error.exception.status_code, 403)

    def test_admin_puede_acceder_a_cualquier_empresa(self):
        usuario = SimpleNamespace(rol="ADMIN", empresa_id=None)
        validar_acceso_empresa(uuid4(), usuario)

    def test_tecnico_no_puede_acceder_al_portal_cliente(self):
        usuario = SimpleNamespace(rol="TECNICO", empresa_id=uuid4())

        with self.assertRaises(HTTPException) as error:
            validar_acceso_empresa(usuario.empresa_id, usuario)
        self.assertEqual(error.exception.status_code, 403)

    def test_coordinador_vinculado_respeta_tenant(self):
        empresa_id = uuid4()
        usuario = SimpleNamespace(rol="COORDINADOR", empresa_id=empresa_id)
        validar_acceso_empresa(empresa_id, usuario)

        with self.assertRaises(HTTPException):
            validar_acceso_empresa(uuid4(), usuario)


if __name__ == "__main__":
    unittest.main()
