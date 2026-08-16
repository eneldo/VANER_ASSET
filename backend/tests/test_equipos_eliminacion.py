import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import HTTPException

from app.routers.equipos import eliminar_equipo


class EquiposEliminacionTests(unittest.TestCase):
    def test_elimina_equipo_nuevo_y_su_hoja_de_vida(self):
        equipo_id = uuid4()
        equipo = SimpleNamespace(id=equipo_id, nombre="Equipo nuevo")
        db = MagicMock()
        equipo_query = MagicMock()
        mantenimiento_query = MagicMock()
        hoja_query = MagicMock()
        db.query.side_effect = [equipo_query, mantenimiento_query, hoja_query]
        equipo_query.filter.return_value.first.return_value = equipo
        mantenimiento_query.filter.return_value.first.return_value = None

        resultado = eliminar_equipo(equipo_id, db)

        hoja_query.filter.return_value.delete.assert_called_once_with(
            synchronize_session=False
        )
        db.delete.assert_called_once_with(equipo)
        db.commit.assert_called_once_with()
        self.assertEqual(resultado, {"message": "Equipo eliminado correctamente"})

    def test_no_elimina_equipo_con_mantenimientos(self):
        equipo_id = uuid4()
        equipo = SimpleNamespace(id=equipo_id, nombre="Equipo en uso")
        db = MagicMock()
        equipo_query = MagicMock()
        mantenimiento_query = MagicMock()
        db.query.side_effect = [equipo_query, mantenimiento_query]
        equipo_query.filter.return_value.first.return_value = equipo
        mantenimiento_query.filter.return_value.first.return_value = (uuid4(),)

        with self.assertRaises(HTTPException) as context:
            eliminar_equipo(equipo_id, db)

        self.assertEqual(context.exception.status_code, 409)
        self.assertIn("mantenimientos asociados", context.exception.detail)
        db.delete.assert_not_called()
        db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
