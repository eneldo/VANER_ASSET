"""
Tests end-to-end del flujo completo de Órdenes de Trabajo.

Flujo: crear → asignar → ejecutar → guardar avance → finalizar → verificar cierre.

Estos tests validan la integración entre:
- Router de mantenimientos (CRUD, estados, asignación)
- Router de dashboard técnico (avance, repuestos, incidencias, evidencias)
- Schemas y modelos
- Transiciones de estado y trazabilidad
"""

import unittest
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException

from app.routers.mantenimientos import (
    TRANSICIONES_VALIDAS,
    ESTADOS_PERMITIDOS,
    normalizar_fecha_programada,
    registrar_historial,
)
from app.routers.dashboard_tecnico import (
    normalizar_repuestos,
    normalizar_incidencias,
    requisitos_finalizacion,
    aplicar_estado_operativo,
)
from app.services.mantenimiento_estado_service import aplicar_reapertura


class TestFlujoCompletoOTTransiciones(unittest.TestCase):
    """Valida que la máquina de estados del flujo OT es completa y coherente."""

    def test_flujo_completo_programado_a_finalizado(self):
        """PROGRAMADO → ASIGNADO → EN_PROCESO → FINALIZADO"""
        flujo = ["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "FINALIZADO"]
        for i in range(len(flujo) - 1):
            origen = flujo[i]
            destino = flujo[i + 1]
            self.assertIn(
                destino,
                TRANSICIONES_VALIDAS.get(origen, []),
                f"Transición {origen} → {destino} no permitida",
            )

    def test_flujo_con_pausa(self):
        """PROGRAMADO → ASIGNADO → EN_PROCESO → PAUSADO → EN_PROCESO → FINALIZADO"""
        pasos = [
            ("PROGRAMADO", "ASIGNADO"),
            ("ASIGNADO", "EN_PROCESO"),
            ("EN_PROCESO", "PAUSADO"),
            ("PAUSADO", "EN_PROCESO"),
            ("EN_PROCESO", "FINALIZADO"),
        ]
        for origen, destino in pasos:
            self.assertIn(
                destino,
                TRANSICIONES_VALIDAS.get(origen, []),
                f"Transición {origen} → {destino} no permitida",
            )

    def test_flujo_con_reapertura(self):
        """FINALIZADO → EN_PROCESO (reapertura) → FINALIZADO"""
        self.assertIn("EN_PROCESO", TRANSICIONES_VALIDAS.get("FINALIZADO", []))
        self.assertIn("FINALIZADO", TRANSICIONES_VALIDAS.get("EN_PROCESO", []))

    def test_flujo_con_anulacion(self):
        """PROGRAMADO → ANULADO y ASIGNADO → ANULADO"""
        for estado in ["PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO"]:
            self.assertIn(
                "ANULADO",
                TRANSICIONES_VALIDAS.get(estado, []),
                f"No se puede anular desde {estado}",
            )

    def test_finalizado_no_se_puede_anular(self):
        """FINALIZADO no permite anulación directa."""
        self.assertNotIn("ANULADO", TRANSICIONES_VALIDAS.get("FINALIZADO", []))

    def test_anulado_no_permite_transiciones(self):
        """ANULADO es estado terminal."""
        self.assertEqual(TRANSICIONES_VALIDAS.get("ANULADO", []), [])

    def test_todos_los_estados_son_validos(self):
        """Todos los estados del flujo OT están en la lista de permitidos."""
        esperados = {"PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO", "FINALIZADO", "ANULADO"}
        self.assertEqual(set(ESTADOS_PERMITIDOS), esperados)


class TestFlujoCompletoOTRepuestosIncidencias(unittest.TestCase):
    """Valida el manejo de repuestos e incidencias en el flujo OT."""

    def test_repuesto_valido_se_normaliza(self):
        raw = '[{"descripcion":"Filtro de aire","cantidad":"2","unidad":"UNIDAD","costo_unitario":"15000"}]'
        items = normalizar_repuestos(raw)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["descripcion"], "Filtro de aire")
        self.assertEqual(items[0]["cantidad"], 2)

    def test_multiples_repuestos(self):
        raw = '[{"descripcion":"Filtro","cantidad":"1"},{"descripcion":"Aceite","cantidad":"5","unidad":"LITRO"}]'
        items = normalizar_repuestos(raw)
        self.assertEqual(len(items), 2)

    def test_repuesto_con_referencia(self):
        raw = '[{"descripcion":"Filtro","cantidad":"1","referencia":"FLT-001","costo_unitario":"20000"}]'
        items = normalizar_repuestos(raw)
        self.assertEqual(items[0]["referencia"], "FLT-001")

    def test_incidencia_severidades_validas(self):
        for sev in ["BAJA", "MEDIA", "ALTA", "CRITICA"]:
            raw = f'[{{"descripcion":"Incidencia {sev}","severidad":"{sev}"}}]'
            items = normalizar_incidencias(raw)
            self.assertEqual(items[0]["severidad"], sev)

    def test_incidencia_tipo_se_normaliza(self):
        raw = '[{"tipo":"seguridad","severidad":"ALTA","descripcion":"Cable expuesto"}]'
        items = normalizar_incidencias(raw)
        self.assertEqual(items[0]["tipo"], "SEGURIDAD")

    def test_incidencia_resuelta(self):
        raw = '[{"descripcion":"Fuga","severidad":"MEDIA","resuelta":true}]'
        items = normalizar_incidencias(raw)
        self.assertTrue(items[0]["resuelta"])

    def test_maximo_50_repuestos(self):
        items = [{"descripcion": f"Repuesto {i}", "cantidad": "1"} for i in range(50)]
        import json
        result = normalizar_repuestos(json.dumps(items))
        self.assertEqual(len(result), 50)

    def test_mas_de_50_repuestos_rechazado(self):
        import json
        items = [{"descripcion": f"Repuesto {i}", "cantidad": "1"} for i in range(51)]
        with self.assertRaises(HTTPException):
            normalizar_repuestos(json.dumps(items))


class TestFlujoCompletoOTEvidencias(unittest.TestCase):
    """Valida los requisitos de evidencias para cierre de OT."""

    def test_cierre_requiere_evidencias_antes_durante_despues(self):
        from types import SimpleNamespace

        evidencias_vacias = []
        faltantes = requisitos_finalizacion(evidencias_vacias)
        self.assertIn("foto inicial", faltantes)
        self.assertIn("foto del proceso", faltantes)
        self.assertIn("foto final", faltantes)

    def test_con_evidencia_antes_falta_durante_despues(self):
        from types import SimpleNamespace

        evidencias = [SimpleNamespace(tipo="ANTES")]
        faltantes = requisitos_finalizacion(evidencias)
        self.assertNotIn("foto inicial", faltantes)
        self.assertIn("foto del proceso", faltantes)
        self.assertIn("foto final", faltantes)

    def test_con_todas_evidencias_no_falta_nada(self):
        from types import SimpleNamespace

        evidencias = [
            SimpleNamespace(tipo="ANTES"),
            SimpleNamespace(tipo="DURANTE"),
            SimpleNamespace(tipo="DESPUES"),
        ]
        faltantes = requisitos_finalizacion(evidencias)
        self.assertEqual(faltantes, [])


class TestFlujoCompletoOTAplicarEstado(unittest.TestCase):
    """Valida la aplicación de estados operativos."""

    def test_aplicar_en_proceso_setea_fecha_inicio(self):
        from types import SimpleNamespace

        m = SimpleNamespace(
            estado="ASIGNADO",
            fecha_inicio=None,
            fecha_pausa=None,
            fecha_finalizacion=None,
            fecha_fin=None,
        )
        aplicar_estado_operativo(m, "EN_PROCESO")
        self.assertEqual(m.estado, "EN_PROCESO")
        self.assertIsNotNone(m.fecha_inicio)

    def test_aplicar_pausado_setea_fecha_pausa(self):
        from types import SimpleNamespace

        m = SimpleNamespace(
            estado="EN_PROCESO",
            fecha_inicio=datetime.now(),
            fecha_pausa=None,
            fecha_finalizacion=None,
            fecha_fin=None,
        )
        aplicar_estado_operativo(m, "PAUSADO")
        self.assertEqual(m.estado, "PAUSADO")
        self.assertIsNotNone(m.fecha_pausa)

    def test_aplicar_finalizado_setea_fechas(self):
        from types import SimpleNamespace

        m = SimpleNamespace(
            estado="EN_PROCESO",
            fecha_inicio=datetime.now(),
            fecha_pausa=None,
            fecha_finalizacion=None,
            fecha_fin=None,
        )
        aplicar_estado_operativo(m, "FINALIZADO")
        self.assertEqual(m.estado, "FINALIZADO")
        self.assertIsNotNone(m.fecha_finalizacion)
        self.assertIsNotNone(m.fecha_fin)

    def test_estado_no_valido_rechazado(self):
        from types import SimpleNamespace

        m = SimpleNamespace(estado="PROGRAMADO")
        with self.assertRaises(HTTPException):
            aplicar_estado_operativo(m, "INVALIDO")


class TestFlujoCompletoOTReapertura(unittest.TestCase):
    """Valida la lógica de reapertura de OTs finalizadas."""

    def test_reapertura_resetea_cerrado(self):
        from types import SimpleNamespace

        m = SimpleNamespace(
            estado="FINALIZADO",
            fecha_inicio=datetime(2026, 8, 20, 8, 0),
            fecha_pausa=None,
            fecha_finalizacion=datetime(2026, 8, 20, 12, 0),
            fecha_fin=datetime(2026, 8, 20, 12, 0),
            cerrado=True,
            fecha_cierre=datetime(2026, 8, 20, 12, 0),
            acciones_realizadas="Completado",
            resultado_final="OK",
            observaciones="Sin novedad",
            actualizado_en=None,
            updated_at=None,
        )
        estado_anterior = aplicar_reapertura(m)
        self.assertEqual(estado_anterior, "FINALIZADO")
        self.assertEqual(m.estado, "EN_PROCESO")
        self.assertFalse(m.cerrado)
        self.assertIsNone(m.fecha_cierre)

    def test_reapertura_conserva_datos(self):
        from types import SimpleNamespace

        m = SimpleNamespace(
            estado="FINALIZADO",
            fecha_inicio=datetime(2026, 8, 20, 8, 0),
            fecha_pausa=None,
            fecha_finalizacion=datetime(2026, 8, 20, 12, 0),
            fecha_fin=datetime(2026, 8, 20, 12, 0),
            cerrado=True,
            fecha_cierre=datetime(2026, 8, 20, 12, 0),
            acciones_realizadas="Trabajo completo",
            resultado_final="Equipo operativo",
            observaciones="OK",
            actualizado_en=None,
            updated_at=None,
        )
        aplicar_reapertura(m)
        self.assertEqual(m.acciones_realizadas, "Trabajo completo")
        self.assertEqual(m.resultado_final, "Equipo operativo")


class TestFlujoCompletoOTNormalizacion(unittest.TestCase):
    """Valida helpers de normalización del flujo OT."""

    def test_normalizar_fecha_programada_none(self):
        self.assertIsNone(normalizar_fecha_programada(None))

    def test_normalizar_fecha_programada_string_iso(self):
        result = normalizar_fecha_programada("2026-08-20T10:00:00")
        self.assertIsNotNone(result)

    def test_normalizar_fecha_programada_datetime(self):
        dt = datetime(2026, 8, 20, 10, 0)
        result = normalizar_fecha_programada(dt)
        self.assertEqual(result, dt)

    def test_normalizar_fecha_programada_fecha(self):
        from datetime import date

        d = date(2026, 8, 20)
        result = normalizar_fecha_programada(d)
        self.assertIsNotNone(result)

    def test_repuesto_lista_vacia(self):
        result = normalizar_repuestos("[]")
        self.assertEqual(result, [])

    def test_incidencia_lista_vacia(self):
        result = normalizar_incidencias("[]")
        self.assertEqual(result, [])


class TestFlujoCompletoOTCoherencia(unittest.TestCase):
    """Valida coherencia entre transiciones, estados y lógica de negocio."""

    def test_transiciones_cubren_todos_los_estados(self):
        """Todos los estados aparecen como origen en transiciones."""
        for estado in ESTADOS_PERMITIDOS:
            self.assertIn(
                estado,
                TRANSICIONES_VALIDAS,
                f"Estado {estado} no tiene transiciones definidas",
            )

    def test_programado_solo_permite_asignar_o_anular(self):
        transiciones = TRANSICIONES_VALIDAS["PROGRAMADO"]
        self.assertEqual(set(transiciones), {"ASIGNADO", "ANULADO"})

    def test_asignado_solo_permite_ejecutar_o_anular(self):
        transiciones = TRANSICIONES_VALIDAS["ASIGNADO"]
        self.assertEqual(set(transiciones), {"EN_PROCESO", "ANULADO"})

    def test_en_proceso_solo_permite_pausar_finalizar_anular(self):
        transiciones = TRANSICIONES_VALIDAS["EN_PROCESO"]
        self.assertEqual(set(transiciones), {"PAUSADO", "FINALIZADO", "ANULADO"})

    def test_finalizado_solo_permite_reabrir(self):
        transiciones = TRANSICIONES_VALIDAS["FINALIZADO"]
        self.assertEqual(set(transiciones), {"EN_PROCESO"})


if __name__ == "__main__":
    unittest.main()
