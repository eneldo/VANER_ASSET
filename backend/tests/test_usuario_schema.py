import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from pydantic import ValidationError

from app.routers.usuarios import crear_usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut


class UsuarioSchemaTests(unittest.TestCase):
    def test_respuesta_tolera_correo_legacy_almacenado(self):
        usuario = UsuarioOut.model_validate(
            {
                "id": uuid4(),
                "nombre_completo": "Administrador local",
                "username": "admin",
                "email": "admin@localhost.local",
                "rol": "ADMIN",
                "empresa_id": None,
                "activo": True,
                "created_at": datetime.now(),
                "updated_at": None,
            }
        )

        self.assertEqual(usuario.email, "admin@localhost.local")

    def test_creacion_sigue_rechazando_correo_invalido(self):
        with self.assertRaises(ValidationError):
            UsuarioCreate.model_validate(
                {
                    "nombre_completo": "Usuario nuevo",
                    "username": "usuario",
                    "email": "correo-invalido",
                    "password": "password-seguro-123",
                    "rol": "TECNICO",
                    "empresa_id": uuid4(),
                }
            )

    def test_creacion_tecnico_conserva_empresa_seleccionada(self):
        empresa_id = uuid4()
        empresa_query = MagicMock()
        usuario_query = MagicMock()
        empresa_query.filter.return_value.first.return_value = SimpleNamespace(id=empresa_id)
        usuario_query.filter.return_value.first.return_value = None
        db = MagicMock()
        db.query.side_effect = [empresa_query, usuario_query]
        data = UsuarioCreate.model_validate(
            {
                "nombre_completo": "Técnico de prueba",
                "username": "tecnico.prueba",
                "email": "tecnico.prueba@sgaholding.co",
                "password": "password-seguro-123",
                "rol": "TECNICO",
                "empresa_id": empresa_id,
            }
        )

        usuario = crear_usuario(data, db)

        self.assertEqual(usuario.empresa_id, empresa_id)
        self.assertEqual(usuario.rol, "TECNICO")
        db.add.assert_called_once_with(usuario)
        db.commit.assert_called_once()

    def test_schema_coordinador_acepta_varias_empresas(self):
        empresa_principal = uuid4()
        empresa_secundaria = uuid4()

        data = UsuarioCreate.model_validate(
            {
                "nombre_completo": "Coordinador multiempresa",
                "username": "coord.multi",
                "email": "coord.multi@example.com",
                "password": "password-seguro-123",
                "rol": "COORDINADOR",
                "empresa_id": empresa_principal,
                "empresa_ids": [empresa_principal, empresa_secundaria],
            }
        )

        self.assertEqual(data.empresa_id, empresa_principal)
        self.assertEqual(data.empresa_ids, [empresa_principal, empresa_secundaria])


if __name__ == "__main__":
    unittest.main()
