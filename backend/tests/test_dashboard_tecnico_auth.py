import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import HTTPException

from app.routers.dashboard_tecnico import construir_card_mantenimiento, validar_identidad_tecnico


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

    def test_card_incluye_identificacion_y_ubicacion_del_equipo(self):
        equipo_id = uuid4()
        mantenimiento = SimpleNamespace(
            id=uuid4(),
            equipo_id=equipo_id,
            tipo='PREVENTIVO',
            estado='ASIGNADO',
            fecha_programada=None,
        )
        equipo = SimpleNamespace(
            id=equipo_id,
            empresa_id=uuid4(),
            sede_id=uuid4(),
            nombre='Bomba principal',
            codigo_id='EQ-001',
            inventario='INV-450',
            marca='Marca',
            modelo='Modelo',
            serie='SER-9',
            ubicacion='Cuarto de bombas',
            estado='OPERATIVO',
            criticidad='ALTA',
        )
        empresa = SimpleNamespace(nombre='Empresa cliente', logo_url=None)
        sede = SimpleNamespace(nombre='Sede norte')
        db = MagicMock()
        equipo_query = MagicMock()
        empresa_query = MagicMock()
        sede_query = MagicMock()
        db.query.side_effect = [equipo_query, empresa_query, sede_query]
        equipo_query.filter.return_value.first.return_value = equipo
        empresa_query.filter.return_value.first.return_value = empresa
        sede_query.filter.return_value.first.return_value = sede

        card = construir_card_mantenimiento(mantenimiento, db)

        self.assertEqual(card['equipo']['inventario'], 'INV-450')
        self.assertEqual(card['equipo']['codigo_id'], 'EQ-001')
        self.assertEqual(card['equipo']['ubicacion'], 'Cuarto de bombas')
        self.assertEqual(card['equipo']['serie'], 'SER-9')
        self.assertEqual(card['empresa']['nombre'], 'Empresa cliente')
        self.assertEqual(card['sede']['nombre'], 'Sede norte')


if __name__ == "__main__":
    unittest.main()
