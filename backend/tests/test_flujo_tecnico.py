import unittest
from datetime import datetime
from types import SimpleNamespace

from fastapi import HTTPException

from app.routers.dashboard_tecnico import (
    requisitos_finalizacion,
    router as dashboard_tecnico_router,
    validar_limite_evidencias_por_etapa,
)
from app.routers.mantenimientos import TRANSICIONES_VALIDAS
from app.services.mantenimiento_estado_service import (
    aplicar_reapertura,
    validar_mantenimiento_editable,
)


class FlujoTecnicoTests(unittest.TestCase):
    def test_ot_completa_no_tiene_requisitos_faltantes(self):
        evidencias = [
            SimpleNamespace(tipo="ANTES"),
            SimpleNamespace(tipo="DURANTE"),
            SimpleNamespace(tipo="DESPUES"),
        ]
        mantenimiento = SimpleNamespace(
            estado_inicial="Equipo con filtros sucios",
            acciones_realizadas="Limpieza y ajuste",
            resultado_final="Equipo operativo",
        )

        self.assertEqual(requisitos_finalizacion(evidencias, mantenimiento), [])

    def test_ot_incompleta_reporta_evidencias_faltantes(self):
        faltantes = requisitos_finalizacion([], SimpleNamespace())

        self.assertIn("foto inicial", faltantes)
        self.assertIn("foto del proceso", faltantes)
        self.assertIn("foto final", faltantes)
        self.assertNotIn("acciones realizadas", faltantes)
        self.assertNotIn("firma digital del cliente o técnico", faltantes)

    def test_ot_completa_no_requiere_firma(self):
        evidencias = [SimpleNamespace(tipo=tipo) for tipo in ("ANTES", "DURANTE", "DESPUES")]

        self.assertEqual(requisitos_finalizacion(evidencias), [])

    def test_permite_hasta_cuatro_evidencias_por_etapa(self):
        validar_limite_evidencias_por_etapa("ANTES", 3)
        validar_limite_evidencias_por_etapa("DURANTE", 3)
        validar_limite_evidencias_por_etapa("DESPUES", 3)

    def test_rechaza_una_quinta_evidencia_por_etapa(self):
        for tipo in ("ANTES", "DURANTE", "DESPUES"):
            with self.subTest(tipo=tipo):
                with self.assertRaises(HTTPException) as error:
                    validar_limite_evidencias_por_etapa(tipo, 4)

                self.assertEqual(error.exception.status_code, 409)
                self.assertIn("hasta 4 evidencias", error.exception.detail)
                self.assertIn(tipo, error.exception.detail)

    def test_soporte_no_usa_limite_por_etapa(self):
        validar_limite_evidencias_por_etapa("SOPORTE", 20)

    def test_reapertura_conserva_datos_y_limpia_cierre(self):
        fecha_inicio = datetime(2026, 8, 16, 8, 0)
        mantenimiento = SimpleNamespace(
            estado="FINALIZADO",
            fecha_inicio=fecha_inicio,
            fecha_pausa=datetime(2026, 8, 16, 9, 0),
            fecha_finalizacion=datetime(2026, 8, 16, 10, 0),
            fecha_fin=datetime(2026, 8, 16, 10, 0),
            acciones_realizadas="Limpieza y ajuste",
            resultado_final="Equipo operativo",
            observaciones="Sin novedad",
            actualizado_en=None,
            updated_at=None,
        )

        estado_anterior = aplicar_reapertura(mantenimiento)

        self.assertEqual(estado_anterior, "FINALIZADO")
        self.assertEqual(mantenimiento.estado, "EN_PROCESO")
        self.assertEqual(mantenimiento.fecha_inicio, fecha_inicio)
        self.assertIsNone(mantenimiento.fecha_pausa)
        self.assertIsNone(mantenimiento.fecha_finalizacion)
        self.assertIsNone(mantenimiento.fecha_fin)
        self.assertEqual(mantenimiento.acciones_realizadas, "Limpieza y ajuste")
        self.assertEqual(mantenimiento.resultado_final, "Equipo operativo")
        self.assertEqual(mantenimiento.observaciones, "Sin novedad")

    def test_solo_finalizados_pueden_reabrirse(self):
        mantenimiento = SimpleNamespace(estado="EN_PROCESO")

        with self.assertRaises(HTTPException) as error:
            aplicar_reapertura(mantenimiento)

        self.assertEqual(error.exception.status_code, 409)

    def test_finalizado_no_es_editable_sin_reapertura(self):
        with self.assertRaises(HTTPException) as error:
            validar_mantenimiento_editable(SimpleNamespace(estado="FINALIZADO"))

        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(error.exception.detail["codigo"], "OT_FINALIZADA")

    def test_tecnico_no_tiene_endpoint_para_reabrir(self):
        rutas = {route.path for route in dashboard_tecnico_router.routes}

        self.assertNotIn("/dashboard-tecnico/mantenimiento/{mantenimiento_id}/reabrir", rutas)

    def test_reapertura_supervisada_vuelve_a_en_proceso(self):
        self.assertEqual(TRANSICIONES_VALIDAS["FINALIZADO"], ["EN_PROCESO"])


if __name__ == "__main__":
    unittest.main()
