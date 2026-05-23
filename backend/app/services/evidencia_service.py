"""
===========================================================
SERVICIO DE EVIDENCIAS PRO
Archivo: backend/app/services/evidencia_service.py

FIX:
- Mantener mismo nombre UUID
- Guardar correctamente en uploads/evidencias
===========================================================
"""

import os
import shutil
from fastapi import UploadFile

from app.middleware.file_security import (
    sanitize_filename,
    validate_extension,
    validate_mime,
    validate_size,
    generate_secure_filename
)

# ===========================================================
# RUTA SEGURA
# ===========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads",
    "evidencias"
)

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ===========================================================
# GUARDAR ARCHIVO
# ===========================================================

async def save_secure_file(file: UploadFile):

    # =======================================================
    # VALIDACIONES
    # =======================================================

    validate_extension(file.filename)

    validate_mime(file)

    await validate_size(file)

    # =======================================================
    # LIMPIAR NOMBRE
    # =======================================================

    clean_name = sanitize_filename(file.filename)

    secure_name = generate_secure_filename(clean_name)

    # =======================================================
    # RUTA FINAL
    # =======================================================

    secure_path = os.path.join(
        UPLOAD_DIR,
        secure_name
    )

    # =======================================================
    # GUARDAR
    # =======================================================

    with open(secure_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": secure_name,
        "path": secure_path
    }