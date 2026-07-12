import unittest
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.routers.solicitudes_correctivas import _tenant_usuario, PRIORIDADES, ESTADOS


class SolicitudesCorrectivasTests(unittest.TestCase):
    def test_tenant_se_deriva_del_usuario(self):
        empresa_id = uuid4()
        usuario = SimpleNamespace(empresa_id=empresa_id)
        self.assertEqual(_tenant_usuario(usuario), empresa_id)

    def test_usuario_sin_tenant_es_rechazado(self):
        with self.assertRaises(HTTPException) as error:
            _tenant_usuario(SimpleNamespace(empresa_id=None))
        self.assertEqual(error.exception.status_code, 403)

    def test_catalogos_de_estado_y_prioridad_son_cerrados(self):
        self.assertEqual(PRIORIDADES, {"ALTA", "CRITICA", "EMERGENCIA"})
        self.assertIn("NUEVA", ESTADOS)
        self.assertIn("CONVERTIDA_OT", ESTADOS)
        self.assertNotIn("FINALIZADO_ARBITRARIO", ESTADOS)


if __name__ == "__main__":
    unittest.main()
