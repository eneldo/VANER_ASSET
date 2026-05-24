"""
===========================================================
SERVICIO DE EVIDENCIAS PRO
Archivo: backend/app/services/evidencia_service.py
===========================================================
"""

from pathlib import Path
import shutil
import os

from fastapi import UploadFile

from app.middleware.file_security import (
    sanitize_filename,
    validate_extension,
    validate_mime,
    validate_size,
    generate_secure_filename,
)

# ===========================================================
# RUTA PRODUCCIÓN DOCKER
# ===========================================================

DOCKER_UPLOADS = Path("/app/uploads")
DOCKER_EVIDENCIAS = DOCKER_UPLOADS / "evidencias"

# Crear carpetas automáticamente
DOCKER_EVIDENCIAS.mkdir(parents=True, exist_ok=True)

UPLOADS_DIR = DOCKER_UPLOADS
EVIDENCIAS_DIR = DOCKER_EVIDENCIAS


# ===========================================================
# GUARDAR ARCHIVO
# ===========================================================

async def save_secure_file(file: UploadFile) -> dict:
    """
    Guarda archivo de forma segura.
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


# ===========================================================
# OBTENER RUTA SEGURA
# ===========================================================

def get_evidencia_path(filename_or_url: str) -> Path:

    safe_name = Path(filename_or_url or "").name

    if not safe_name:
        raise ValueError("Nombre inválido")

    return EVIDENCIAS_DIR / safe_name