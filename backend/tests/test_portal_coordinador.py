import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.routers.coordinador import MantenimientoCreate, MantenimientoUpdate, router
from app.routers.mantenimientos import normalizar_fecha_programada
from app.models.usuario import Usuario
from app.services.coordinador_empresas import aplicar_empresa_activa, ids_empresas_autorizadas


class PortalCoordinadorTests(unittest.TestCase):
    def test_migracion_otorga_solo_dml_al_rol_web(self):
        migration = (
            Path(__file__).resolve().parents[1]
            / "alembic"
            / "versions"
            / "j60f8b310001_coordinador_multiempresa.py"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.usuario_empresas TO sga_app",
            migration,
        )
        self.assertNotIn("GRANT CREATE", migration)
        self.assertNotIn("BYPASSRLS", migration)

    def test_rutas_operativas_requeridas_estan_registradas(self):
        paths = {route.path for route in router.routes}

        self.assertIn("/coordinador/equipos/exportar", paths)
        self.assertIn("/coordinador/equipos/{equipo_id}/hoja-vida", paths)
        self.assertIn("/coordinador/mantenimientos", paths)
        self.assertIn("/coordinador/empresas-autorizadas", paths)

    def test_exportacion_coordinador_requiere_autenticacion(self):
        response = TestClient(app).get("/coordinador/equipos/exportar")

        self.assertEqual(response.status_code, 401)

    def test_schemas_coordinador_aceptan_bitacora_profesional(self):
        fecha_inicio = datetime(2026, 8, 17, 8, 30)
        fecha_fin = datetime(2026, 8, 17, 10, 45)
        payload = MantenimientoCreate(
            equipo_id="11111111-1111-1111-1111-111111111111",
            tipo="PREVENTIVO",
            fecha_inicio_programada=fecha_inicio,
            fecha_fin_programada=fecha_fin,
            estado_inicial_equipo="Equipo operativo con ruido",
            acciones_realizadas="Limpieza y ajuste",
            resultado_final="Operacion normal",
            latitud="5.3489",
            longitud="-72.4057",
        )

        self.assertEqual(payload.fecha_inicio_programada, fecha_inicio)
        self.assertEqual(payload.fecha_fin_programada, fecha_fin)
        self.assertEqual(payload.estado_inicial_equipo, "Equipo operativo con ruido")
        self.assertEqual(MantenimientoUpdate(latitud="5.3").latitud, "5.3")

    def test_fecha_programada_conserva_hora(self):
        fecha = datetime(2026, 8, 17, 14, 25)

        self.assertEqual(normalizar_fecha_programada(fecha), fecha)
        self.assertEqual(
            normalizar_fecha_programada("2026-08-17T14:25:00"),
            fecha,
        )

    def test_empresa_activa_autorizada_cambia_contexto_rls(self):
        empresa_principal = uuid4()
        empresa_secundaria = uuid4()
        usuario = Usuario(
            id=uuid4(),
            nombre_completo="Coordinador multiempresa",
            username="coord.multi",
            email="coord.multi@example.com",
            password_hash="hash",
            rol="COORDINADOR",
            empresa_id=empresa_principal,
            activo=True,
        )
        db = MagicMock()
        db.execute.return_value.scalars.return_value = [empresa_principal, empresa_secundaria]

        with patch("app.services.coordinador_empresas.establecer_contexto_empresa") as contexto:
            aplicar_empresa_activa(db, usuario, str(empresa_secundaria))

        self.assertEqual(usuario.empresa_id, empresa_secundaria)
        self.assertEqual(usuario.empresa_id_principal, empresa_principal)
        contexto.assert_called_once_with(db, empresa_secundaria)

    def test_empresa_activa_no_autorizada_es_rechazada(self):
        empresa_principal = uuid4()
        usuario = Usuario(
            id=uuid4(),
            nombre_completo="Coordinador restringido",
            username="coord.restringido",
            email="coord.restringido@example.com",
            password_hash="hash",
            rol="COORDINADOR",
            empresa_id=empresa_principal,
            activo=True,
        )
        db = MagicMock()
        db.execute.return_value.scalars.return_value = [empresa_principal]

        with self.assertRaises(HTTPException) as contexto:
            aplicar_empresa_activa(db, usuario, str(uuid4()))

        self.assertEqual(contexto.exception.status_code, 403)

    def test_empresa_principal_siempre_es_la_predeterminada(self):
        empresa_principal = uuid4()
        empresa_secundaria = uuid4()
        usuario = Usuario(id=uuid4(), rol="COORDINADOR", empresa_id=empresa_principal)
        db = MagicMock()
        db.execute.return_value.scalars.return_value = [empresa_secundaria, empresa_principal]

        resultado = ids_empresas_autorizadas(db, usuario)

        self.assertEqual(resultado, [empresa_principal, empresa_secundaria])

    def test_esquema_anterior_permite_ingreso_con_empresa_principal(self):
        empresa_principal = uuid4()
        usuario = Usuario(id=uuid4(), rol="COORDINADOR", empresa_id=empresa_principal)
        db = MagicMock()

        with patch(
            "app.services.coordinador_empresas.tabla_usuario_empresas_disponible",
            return_value=False,
        ):
            resultado = ids_empresas_autorizadas(db, usuario)

        self.assertEqual(resultado, [empresa_principal])
        db.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
