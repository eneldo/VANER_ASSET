import time
import unittest
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from fastapi import HTTPException

from app.routers.evidencias import (
    autorizar_mantenimiento,
    crear_url_firmada,
    validar_firma_archivo,
)


class EvidenciasPrivadasTests(unittest.TestCase):
    def test_url_firmada_valida_y_expira(self):
        evidencia_id = uuid4()
        url = crear_url_firmada(evidencia_id, "foto.jpg", ttl_segundos=60)
        query = parse_qs(urlparse(url).query)
        validar_firma_archivo(evidencia_id, int(query["expires"][0]), query["signature"][0])
        self.assertEqual(query["filename"][0], "foto.jpg")

        with self.assertRaises(HTTPException) as error:
            validar_firma_archivo(evidencia_id, int(time.time()) - 1, "firma")
        self.assertEqual(error.exception.status_code, 401)

    def test_firma_alterada_es_rechazada(self):
        with self.assertRaises(HTTPException) as error:
            validar_firma_archivo(uuid4(), int(time.time()) + 60, "incorrecta")
        self.assertEqual(error.exception.status_code, 403)

    def test_director_solo_lee_evidencias_de_su_tenant(self):
        empresa_id = uuid4()
        usuario = SimpleNamespace(rol="EMPRESA", empresa_id=empresa_id)
        mantenimiento = SimpleNamespace(empresa_id=empresa_id)
        autorizar_mantenimiento(usuario, mantenimiento, db=None, escritura=False)

        with self.assertRaises(HTTPException):
            autorizar_mantenimiento(usuario, mantenimiento, db=None, escritura=True)
        with self.assertRaises(HTTPException):
            autorizar_mantenimiento(
                usuario, SimpleNamespace(empresa_id=uuid4()), db=None, escritura=False
            )


if __name__ == "__main__":
    unittest.main()
