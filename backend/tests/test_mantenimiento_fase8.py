import unittest
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.schemas.mantenimiento import (
    MantenimientoBase,
    MantenimientoCreate,
    MantenimientoUpdate,
    MantenimientoOut,
)
from app.routers.mantenimientos import mantenimiento_dict, TRANSICIONES_VALIDAS
from app.services.mantenimiento_estado_service import aplicar_reapertura


class MantenimientoFase8SchemaTests(unittest.TestCase):
    def test_create_acepta_campos_fase8(self):
        schema = MantenimientoCreate(
            equipo_id=str(uuid4()),
            tipo="CORRECTIVO",
            prioridad="ALTA",
            falla_incidencia="Falla en compresor",
            diagnostico="Compresor dañado",
            trabajo_realizado="Reemplazo de compresor",
            costo_mano_obra=Decimal("150000"),
            costo_repuestos=Decimal("300000"),
            costo_total=Decimal("450000"),
            solucion="Compresor reemplazado y funcionando",
        )
        self.assertEqual(schema.prioridad, "ALTA")
        self.assertEqual(schema.falla_incidencia, "Falla en compresor")
        self.assertEqual(schema.costo_total, Decimal("450000"))

    def test_update_acepta_campos_fase8(self):
        schema = MantenimientoUpdate(
            diagnostico="Motor sobrecalentado",
            cerrado=True,
            responsable_id=str(uuid4()),
        )
        self.assertTrue(schema.cerrado)
        self.assertIsNotNone(schema.responsable_id)

    def test_base_default_prioridad_media(self):
        schema = MantenimientoBase(equipo_id=str(uuid4()), tipo="PREVENTIVO")
        self.assertEqual(schema.prioridad, "MEDIA")
        self.assertFalse(schema.cerrado)

    def test_out_incluye_campos_fase8(self):
        data = {
            "id": str(uuid4()),
            "equipo_id": str(uuid4()),
            "tipo": "CORRECTIVO",
            "estado": "PROGRAMADO",
            "prioridad": "CRITICA",
            "falla_incidencia": "Falla",
            "diagnostico": "Diag",
            "trabajo_realizado": "Trabajo",
            "costo_mano_obra": Decimal("100"),
            "costo_repuestos": Decimal("200"),
            "costo_total": Decimal("300"),
            "solucion": "Solucion",
            "cerrado": True,
        }
        schema = MantenimientoOut(**data)
        self.assertEqual(schema.prioridad, "CRITICA")
        self.assertTrue(schema.cerrado)
        self.assertEqual(schema.costo_total, Decimal("300"))


class MantenimientoFase8ReaperturaTests(unittest.TestCase):
    def test_reapertura_resetea_cerrado_y_fecha_cierre(self):
        mantenimiento = SimpleNamespace(
            estado="FINALIZADO",
            fecha_inicio=datetime(2026, 8, 20, 8, 0),
            fecha_pausa=None,
            fecha_finalizacion=datetime(2026, 8, 20, 12, 0),
            fecha_fin=datetime(2026, 8, 20, 12, 0),
            cerrado=True,
            fecha_cierre=datetime(2026, 8, 20, 12, 0),
            acciones_realizadas="Trabajo completado",
            resultado_final="OK",
            observaciones="Sin novedad",
            actualizado_en=None,
            updated_at=None,
        )

        estado_anterior = aplicar_reapertura(mantenimiento)

        self.assertEqual(estado_anterior, "FINALIZADO")
        self.assertEqual(mantenimiento.estado, "EN_PROCESO")
        self.assertFalse(mantenimiento.cerrado)
        self.assertIsNone(mantenimiento.fecha_cierre)

    def test_reapertura_conserva_datos_operativos(self):
        mantenimiento = SimpleNamespace(
            estado="FINALIZADO",
            fecha_inicio=datetime(2026, 8, 20, 8, 0),
            fecha_pausa=None,
            fecha_finalizacion=datetime(2026, 8, 20, 12, 0),
            fecha_fin=datetime(2026, 8, 20, 12, 0),
            cerrado=True,
            fecha_cierre=datetime(2026, 8, 20, 12, 0),
            acciones_realizadas="Trabajo completado",
            resultado_final="OK",
            observaciones="Sin novedad",
            actualizado_en=None,
            updated_at=None,
        )

        aplicar_reapertura(mantenimiento)

        self.assertEqual(mantenimiento.acciones_realizadas, "Trabajo completado")
        self.assertEqual(mantenimiento.resultado_final, "OK")


class MantenimientoFase8DictTests(unittest.TestCase):
    def test_dict_incluye_campos_fase8(self):
        mantenimiento = SimpleNamespace(
            id=uuid4(),
            equipo_id=uuid4(),
            tipo="CORRECTIVO",
            descripcion="Test",
            prioridad="ALTA",
            fecha_programada=None,
            fecha_inicio_programada=None,
            fecha_fin_programada=None,
            estado="PROGRAMADO",
            tecnico_id=None,
            responsable_id=None,
            fecha_asignacion=None,
            fecha_inicio=None,
            fecha_pausa=None,
            fecha_finalizacion=None,
            observaciones=None,
            estado_inicial=None,
            estado_inicial_equipo=None,
            acciones_realizadas=None,
            resultado_final=None,
            falla_incidencia="Falla reportada",
            diagnostico="Diagnóstico técnico",
            trabajo_realizado="Trabajo realizado",
            repuestos=None,
            latitud=None,
            longitud=None,
            observacion_estado=None,
            motivo_anulacion=None,
            costo=Decimal("1000"),
            costo_mano_obra=Decimal("500"),
            costo_repuestos=Decimal("300"),
            costo_total=Decimal("800"),
            evidencia_fotos=None,
            evidencia_documentos=None,
            solucion="Solución aplicada",
            cerrado=False,
            fecha_cierre=None,
            tipo_movimiento=None,
            activo_afectado_id=None,
            activo_afectado_tipo=None,
            activo=True,
            empresa_id=None,
            sede_id=None,
            equipo=None,
            tecnico=None,
            empresa=None,
            sede=None,
            creado_en=datetime.now(),
            actualizado_en=datetime.now(),
        )

        db = SimpleNamespace(
            query=lambda *a: SimpleNamespace(
                filter=lambda *a: SimpleNamespace(
                    first=lambda: None,
                    all=lambda: [],
                    delete=lambda *a, **kw: None,
                    get=lambda *a: None,
                ),
                order_by=lambda *a: SimpleNamespace(all=lambda: []),
            ),
            refresh=lambda *a, **kw: None,
        )

        result = mantenimiento_dict(mantenimiento, db)

        self.assertEqual(result["prioridad"], "ALTA")
        self.assertEqual(result["falla_incidencia"], "Falla reportada")
        self.assertEqual(result["diagnostico"], "Diagnóstico técnico")
        self.assertEqual(result["trabajo_realizado"], "Trabajo realizado")
        self.assertEqual(result["costo_mano_obra"], Decimal("500"))
        self.assertEqual(result["costo_repuestos"], Decimal("300"))
        self.assertEqual(result["costo_total"], Decimal("800"))
        self.assertEqual(result["solucion"], "Solución aplicada")
        self.assertFalse(result["cerrado"])
        self.assertIsNone(result["fecha_cierre"])


class MantenimientoFase8TransicionesTests(unittest.TestCase):
    def test_finalizado_marca_cerrado(self):
        self.assertIn("FINALIZADO", TRANSICIONES_VALIDAS.get("EN_PROCESO", []))

    def test_reapertura_desde_finalizado(self):
        self.assertIn("EN_PROCESO", TRANSICIONES_VALIDAS.get("FINALIZADO", []))

    def test_campos_modelo_coherent_con_migracion(self):
        from app.models.mantenimiento import Mantenimiento

        columnas_fase8 = [
            "prioridad", "falla_incidencia", "diagnostico", "trabajo_realizado",
            "repuestos", "costo_mano_obra", "costo_repuestos", "costo_total",
            "evidencia_fotos", "evidencia_documentos", "solucion", "cerrado",
            "fecha_cierre", "responsable_id", "tipo_movimiento",
            "activo_afectado_id", "activo_afectado_tipo",
        ]
        for col in columnas_fase8:
            self.assertTrue(
                hasattr(Mantenimiento, col),
                f"Modelo Mantenimiento no tiene columna '{col}'",
            )


if __name__ == "__main__":
    unittest.main()
