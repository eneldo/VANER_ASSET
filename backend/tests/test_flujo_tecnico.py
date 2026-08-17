import unittest
from types import SimpleNamespace

from app.routers.dashboard_tecnico import requisitos_finalizacion


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


if __name__ == "__main__":
    unittest.main()
