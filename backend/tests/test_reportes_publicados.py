import unittest
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.routers.reportes_publicados import (
    _autorizar_empresa,
    _estilos_reporte,
    _ordenar_evidencias,
    _tabla_firmas,
)


class ReportesPublicadosTests(unittest.TestCase):
    def test_evidencias_se_ordenan_por_etapa_y_conservan_cronologia(self):
        evidencias = [
            SimpleNamespace(tipo="DURANTE", descripcion="Durante 1"),
            SimpleNamespace(tipo="SOPORTE", descripcion="Soporte 1"),
            SimpleNamespace(tipo="ANTES", descripcion="Antes 1"),
            SimpleNamespace(tipo="DESPUES", descripcion="Después 1"),
            SimpleNamespace(tipo="DURANTE", descripcion="Durante 2"),
            SimpleNamespace(tipo="ANTES", descripcion="Antes 2"),
        ]

        ordenadas = _ordenar_evidencias(evidencias)

        self.assertEqual(
            [item.tipo for item in ordenadas],
            ["ANTES", "ANTES", "DURANTE", "DURANTE", "DESPUES", "SOPORTE"],
        )
        self.assertEqual(
            [item.descripcion for item in ordenadas if item.tipo == "DURANTE"],
            ["Durante 1", "Durante 2"],
        )

    def test_informe_muestra_solo_firmas_cliente_y_gerencia(self):
        tabla = _tabla_firmas(
            None,
            None,
            ["Cliente ACME", "Coordinadora VANER"],
            _estilos_reporte("#1E3A8A"),
        )

        self.assertEqual(len(tabla._cellvalues[0]), 2)
        textos = [
            elemento.getPlainText()
            for celda in tabla._cellvalues[0]
            for elemento in celda
            if hasattr(elemento, "getPlainText")
        ]
        self.assertIn("Cliente / Usuario", textos)
        self.assertIn("Gerente / Coordinador VANER ASSET", textos)
        self.assertNotIn("Tecnico responsable", textos)

    def test_director_solo_descarga_de_su_empresa(self):
        empresa_id = uuid4()
        director = SimpleNamespace(rol="EMPRESA", empresa_id=empresa_id)
        _autorizar_empresa(director, empresa_id, escritura=False)

        with self.assertRaises(HTTPException):
            _autorizar_empresa(director, uuid4(), escritura=False)
        with self.assertRaises(HTTPException):
            _autorizar_empresa(director, empresa_id, escritura=True)

    def test_coordinador_escribe_solo_en_su_tenant(self):
        empresa_id = uuid4()
        coordinador = SimpleNamespace(rol="COORDINADOR", empresa_id=empresa_id)
        _autorizar_empresa(coordinador, empresa_id, escritura=True)
        with self.assertRaises(HTTPException):
            _autorizar_empresa(coordinador, uuid4(), escritura=True)

    def test_admin_tiene_acceso_global(self):
        _autorizar_empresa(SimpleNamespace(rol="ADMIN", empresa_id=None), uuid4(), escritura=True)


if __name__ == "__main__":
    unittest.main()
