"""
Tests del módulo de Reportes — Fase 10.

Cubre:
- Schemas y validación de plantillas de reporte
- Helpers de reportes publicados
- Lógica de BI ejecutivo (costos, conteos)
- Exportaciones: generación Excel/PDF
- Coherencia de modelos y rutas
"""

import unittest
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.routers.plantillas_reporte import _validar_tipo, _serializar
from app.routers.bi_ejecutivo import (
    obtener_kpis,
    mantenimientos_estados,
    costos_empresa,
    tecnicos_productivos,
    equipos_criticos,
    equipos_empresa,
)
from app.routers.dashboard_tecnico import requisitos_finalizacion
from app.models.plantilla_reporte import PlantillaReporte


class PlantillaReporteSchemaTests(unittest.TestCase):
    """Valida schemas y validación de plantillas de reporte."""

    def test_tipo_ot_es_valido(self):
        self.assertEqual(_validar_tipo("OT"), "OT")

    def test_tipo_mensual_es_valido(self):
        self.assertEqual(_validar_tipo("MENSUAL"), "MENSUAL")

    def test_tipo_ambos_es_valido(self):
        self.assertEqual(_validar_tipo("AMBOS"), "AMBOS")

    def test_tipo_invalido_rechazado(self):
        with self.assertRaises(HTTPException) as ctx:
            _validar_tipo("INVALIDO")
        self.assertEqual(ctx.exception.status_code, 422)

    def test_tipo_none_usa_default(self):
        with self.assertRaises(HTTPException):
            _validar_tipo(None)

    def test_tipo_se_normaliza_a_mayusculas(self):
        self.assertEqual(_validar_tipo("ot"), "OT")
        self.assertEqual(_validar_tipo("mensual"), "MENSUAL")


class PlantillaReporteSerializarTests(unittest.TestCase):
    """Valida serialización de plantillas."""

    def test_serializar_plantilla_global(self):
        plantilla = SimpleNamespace(
            id=uuid4(),
            empresa_id=None,
            nombre="Plantilla Base",
            tipo="AMBOS",
            titulo="Reporte de Mantenimiento",
            color_primario="#1E3A8A",
            pie_pagina="Pie de prueba",
            incluir_logo=True,
            incluir_evidencias=True,
            incluir_firmas=True,
            incluir_costos=False,
            activo=True,
            created_at=datetime(2026, 8, 20),
        )
        result = _serializar(plantilla)
        self.assertIsNone(result["empresa_id"])
        self.assertEqual(result["empresa_nombre"], "Plantilla global")
        self.assertEqual(result["nombre"], "Plantilla Base")
        self.assertTrue(result["incluir_logo"])

    def test_serializar_plantilla_empresa(self):
        plantilla = SimpleNamespace(
            id=uuid4(),
            empresa_id=uuid4(),
            nombre="Plantilla Empresa",
            tipo="OT",
            titulo="OT Report",
            color_primario="#0f766e",
            pie_pagina=None,
            incluir_logo=False,
            incluir_evidencias=False,
            incluir_firmas=False,
            incluir_costos=True,
            activo=True,
            created_at=datetime(2026, 8, 20),
        )
        empresa = SimpleNamespace(nombre="Empresa Test")
        result = _serializar(plantilla, empresa)
        self.assertIsNotNone(result["empresa_id"])
        self.assertEqual(result["empresa_nombre"], "Empresa Test")
        self.assertTrue(result["incluir_costos"])
        self.assertFalse(result["incluir_logo"])


class PlantillaReporteModelTests(unittest.TestCase):
    """Valida que el modelo PlantillaReporte tiene las columnas esperadas."""

    def test_modelo_tiene_campos_requeridos(self):
        campos_esperados = [
            "id", "empresa_id", "creado_por_id", "nombre", "tipo", "titulo",
            "color_primario", "pie_pagina", "incluir_logo", "incluir_evidencias",
            "incluir_firmas", "incluir_costos", "activo", "created_at", "updated_at",
        ]
        for campo in campos_esperados:
            self.assertTrue(
                hasattr(PlantillaReporte, campo),
                f"Modelo PlantillaReporte no tiene columna '{campo}'",
            )

    def test_tabla_es_plantillas_reporte(self):
        self.assertEqual(PlantillaReporte.__tablename__, "plantillas_reporte")


class BIExecutiveKPITests(unittest.TestCase):
    """Valida la lógica de KPIs del BI ejecutivo."""

    def test_kpis_retorna_estructura_correcta(self):
        db = SimpleNamespace(
            query=lambda modelo: SimpleNamespace(
                count=lambda: 5,
            )
        )
        result = obtener_kpis(db)
        self.assertIn("total_empresas", result)
        self.assertIn("total_sedes", result)
        self.assertIn("total_equipos", result)
        self.assertIn("total_usuarios", result)
        self.assertIn("total_mantenimientos", result)

    def test_kpis_error_retorna_ceros(self):
        db = SimpleNamespace(
            query=lambda modelo: (_ for _ in ()).throw(Exception("DB error"))
        )
        result = obtener_kpis(db)
        self.assertEqual(result["total_empresas"], 0)
        self.assertEqual(result["total_mantenimientos"], 0)


class BIExecutiveCostosTests(unittest.TestCase):
    """Valida que costos_empresa retorna la estructura correcta."""

    def test_costos_empresa_estructura(self):
        db = SimpleNamespace(
            query=lambda *a: SimpleNamespace(
                outerjoin=lambda *a: SimpleNamespace(
                    group_by=lambda *a: SimpleNamespace(
                        all=lambda: [
                            ("Empresa A", Decimal("1500000")),
                            ("Empresa B", Decimal("800000")),
                        ]
                    )
                )
            )
        )
        result = costos_empresa(db)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["empresa"], "Empresa A")
        self.assertEqual(result[0]["costo_total"], 1500000.0)
        self.assertEqual(result[1]["costo"], 800000.0)


class BIExecutiveEstadosTests(unittest.TestCase):
    """Valida la estructura de mantenimientos por estado."""

    def test_mantenimientos_estados_estructura(self):
        db = SimpleNamespace(
            query=lambda *a: SimpleNamespace(
                group_by=lambda *a: SimpleNamespace(
                    all=lambda: [
                        ("PROGRAMADO", 10),
                        ("EN_PROCESO", 5),
                        ("FINALIZADO", 20),
                    ]
                )
            )
        )
        result = mantenimientos_estados(db)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["estado"], "PROGRAMADO")
        self.assertEqual(result[0]["total"], 10)


class BIExecutiveEquiposTests(unittest.TestCase):
    """Valida la estructura de equipos por empresa."""

    def test_equipos_empresa_estructura(self):
        db = SimpleNamespace(
            query=lambda *a: SimpleNamespace(
                outerjoin=lambda *a: SimpleNamespace(
                    group_by=lambda *a: SimpleNamespace(
                        all=lambda: [
                            ("Empresa A", 15),
                            ("Empresa B", 8),
                        ]
                    )
                )
            )
        )
        result = equipos_empresa(db)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["empresa"], "Empresa A")
        self.assertEqual(result[0]["equipos"], 15)


class ReportesPublicadosRequisitosTests(unittest.TestCase):
    """Valida los requisitos de evidencias para reportes."""

    def test_requisitos_finalizacion_faltan_todos(self):
        evidencias = []
        faltantes = requisitos_finalizacion(evidencias)
        self.assertEqual(len(faltantes), 3)

    def test_requisitos_finalizacion_completo(self):
        evidencias = [
            SimpleNamespace(tipo="ANTES"),
            SimpleNamespace(tipo="DURANTE"),
            SimpleNamespace(tipo="DESPUES"),
        ]
        faltantes = requisitos_finalizacion(evidencias)
        self.assertEqual(len(faltantes), 0)


class ExportacionesCoherenciaTests(unittest.TestCase):
    """Valida coherencia del módulo de exportaciones."""

    def test_router_exportaciones_existe(self):
        from app.routers import exportaciones
        self.assertTrue(hasattr(exportaciones, "router"))
        self.assertEqual(exportaciones.router.prefix, "/exportaciones")

    def test_router_reportes_existe(self):
        from app.routers import reportes
        self.assertTrue(hasattr(reportes, "router"))
        self.assertEqual(reportes.router.prefix, "/reportes")

    def test_router_reportes_publicados_existe(self):
        from app.routers import reportes_publicados
        self.assertTrue(hasattr(reportes_publicados, "router"))
        self.assertEqual(reportes_publicados.router.prefix, "/reportes-publicados")

    def test_router_plantillas_existe(self):
        from app.routers import plantillas_reporte
        self.assertTrue(hasattr(plantillas_reporte, "router"))
        self.assertEqual(plantillas_reporte.router.prefix, "/plantillas-reporte")

    def test_router_bi_ejecutivo_existe(self):
        from app.routers import bi_ejecutivo
        self.assertTrue(hasattr(bi_ejecutivo, "router"))
        self.assertEqual(bi_ejecutivo.router.prefix, "/bi-ejecutivo")


class ExportacionesExcelTests(unittest.TestCase):
    """Valida la utilidad de exportación Excel."""

    def test_crear_excel_genera_archivo(self):
        from app.utils.excel_exporter import crear_excel
        datos = [
            {"nombre": "Equipo A", "estado": "OPERATIVO", "costo": 1000},
            {"nombre": "Equipo B", "estado": "EN_MANTENIMIENTO", "costo": 2000},
        ]
        columnas = ["nombre", "estado", "costo"]
        resultado = crear_excel("test_report", "Test Report", columnas, datos)
        self.assertIsNotNone(resultado)

    def test_crear_excel_con_datos_vacios(self):
        from app.utils.excel_exporter import crear_excel
        resultado = crear_excel("test_empty", "Empty Report", ["col1", "col2"], [])
        self.assertIsNotNone(resultado)


class ExportacionesPDFTests(unittest.TestCase):
    """Valida la utilidad de exportación PDF."""

    def test_crear_pdf_genera_archivo(self):
        from app.utils.pdf_exporter import crear_pdf
        datos = [
            {"nombre": "Equipo A", "estado": "OPERATIVO"},
            {"nombre": "Equipo B", "estado": "EN_MANTENIMIENTO"},
        ]
        columnas = ["nombre", "estado"]
        resultado = crear_pdf("test_pdf", "Test PDF Report", columnas, datos)
        self.assertIsNotNone(resultado)

    def test_crear_pdf_con_datos_vacios(self):
        from app.utils.pdf_exporter import crear_pdf
        resultado = crear_pdf("test_empty_pdf", "Empty PDF", ["col1"], [])
        self.assertIsNotNone(resultado)


if __name__ == "__main__":
    unittest.main()
