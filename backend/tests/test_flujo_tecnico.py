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
        formato = SimpleNamespace(firma_usuario="data:image/png;base64,firma", firma_operario=None)
        mantenimiento = SimpleNamespace(
            estado_inicial="Equipo con filtros sucios",
            acciones_realizadas="Limpieza y ajuste",
            resultado_final="Equipo operativo",
        )
        self.assertEqual(requisitos_finalizacion(evidencias, formato, mantenimiento), [])

    def test_ot_incompleta_reporta_cada_requisito(self):
        faltantes = requisitos_finalizacion([], None, SimpleNamespace())
        self.assertIn("foto inicial", faltantes)
        self.assertIn("foto del proceso", faltantes)
        self.assertIn("foto final", faltantes)
        self.assertIn("acciones realizadas", faltantes)
        self.assertIn("firma digital del cliente o técnico", faltantes)

    def test_firma_del_tecnico_es_valida(self):
        evidencias = [SimpleNamespace(tipo=t) for t in ("ANTES", "DURANTE", "DESPUES")]
        formato = SimpleNamespace(firma_usuario=None, firma_operario="data:image/png;base64,firma")
        mantenimiento = SimpleNamespace(
            estado_inicial="inicial", acciones_realizadas="acciones", resultado_final="final"
        )
        self.assertEqual(requisitos_finalizacion(evidencias, formato, mantenimiento), [])


if __name__ == "__main__":
    unittest.main()
