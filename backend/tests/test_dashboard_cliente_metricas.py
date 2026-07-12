import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace

from app.routers.cliente import clasificar_estado_dashboard, porcentaje_cumplimiento_preventivo


class DashboardClienteMetricasTests(unittest.TestCase):
    def test_clasificacion_respeta_estado_y_retraso(self):
        ahora = datetime(2026, 7, 11, 12, 0)
        self.assertEqual(clasificar_estado_dashboard(SimpleNamespace(estado="FINALIZADO"), ahora), "COMPLETADO")
        self.assertEqual(clasificar_estado_dashboard(SimpleNamespace(estado="EN_PROCESO"), ahora), "EN_PROCESO")
        self.assertEqual(
            clasificar_estado_dashboard(SimpleNamespace(estado="PROGRAMADO", fecha_programada=ahora - timedelta(days=1)), ahora),
            "RETRASADO",
        )
        self.assertEqual(
            clasificar_estado_dashboard(SimpleNamespace(estado="PROGRAMADO", fecha_programada=ahora + timedelta(days=1)), ahora),
            "PENDIENTE",
        )

    def test_cumplimiento_preventivo_mensual(self):
        inicio = datetime(2026, 7, 1)
        fin = datetime(2026, 8, 1)
        mantenimientos = [
            SimpleNamespace(tipo="PREVENTIVO", estado="FINALIZADO", fecha_programada=datetime(2026, 7, 5)),
            SimpleNamespace(tipo="PREVENTIVO", estado="PROGRAMADO", fecha_programada=datetime(2026, 7, 12)),
            SimpleNamespace(tipo="CORRECTIVO", estado="FINALIZADO", fecha_programada=datetime(2026, 7, 8)),
        ]
        self.assertEqual(porcentaje_cumplimiento_preventivo(mantenimientos, inicio, fin), 50.0)

    def test_sin_plan_preventivo_el_cumplimiento_es_total(self):
        self.assertEqual(
            porcentaje_cumplimiento_preventivo([], datetime(2026, 7, 1), datetime(2026, 8, 1)),
            100.0,
        )


if __name__ == "__main__":
    unittest.main()
