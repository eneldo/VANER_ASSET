"""
===========================================================
SERVICIO DE EVIDENCIAS
===========================================================
"""

import shutil
from fastapi import UploadFile

from app.middleware.file_security import (
    sanitize_filename,
    validate_extension,
    validate_mime,
    validate_size,
    generate_secure_filename
)

from app.utils.secure_files import build_secure_path


async def save_secure_file(file: UploadFile):

    # =======================================================
    # VALIDACIONES
    # =======================================================

    validate_extension(file.filename)

    validate_mime(file)

    await validate_size(file)

    # =======================================================
    # SANITIZAR
    # =======================================================

    clean_name = sanitize_filename(file.filename)

    secure_name = generate_secure_filename(clean_name)

    secure_path = build_secure_path(secure_name)

    # =======================================================
    # GUARDAR ARCHIVO
    # =======================================================

    with open(secure_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": secure_name,
        "path": secure_path
    }