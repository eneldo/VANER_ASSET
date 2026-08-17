import unittest
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.routers.mantenimientos import sincronizar_tenant_desde_equipo


class MantenimientoTenantTests(unittest.TestCase):
    def test_mantenimiento_hereda_empresa_y_sede_del_equipo(self):
        empresa_id = uuid4()
        sede_id = uuid4()
        mantenimiento = SimpleNamespace(empresa_id=None, sede_id=None)
        equipo = SimpleNamespace(empresa_id=empresa_id, sede_id=sede_id)

        sincronizar_tenant_desde_equipo(mantenimiento, equipo)

        self.assertEqual(mantenimiento.empresa_id, empresa_id)
        self.assertEqual(mantenimiento.sede_id, sede_id)

    def test_equipo_sin_tenant_no_puede_generar_mantenimiento(self):
        mantenimiento = SimpleNamespace(empresa_id=None, sede_id=None)
        equipo = SimpleNamespace(empresa_id=None, sede_id=None)

        with self.assertRaises(HTTPException) as error:
            sincronizar_tenant_desde_equipo(mantenimiento, equipo)

        self.assertEqual(error.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
