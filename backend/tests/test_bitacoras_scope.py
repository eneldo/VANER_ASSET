import unittest
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.routers.bitacoras_dinamicas import autorizar_bitacora


class BitacorasScopeTests(unittest.TestCase):
    def test_director_solo_lee_bitacora_de_su_tenant(self):
        empresa_id = uuid4()
        director = SimpleNamespace(rol="EMPRESA", empresa_id=empresa_id)
        mantenimiento = SimpleNamespace(empresa_id=empresa_id)
        autorizar_bitacora(director, mantenimiento, db=None, escritura=False)
        with self.assertRaises(HTTPException):
            autorizar_bitacora(director, mantenimiento, db=None, escritura=True)
        with self.assertRaises(HTTPException):
            autorizar_bitacora(director, SimpleNamespace(empresa_id=uuid4()), db=None, escritura=False)

    def test_coordinador_respeta_tenant(self):
        empresa_id = uuid4()
        coordinador = SimpleNamespace(rol="COORDINADOR", empresa_id=empresa_id)
        autorizar_bitacora(coordinador, SimpleNamespace(empresa_id=empresa_id), db=None, escritura=True)
        with self.assertRaises(HTTPException):
            autorizar_bitacora(coordinador, SimpleNamespace(empresa_id=uuid4()), db=None, escritura=True)

    def test_admin_tiene_acceso_global(self):
        autorizar_bitacora(SimpleNamespace(rol="ADMIN"), SimpleNamespace(empresa_id=uuid4()), db=None, escritura=True)


if __name__ == "__main__":
    unittest.main()
