import unittest
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.routers.dashboard_tecnico import validar_identidad_tecnico


class DashboardTecnicoAuthTests(unittest.TestCase):
    def test_tecnico_solo_puede_usar_su_identidad(self):
        usuario_id = uuid4()
        usuario = SimpleNamespace(id=usuario_id, rol="TECNICO")
        validar_identidad_tecnico(usuario_id, usuario)

        with self.assertRaises(HTTPException) as error:
            validar_identidad_tecnico(uuid4(), usuario)
        self.assertEqual(error.exception.status_code, 403)

    def test_otro_rol_no_puede_usar_endpoint_tecnico(self):
        usuario_id = uuid4()
        usuario = SimpleNamespace(id=usuario_id, rol="EMPRESA")

        with self.assertRaises(HTTPException) as error:
            validar_identidad_tecnico(usuario_id, usuario)
        self.assertEqual(error.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
