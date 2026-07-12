import unittest
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.routers.reportes_publicados import _autorizar_empresa


class ReportesPublicadosTests(unittest.TestCase):
    def test_director_solo_descarga_de_su_empresa(self):
        empresa_id = uuid4()
        director = SimpleNamespace(rol="EMPRESA", empresa_id=empresa_id)
        _autorizar_empresa(director, empresa_id, escritura=False)

        with self.assertRaises(HTTPException):
            _autorizar_empresa(director, uuid4(), escritura=False)
        with self.assertRaises(HTTPException):
            _autorizar_empresa(director, empresa_id, escritura=True)

    def test_coordinador_escribe_solo_en_su_tenant(self):
        empresa_id = uuid4()
        coordinador = SimpleNamespace(rol="COORDINADOR", empresa_id=empresa_id)
        _autorizar_empresa(coordinador, empresa_id, escritura=True)
        with self.assertRaises(HTTPException):
            _autorizar_empresa(coordinador, uuid4(), escritura=True)

    def test_admin_tiene_acceso_global(self):
        _autorizar_empresa(SimpleNamespace(rol="ADMIN", empresa_id=None), uuid4(), escritura=True)


if __name__ == "__main__":
    unittest.main()
