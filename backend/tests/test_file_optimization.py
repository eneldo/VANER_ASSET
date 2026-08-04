import asyncio
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException, UploadFile
from PIL import Image
from starlette.datastructures import Headers

from app.services import evidencia_service, file_optimizer


def _large_jpeg() -> bytes:
    image = Image.effect_noise((2600, 1900), 85).convert("RGB")
    output = BytesIO()
    image.save(output, format="JPEG", quality=96)
    return output.getvalue()


def _upload(filename: str, content: bytes, content_type: str) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(content),
        headers=Headers({"content-type": content_type}),
    )


class FileOptimizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_jpeg = _large_jpeg()

    def test_imagen_se_reduce_y_redimensiona(self):
        result = file_optimizer.optimize_file_content(
            self.original_jpeg,
            ".jpg",
            {"compresion_imagen": True, "calidad_imagen": 80, "max_dimension_imagen": 1600},
        )

        self.assertTrue(result.optimized)
        self.assertLess(result.stored_size, result.original_size)
        with Image.open(BytesIO(result.content)) as image:
            self.assertLessEqual(max(image.size), 1600)

    def test_imagen_invalida_es_rechazada(self):
        with self.assertRaises(HTTPException) as context:
            file_optimizer.optimize_file_content(b"no-es-imagen", ".jpg", {})

        self.assertEqual(context.exception.status_code, 400)

    def test_compresion_desactivada_conserva_imagen(self):
        result = file_optimizer.optimize_file_content(
            self.original_jpeg,
            ".jpg",
            {"compresion_imagen": False},
        )

        self.assertFalse(result.optimized)
        self.assertEqual(result.content, self.original_jpeg)

    def test_pdf_invalido_es_rechazado(self):
        with self.assertRaises(HTTPException) as context:
            file_optimizer.optimize_file_content(b"archivo falso", ".pdf", {})

        self.assertEqual(context.exception.status_code, 400)

    def test_pdf_valido_se_conserva_si_qpdf_no_esta_disponible(self):
        content = b"%PDF-1.4" + bytes([10]) + b"1 0 obj<</Type/Catalog>>endobj" + bytes([10]) + b"%%EOF"
        with patch.object(file_optimizer.shutil, "which", return_value=None):
            result = file_optimizer.optimize_file_content(content, ".pdf", {})

        self.assertFalse(result.optimized)
        self.assertEqual(result.content, content)
        self.assertEqual(result.engine, "qpdf-unavailable")

    def test_guardado_usa_archivo_optimizado(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            upload = _upload("evidencia.jpg", self.original_jpeg, "image/jpeg")
            with patch.object(evidencia_service, "EVIDENCIAS_DIR", Path(temp_dir)):
                saved = asyncio.run(
                    evidencia_service.save_secure_file(
                        upload,
                        {
                            "compresion_imagen": True,
                            "calidad_imagen": 80,
                            "max_dimension_imagen": 1600,
                        },
                    )
                )

            stored_path = Path(saved["path"])
            self.assertTrue(saved["optimized"])
            self.assertLess(saved["stored_size"], saved["original_size"])
            self.assertTrue(stored_path.exists())
            self.assertEqual(stored_path.suffix, ".jpg")


if __name__ == "__main__":
    unittest.main()
