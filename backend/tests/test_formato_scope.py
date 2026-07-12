import unittest
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.routers.formatos_mantenimiento import _autorizar_formato


class FormatoScopeTests(unittest.TestCase):
    def test_director_solo_puede_leer_formato_de_su_empresa(self):
        empresa_id = uuid4()
        usuario = SimpleNamespace(rol="EMPRESA", empresa_id=empresa_id)
        mantenimiento = SimpleNamespace(empresa_id=empresa_id)
        _autorizar_formato(usuario, mantenimiento, db=None, escritura=False)

        with self.assertRaises(HTTPException):
            _autorizar_formato(usuario, mantenimiento, db=None, escritura=True)

    def test_director_no_puede_leer_ot_de_otro_tenant(self):
        usuario = SimpleNamespace(rol="EMPRESA", empresa_id=uuid4())
        mantenimiento = SimpleNamespace(empresa_id=uuid4())
        with self.assertRaises(HTTPException) as error:
            _autorizar_formato(usuario, mantenimiento, db=None, escritura=False)
        self.assertEqual(error.exception.status_code, 403)

    def test_admin_tiene_alcance_global(self):
        usuario = SimpleNamespace(rol="ADMIN", empresa_id=None)
        _autorizar_formato(usuario, SimpleNamespace(empresa_id=uuid4()), db=None)


if __name__ == "__main__":
    unittest.main()
