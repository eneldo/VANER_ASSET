"""
===========================================================
UTILIDADES SEGURAS DE ARCHIVOS
===========================================================
"""

import os

BASE_UPLOAD_DIR = "app/uploads/evidencias"


def ensure_upload_folder():

    if not os.path.exists(BASE_UPLOAD_DIR):
        os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)


def build_secure_path(filename: str):

    ensure_upload_folder()

    return os.path.join(BASE_UPLOAD_DIR, filename)