"""
===========================================================
SERVICIO DE EVIDENCIAS PRO
Archivo: backend/app/services/evidencia_service.py

Responsabilidad:
- Validar archivos de evidencia.
- Generar un nombre seguro único.
- Guardar físicamente el archivo en app/uploads/evidencias.
- Retornar el mismo nombre que realmente se guardó en disco.

IMPORTANTE PRODUCCIÓN:
- No usar rutas relativas frágiles.
- No generar doble nombre.
- La BD debe guardar /uploads/evidencias/<filename>.
===========================================================
"""

from pathlib import Path
import shutil

from fastapi import UploadFile

from app.middleware.file_security import (
    sanitize_filename,
    validate_extension,
    validate_mime,
    validate_size,
    generate_secure_filename,
)

# backend/app
BASE_DIR = Path(__file__).resolve().parent.parent

# backend/app/uploads/evidencias
UPLOADS_DIR = BASE_DIR / "uploads"
EVIDENCIAS_DIR = UPLOADS_DIR / "evidencias"

EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)


async def save_secure_file(file: UploadFile) -> dict:
    """
    Guarda una evidencia de forma segura y retorna el nombre final real.

    Return:
        {
            "filename": "uuid.ext",
            "path": "/app/app/uploads/evidencias/uuid.ext",
            "public_url": "/uploads/evidencias/uuid.ext"
        }
    """

    if not file or not file.filename:
        raise ValueError("Archivo no recibido")

    validate_extension(file.filename)
    validate_mime(file)
    await validate_size(file)

    clean_name = sanitize_filename(file.filename)
    secure_name = generate_secure_filename(clean_name)

    final_path = EVIDENCIAS_DIR / secure_name

    file.file.seek(0)

    with final_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": secure_name,
        "path": str(final_path),
        "public_url": f"/uploads/evidencias/{secure_name}",
    }


def get_evidencia_path(filename_or_url: str) -> Path:
    """
    Convierte un filename o archivo_url en ruta física segura.
    """

    safe_name = Path(filename_or_url or "").name

    if not safe_name:
        raise ValueError("Nombre de archivo inválido")

    return EVIDENCIAS_DIR / safe_name
