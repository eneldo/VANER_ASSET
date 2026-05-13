"""
===========================================================
VALIDADOR EXTRA MIME
===========================================================
"""

import mimetypes


def detect_mime(filename: str):

    mime, _ = mimetypes.guess_type(filename)

    return mime