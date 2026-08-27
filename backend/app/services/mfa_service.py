# =========================================================
# MFA — Multi-Factor Authentication (TOTP)
# Archivo: app/services/mfa_service.py
#
# Implementa MFA basado en TOTP (Time-based One-Time Password)
# Compatible con Google Authenticator, Authy, etc.
# =========================================================

import secrets
import hashlib
import hmac
import time
import base64
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models.usuario import Usuario


# Base32 alphabet for TOTP secrets
BASE32_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def generate_mfa_secret(length: int = 32) -> str:
    """Genera un secreto TOTP seguro en base32."""
    bytes_secret = secrets.token_bytes(length)
    return base64.b32encode(bytes_secret).decode("utf-8").rstrip("=")


def generate_mfa_uri(secret: str, email: str, issuer: str = "VANER ASSET") -> str:
    """Genera URI otpauth:// para escanear con authenticator app."""
    import urllib.parse
    encoded_issuer = urllib.parse.quote(issuer)
    encoded_email = urllib.parse.quote(email)
    return f"otpauth://totp/{encoded_issuer}:{encoded_email}?secret={secret}&issuer={encoded_issuer}&digits=6&period=30"


def _dynamic_truncation(hash_bytes: bytes) -> int:
    """Dynamic truncation according to RFC 4226."""
    offset = hash_bytes[-1] & 0x0F
    code = (
        ((hash_bytes[offset] & 0x7F) << 24)
        | ((hash_bytes[offset + 1] & 0xFF) << 16)
        | ((hash_bytes[offset + 2] & 0xFF) << 8)
        | (hash_bytes[offset + 3] & 0xFF)
    )
    return code % 1_000_000


def generate_totp_code(secret: str, time_step: int = 30, digits: int = 6) -> str:
    """Genera un código TOTP para el time step actual."""
    # Decode base32 secret (remove padding)
    padded_secret = secret + "=" * ((8 - len(secret) % 8) % 8)
    secret_bytes = base64.b32decode(padded_secret)

    # Calculate time counter
    counter = int(time.time()) // time_step

    # HMAC-SHA1
    counter_bytes = counter.to_bytes(8, byteorder="big")
    hash_obj = hmac.new(secret_bytes, counter_bytes, hashlib.sha1)
    hash_bytes = hash_obj.digest()

    # Dynamic truncation
    code = _dynamic_truncation(hash_bytes)
    return str(code).zfill(digits)


def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
    """
    Verifica un código TOTP.
    window: número de time steps a cada lado para tolerancia de tiempo.
    """
    if not code or len(code) != 6 or not code.isdigit():
        return False

    for offset in range(-window, window + 1):
        # Calculate counter with offset
        counter = (int(time.time()) // 30) + offset
        padded_secret = secret + "=" * ((8 - len(secret) % 8) % 8)
        secret_bytes = base64.b32decode(padded_secret)
        counter_bytes = counter.to_bytes(8, byteorder="big")
        hash_obj = hmac.new(secret_bytes, counter_bytes, hashlib.sha1)
        hash_bytes = hash_obj.digest()
        expected_code = str(_dynamic_truncation(hash_bytes)).zfill(6)
        if hmac.compare_digest(code, expected_code):
            return True
    return False


def generate_backup_codes(count: int = 8) -> list[str]:
    """Genera códigos de respaldo de uso único."""
    codes = []
    for _ in range(count):
        code = secrets.token_hex(4).upper()
        formatted = f"{code[:4]}-{code[4:]}"
        codes.append(formatted)
    return codes


def hash_backup_code(code: str) -> str:
    """Hashea un código de respaldo para almacenamiento seguro."""
    return hashlib.sha256(code.encode()).hexdigest()


class MFAService:
    """Servicio central para operaciones MFA."""

    def __init__(self, db: Session):
        self.db = db

    def setup_mfa(self, usuario_id: str) -> dict:
        """
        Inicializa MFA para un usuario.
        Retorna secreto, URI y códigos de respaldo.
        """
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Generate secret
        secret = generate_mfa_secret()

        # Generate backup codes
        backup_codes = generate_backup_codes()
        hashed_codes = [hash_backup_code(c) for c in backup_codes]

        # Store temporarily (not enabled yet)
        # In a real implementation, store in a separate MFA table
        # For now, we'll use a simple approach
        usuario.mfa_secret = secret
        usuario.mfa_backup_codes = ",".join(hashed_codes)
        self.db.commit()

        # Generate URI for QR code
        uri = generate_mfa_uri(secret, usuario.email or usuario.username)

        return {
            "secret": secret,
            "uri": uri,
            "backup_codes": backup_codes,
            "message": "Escanea el código QR con tu authenticator app y verifica con un código para activar MFA",
        }

    def enable_mfa(self, usuario_id: str, code: str) -> bool:
        """
        Activa MFA después de verificar un código válido.
        """
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario or not usuario.mfa_secret:
            return False

        # Verify the code
        if not verify_totp_code(usuario.mfa_secret, code):
            return False

        # Enable MFA
        usuario.mfa_enabled = True
        self.db.commit()
        return True

    def verify_mfa(self, usuario_id: str, code: str) -> bool:
        """
        Verifica un código MFA durante el login.
        """
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario or not usuario.mfa_enabled or not usuario.mfa_secret:
            return False

        # Check TOTP code
        if verify_totp_code(usuario.mfa_secret, code):
            return True

        # Check backup codes
        if usuario.mfa_backup_codes:
            hashed_input = hash_backup_code(code)
            codes = usuario.mfa_backup_codes.split(",")
            if hashed_input in codes:
                # Remove used backup code
                codes.remove(hashed_input)
                usuario.mfa_backup_codes = ",".join(codes)
                self.db.commit()
                return True

        return False

    def disable_mfa(self, usuario_id: str, code: str) -> bool:
        """
        Desactiva MFA después de verificar un código válido.
        """
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario or not usuario.mfa_enabled:
            return False

        # Verify the code
        if not verify_totp_code(usuario.mfa_secret, code):
            return False

        # Disable MFA
        usuario.mfa_enabled = False
        usuario.mfa_secret = None
        usuario.mfa_backup_codes = None
        self.db.commit()
        return True

    def get_mfa_status(self, usuario_id: str) -> dict:
        """Obtiene el estado MFA de un usuario."""
        usuario = self.db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            return {"enabled": False, "configured": False}

        return {
            "enabled": usuario.mfa_enabled or False,
            "configured": bool(usuario.mfa_secret),
            "backup_codes_remaining": len(usuario.mfa_backup_codes.split(",")) if usuario.mfa_backup_codes else 0,
        }
