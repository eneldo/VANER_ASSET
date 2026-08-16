import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import HTTPException

from app.routers.categorias import (
    actualizar_categoria,
    crear_categoria,
    eliminar_categoria,
)
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate


class CategoriasCrudTests(unittest.TestCase):
    def test_crea_categoria_y_genera_codigo_desde_nombre(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        categoria = crear_categoria(
            CategoriaCreate(
                nombre='Equipos biomédicos',
                descripcion='Equipos de atención clínica',
            ),
            db,
            SimpleNamespace(rol='ADMIN'),
        )

        self.assertEqual(categoria.code, 'EQUIPOS_BIOMEDICOS')
        self.assertEqual(categoria.nombre, 'Equipos biomédicos')
        self.assertTrue(categoria.activo)
        db.add.assert_called_once_with(categoria)
        db.commit.assert_called_once_with()

    def test_actualiza_nombre_codigo_descripcion_y_estado(self):
        categoria_id = uuid4()
        categoria = SimpleNamespace(
            id=categoria_id,
            code='BOMBAS',
            nombre='Bombas',
            descripcion=None,
            activo=True,
        )
        db = MagicMock()
        categoria_query = MagicMock()
        duplicada_query = MagicMock()
        db.query.side_effect = [categoria_query, duplicada_query]
        categoria_query.filter.return_value.first.return_value = categoria
        duplicada_query.filter.return_value = duplicada_query
        duplicada_query.first.return_value = None

        resultado = actualizar_categoria(
            categoria_id,
            CategoriaUpdate(
                code='bombas hidraulicas',
                nombre='Bombas hidráulicas',
                descripcion='Sistemas de bombeo',
                activo=False,
            ),
            db,
            SimpleNamespace(rol='ADMIN'),
        )

        self.assertIs(resultado, categoria)
        self.assertEqual(categoria.code, 'BOMBAS_HIDRAULICAS')
        self.assertEqual(categoria.nombre, 'Bombas hidráulicas')
        self.assertEqual(categoria.descripcion, 'Sistemas de bombeo')
        self.assertFalse(categoria.activo)
        db.commit.assert_called_once_with()

    def test_elimina_categoria_sin_equipos(self):
        categoria_id = uuid4()
        categoria = SimpleNamespace(id=categoria_id, nombre='Sin uso')
        db = MagicMock()
        categoria_query = MagicMock()
        equipo_query = MagicMock()
        db.query.side_effect = [categoria_query, equipo_query]
        categoria_query.filter.return_value.first.return_value = categoria
        equipo_query.filter.return_value.first.return_value = None

        resultado = eliminar_categoria(
            categoria_id,
            db,
            SimpleNamespace(rol='ADMIN'),
        )

        db.delete.assert_called_once_with(categoria)
        db.commit.assert_called_once_with()
        self.assertEqual(resultado, {'message': 'Categoria eliminada correctamente'})

    def test_no_elimina_categoria_con_equipos(self):
        categoria_id = uuid4()
        categoria = SimpleNamespace(id=categoria_id, nombre='En uso')
        db = MagicMock()
        categoria_query = MagicMock()
        equipo_query = MagicMock()
        db.query.side_effect = [categoria_query, equipo_query]
        categoria_query.filter.return_value.first.return_value = categoria
        equipo_query.filter.return_value.first.return_value = (uuid4(),)

        with self.assertRaises(HTTPException) as context:
            eliminar_categoria(
                categoria_id,
                db,
                SimpleNamespace(rol='ADMIN'),
            )

        self.assertEqual(context.exception.status_code, 409)
        self.assertIn('equipos asociados', context.exception.detail)
        db.delete.assert_not_called()


if __name__ == '__main__':
    unittest.main()
