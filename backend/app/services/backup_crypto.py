import os
import struct
from base64 import urlsafe_b64decode
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings


MAGIC = b"SGABKP1"
NONCE_SIZE = 12
CHUNK_SIZE = 1024 * 1024
MAX_ENCRYPTED_CHUNK = CHUNK_SIZE + 16


def backup_encryption_enabled() -> bool:
    return bool(settings.CONFIG_ENCRYPTION_KEY)


def encrypt_backup_file(source: Path, destination: Path) -> Path:
    cipher = AESGCM(_key())
    temporary = destination.with_suffix(destination.suffix + ".tmp")

    try:
        with source.open("rb") as input_file, temporary.open("wb") as output_file:
            output_file.write(MAGIC)
            while True:
                chunk = input_file.read(CHUNK_SIZE)
                if not chunk:
                    break
                nonce = os.urandom(NONCE_SIZE)
                encrypted = cipher.encrypt(nonce, chunk, MAGIC)
                output_file.write(nonce)
                output_file.write(struct.pack(">I", len(encrypted)))
                output_file.write(encrypted)
        temporary.replace(destination)
        return destination
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def decrypt_backup_file(source: Path, destination: Path) -> Path:
    cipher = AESGCM(_key())
    temporary = destination.with_suffix(destination.suffix + ".tmp")

    try:
        with source.open("rb") as input_file, temporary.open("wb") as output_file:
            if input_file.read(len(MAGIC)) != MAGIC:
                raise RuntimeError("El archivo no es un backup cifrado válido")

            while True:
                nonce = input_file.read(NONCE_SIZE)
                if not nonce:
                    break
                if len(nonce) != NONCE_SIZE:
                    raise RuntimeError("Backup cifrado truncado")
                length_bytes = input_file.read(4)
                if len(length_bytes) != 4:
                    raise RuntimeError("Backup cifrado truncado")
                encrypted_length = struct.unpack(">I", length_bytes)[0]
                if encrypted_length <= 16 or encrypted_length > MAX_ENCRYPTED_CHUNK:
                    raise RuntimeError("Tamaño de bloque cifrado inválido")
                encrypted = input_file.read(encrypted_length)
                if len(encrypted) != encrypted_length:
                    raise RuntimeError("Backup cifrado truncado")
                output_file.write(cipher.decrypt(nonce, encrypted, MAGIC))
        temporary.replace(destination)
        return destination
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _key() -> bytes:
    if not settings.CONFIG_ENCRYPTION_KEY:
        raise RuntimeError("CONFIG_ENCRYPTION_KEY es obligatoria para cifrar backups")
    key = urlsafe_b64decode(settings.CONFIG_ENCRYPTION_KEY.encode("ascii"))
    if len(key) != 32:
        raise RuntimeError("CONFIG_ENCRYPTION_KEY no es válida")
    return key
