import unittest
from io import BytesIO
from unittest.mock import patch

from fastapi import HTTPException
from starlette.datastructures import Headers, UploadFile

from app.config import settings
from app.services.inventory_import_security import (
    read_inventory_upload,
    validate_inventory_shape,
)


def _upload(filename: str, content: bytes, content_type: str) -> UploadFile:
    return UploadFile(
        BytesIO(content),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


class InventoryImportSecurityTests(unittest.IsolatedAsyncioTestCase):
    async def test_acepta_csv_utf8_valido(self):
        content, extension = await read_inventory_upload(
            _upload("inventario.csv", b"codigo_inventario,nombre\nEQ-1,Monitor\n", "text/csv")
        )
        self.assertEqual(extension, ".csv")
        self.assertIn(b"EQ-1", content)

    async def test_rechaza_extension_no_permitida(self):
        with self.assertRaises(HTTPException) as context:
            await read_inventory_upload(
                _upload("inventario.xls", b"contenido", "application/octet-stream")
            )
        self.assertEqual(context.exception.status_code, 400)

    async def test_rechaza_csv_con_datos_binarios(self):
        with self.assertRaises(HTTPException):
            await read_inventory_upload(
                _upload("inventario.csv", b"codigo\x00nombre", "text/csv")
            )

    def test_limita_numero_de_filas(self):
        with patch.object(settings, "MAX_INVENTORY_IMPORT_ROWS", 2):
            with self.assertRaises(HTTPException):
                validate_inventory_shape(3, 10)


if __name__ == "__main__":
    unittest.main()
