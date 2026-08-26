import unittest
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError

from app.automation.jobs.vida_util_job import (
    obtener_fecha_base_vida_util,
    procesar_vida_util,
)
from app.routers.equipos import (
    _agregar_historial,
    _guardar_movimiento,
    validar_equipo_movible,
    validar_responsable,
)
from app.schemas.equipo import EquipoCreate, EquipoHistorialItem


class EquipoFase7Tests(unittest.TestCase):
    def test_vida_util_debe_ser_positiva(self):
        with self.assertRaises(ValidationError):
            EquipoCreate(
                empresa_id=uuid4(),
                sede_id=uuid4(),
                categoria_id=uuid4(),
                nombre="Equipo",
                vida_util_meses=0,
            )

    def test_historial_reasigna_lista_y_acepta_actor_automatico(self):
        historial = [{"campo": "ubicacion"}]
        equipo = SimpleNamespace(historial_cambios=historial)
        _agregar_historial(equipo, "estado", "OPERATIVO", "FUERA_DE_SERVICIO", "system")
        self.assertIsNot(equipo.historial_cambios, historial)
        self.assertEqual(equipo.historial_cambios[-1]["usuario_id"], "system")
        item = EquipoHistorialItem(**equipo.historial_cambios[-1])
        self.assertEqual(item.usuario_id, "system")

    def test_bloquea_movimientos_en_baja_o_inactivo(self):
        for equipo in (
            SimpleNamespace(activo=True, estado="BAJA"),
            SimpleNamespace(activo=False, estado="OPERATIVO"),
        ):
            with self.assertRaises(HTTPException) as context:
                validar_equipo_movible(equipo)
            self.assertEqual(context.exception.status_code, 409)

    def test_valida_responsable_activo_y_empresa(self):
        empresa_id = uuid4()
        responsable = SimpleNamespace(activo=True, empresa_id=empresa_id)
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = responsable
        self.assertIs(validar_responsable(db, uuid4(), empresa_id), responsable)
        responsable.activo = False
        with self.assertRaises(HTTPException) as context:
            validar_responsable(db, uuid4(), empresa_id)
        self.assertEqual(context.exception.status_code, 404)
        responsable.activo = True
        responsable.empresa_id = uuid4()
        with self.assertRaises(HTTPException) as context:
            validar_responsable(db, uuid4(), empresa_id)
        self.assertEqual(context.exception.status_code, 400)

    def test_guardar_movimiento_hace_rollback_si_falla_commit(self):
        db = MagicMock()
        db.commit.side_effect = RuntimeError("db")
        with self.assertRaises(RuntimeError):
            _guardar_movimiento(db, SimpleNamespace())
        db.rollback.assert_called_once_with()

    def test_fecha_base_prioriza_instalacion_compra_y_creacion(self):
        equipo = SimpleNamespace(created_at=datetime(2020, 3, 1))
        hoja = SimpleNamespace(fecha_instalacion=date(2020, 1, 1), fecha_compra=date(2019, 1, 1))
        self.assertEqual(obtener_fecha_base_vida_util(equipo, hoja), datetime(2020, 1, 1))
        hoja.fecha_instalacion = None
        self.assertEqual(obtener_fecha_base_vida_util(equipo, hoja), datetime(2019, 1, 1))
        hoja.fecha_compra = None
        self.assertEqual(obtener_fecha_base_vida_util(equipo, hoja), equipo.created_at)

    def test_vida_util_vence_sin_baja_y_es_idempotente(self):
        equipo = SimpleNamespace(
            created_at=datetime(2020, 1, 1),
            vida_util_meses=12,
            estado="OPERATIVO",
            activo=True,
            historial_cambios=None,
        )
        hoja = SimpleNamespace(fecha_instalacion=date(2020, 2, 1), fecha_compra=None)
        ahora = datetime(2021, 2, 1)
        self.assertEqual(procesar_vida_util([(equipo, hoja)], ahora), 1)
        self.assertEqual(equipo.estado, "FUERA_DE_SERVICIO")
        self.assertTrue(equipo.activo)
        self.assertEqual(len(equipo.historial_cambios), 1)
        self.assertEqual(procesar_vida_util([(equipo, hoja)], ahora), 0)
        self.assertEqual(len(equipo.historial_cambios), 1)

    def test_vida_util_no_vence_antes_del_limite(self):
        equipo = SimpleNamespace(
            created_at=datetime(2024, 1, 1),
            vida_util_meses=12,
            estado="OPERATIVO",
            activo=True,
            historial_cambios=None,
        )
        self.assertEqual(procesar_vida_util([(equipo, None)], datetime(2024, 12, 31)), 0)
        self.assertEqual(equipo.estado, "OPERATIVO")


if __name__ == "__main__":
    unittest.main()
